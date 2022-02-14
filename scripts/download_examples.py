# %% [markdown]
#
# # Download IMC example data
#

# %% [markdown]
# This script downloads IMC example raw data, a fully trained `ilastik` pixel classifier and the used panel file. The IMC raw data will be stored in the `raw` folder together with the panel file. The ilastik project will be stored in the project root.

# %%
from pathlib import Path
from urllib import request

raw_folder = Path("../raw")
raw_folder.mkdir(exist_ok=True, parents=True)

# Raw data and panel
for example_file_name, example_file_url in [
    (
        "Patient1.zip",
        "https://zenodo.org/record/5949116/files/Patient1.zip",
    ),
    (
        "Patient2.zip",
        "https://zenodo.org/record/5949116/files/Patient2.zip",
    ),
    (
        "Patient3.zip",
        "https://zenodo.org/record/5949116/files/Patient3.zip",
    ),
    (
        "Patient4.zip",
        "https://zenodo.org/record/5949116/files/Patient4.zip",
    ),
    (
        "panel.csv",
        "https://zenodo.org/record/5949116/files/panel.csv",
    )
]:
    example_file = raw_folder / example_file_name
    if not example_file.exists():
        request.urlretrieve(example_file_url, example_file)
        
# Ilastik project
ilastik_project = Path("..") / "IMCWorkflow.ilp"
if not ilastik_project.exists():
    request.urlretrieve("https://zenodo.org/record/6043544/files/IMCWorkflow.ilp", ilastik_project)

# %%
# !conda list
