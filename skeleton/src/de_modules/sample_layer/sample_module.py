"""
sample module
"""

import json
import logging
try:
    from common_utils.utils.hash import get_hash_str
    from common_utils.utils.io import get_input_info, is_exists, load_inputs, load_params, save_data
    from de_modules.schema import SampleModuleParams
except:
    from src.common_utils.utils.hash import get_hash_str
    from src.common_utils.utils.io import get_input_info, is_exists, load_inputs, load_params, save_data
    from src.de_modules.schema import SampleModuleParams

logger = logging.getLogger("de_modules.sample_module")


def run():
    # Parameters to process input data
    params = load_params("sample_module_params")                        # sample_module_params comes from parameters.yml
    params = {} if params is None else params
    # validate parameters
    validated_params = SampleModuleParams(**params)
    params = validated_params.model_dump()

    # Input data path
    input_catalog_entry_filenames = {"input_sample": None}             # input_sample comes from catalog.yml as it is input entry

    # Getting input info
    input_info = get_input_info(input_catalog_entry_filenames)

    # all parameters to save at the end
    overwrite = params.pop("overwrite", False)
    hash_params = dict(**params, **input_info)

    filename = get_hash_str(obj2hash=hash_params)

    # Define output catalog entries
    output_catalog_entry = "sample_module"                              # sample_module comes from catalog.yml as it is output entry

    # check if output exists
    b_exists = is_exists(catalog_entry=output_catalog_entry, suffix=filename)

    logger.info(json.dumps({"b_exists": b_exists, "overwrite": overwrite}))

    # Run processing if output doesn't exist or overwrite is True
    if (b_exists is False) or (overwrite is True):

        # load all input data sets
        inputs = load_inputs(input_catalog_entry_filenames)
        raw_model_def = inputs["input_sample"]                         # input_sample comes from catalog.yml and it will be input

        # Load require variables
        param_1 = params["param_1"]
        param_2 = params["param_2"]

        # Preprocessing
        output = ""                                                  # output



















        # Save output & params
        save_data(output, "sample_module", suffix=filename)             
        save_data(hash_params, "sample_module", suffix=f"{filename}.pkl")

        logger.info(
            json.dumps(
                {
                    "message": "Saved successfully.",
                    "output": output_catalog_entry,
                    "filename": filename,
                }
            )
        )
