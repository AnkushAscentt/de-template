import os
import sys

from setuptools import find_namespace_packages, setup

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
modulepath = os.path.join(ROOT_DIR, "src")
if modulepath not in sys.path:
    sys.path.append(modulepath)

from src.common_utils import __version__  # noqa: E402


# Read the contents of your requirements.txt file
def read_requirements(filename):
    with open(filename, "r") as f:
        return f.readlines()


# Parse the requirements to include only package lines, ignoring --extra-index-url and
# other directives
def parse_requirements(filename):
    lines = read_requirements(filename)
    requirements = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("--"):
            requirements.append(line)
    return requirements

# setup(
#     name="tmna-{{ cookiecutter.project_slug }}",
#     version="{{ cookiecutter.version }}",
#     author="{{ cookiecutter.author_name }}",
#     author_email="{{ cookiecutter.email }}",
#     description="{{ cookiecutter.description }}",
#     packages=find_packages(),
#     install_requires=[],
# )

setup(
    name="tmna-{{ cookiecutter.project_slug }}",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    version=__version__,
    author="{{ cookiecutter.author_name }}",
    description="{{ cookiecutter.description }}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="OSI Approved :: MIT License",
    platforms=["OS Independent"],
    setup_requires=["pytest-runner", "setuptools_scm"],
    use_scm_version=True,
    include_package_data=True,
    install_requires=requirements,
)