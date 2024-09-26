"""
Great Expectation related functions
"""

import logging
import os
from typing import Union

import great_expectations as ge
import pandas as pd
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.exceptions.exceptions import DataContextError, InvalidDataContextKeyError
from pyspark.sql import DataFrame as sparkDataFrame

try:
    from common_utils.utils.helpers import get_root_directory
    from common_utils.utils.spark import is_running_dbx
except ModuleNotFoundError:
    from src.common_utils.utils.helpers import get_root_directory
    from src.common_utils.utils.spark import is_running_dbx

logger = logging.getLogger("utils.ge")

ge_folder = os.path.join(get_root_directory(), "great_expectations")


def run_validation(expectation_suite: str, data: Union[pd.DataFrame, sparkDataFrame]) -> None:
    """Run great expectations to do data validation

    Args:
        expectation_suite: data set name
        data: dataset to be validated
    """
    # Set store locations
    if is_running_dbx():
        runtime_environment = {"expectations_store": {}, "validations_store": {}, "local_site": {}}
    else:
        runtime_environment = None

    # Get GE context
    ge_context = ge.get_context(context_root_dir=ge_folder, runtime_environment=runtime_environment)

    try:
        _ = ge_context.get_expectation_suite(expectation_suite)
    except (DataContextError, InvalidDataContextKeyError):
        logger.info(f"No validations suite {expectation_suite} found, skipping...")
        return

    logger.info(f"Running Great Expectations validations for {expectation_suite}")

    datasource = "datasource_pandas" if isinstance(data, pd.DataFrame) else "datasource_spark"

    if datasource == "datasource_spark":
        data.persist().count()

    # Create batch request
    batch_request = RuntimeBatchRequest(
        datasource_name=datasource,
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name=expectation_suite,
        runtime_parameters={"batch_data": data},
        batch_identifiers={
            "default_identifier_name": datasource
        },  # Use datastore name as the batch ID
    )

    # Run data validate via checkpoint
    result = ge_context.run_checkpoint(
        checkpoint_name=f"{expectation_suite}_checkpoint",
        batch_request=batch_request,
        expectation_suite_name=expectation_suite,
    )

    # Build data doc
    # TODO update when ge data docs perms are updated (see TDSP)
    # ge_context.build_data_docs(site_names=[data_docs_site])

    # throw errors if data validation is failed
    if not result["success"]:
        logger.error(
            f"Failed Great Expectation for {expectation_suite}! Refer to data docs for"
            " more information"
        )

        _get_validation_err(result)

        # break pipeline if anything fails
        raise RuntimeError(
            f"Failed Great Expectation for {expectation_suite}! Refer to data docs for"
            " more information"
        )
    else:
        logger.info(f"Passed Great Expectation for {expectation_suite}")


def _get_validation_err(result: dict) -> None:
    """Log validation error per expectation

    Args:
        result: JSON formatted result output from run_checkpoint call
    Raises:
        RuntimeError: error when certain validation was not able to run
    """
    validation_results = next(iter(result["run_results"].values()))["validation_result"]["results"]

    # Iterate through each validation/expectation
    for validation in validation_results:
        if not validation["success"]:
            logger.error(
                "Failed validation:"
                f" {validation['expectation_config']['meta']['notes']['content']}"
            )
            if validation.get("exception_info"):
                if validation["exception_info"].get("raised_exception"):
                    raise RuntimeError(
                        "Unable to run Great Expectations due to exception!\n" f" {validation}"
                    )
            if validation.get("partial_unexpected_list"):
                logger.error("Failures: + \n" + validation["partial_unexpected_list"])
