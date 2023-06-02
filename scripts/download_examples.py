# %% [markdown]
#
# # Download IMC example data
#

# %% [markdown]
# This script downloads IMC example raw data, a fully trained `Ilastik` pixel classifier, the panel file used for the experiment and sample metadata (the cancer type of the patient). The IMC raw data will be stored in the `raw` folder together with the panel file. The ilastik project and the sample metadata will be stored in the root of the repository.

# %%
from pathlib import Path
from urllib import request

raw_folder = Path("../raw")
raw_folder.mkdir(exist_ok=True, parents=True)

# Raw data and panel
for example_file_name, example_file_url in [
    (
        "Patient1.zip",
        "https://zenodo.org/record/7575859/files/Patient1.zip",
    ),
    (
        "Patient2.zip",
        "https://zenodo.org/record/7575859/files/Patient2.zip",
    ),
    (
        "Patient3.zip",
        "https://zenodo.org/record/7575859/files/Patient3.zip",
    ),
    (
        "Patient4.zip",
        "https://zenodo.org/record/7575859/files/Patient4.zip",
    ),
    (
        "panel.csv",
        "https://zenodo.org/record/7575859/files/panel.csv",
    )
]:
    example_file = raw_folder / example_file_name
    if not example_file.exists():
        request.urlretrieve(example_file_url, example_file)
        
# Ilastik project
ilastik_project = Path("..") / "IMCWorkflow.ilp"
if not ilastik_project.exists():
    request.urlretrieve("https://zenodo.org/record/7997296/files/IMCWorkflow.ilp", ilastik_project)
    
# Sample metadata
sample_metadata = Path("..") / "sample_metadata.csv"
if not sample_metadata.exists():
    request.urlretrieve("https://zenodo.org/record/7575859/files/sample_metadata.csv", sample_metadata)

# %%
# !conda list

# %%
