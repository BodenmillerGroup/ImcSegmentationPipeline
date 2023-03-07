# %%
# import sys

# from pathlib import Path

# # !{sys.executable} -m pip install -e {Path.cwd().parent}

# %%
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pandas as pd

import imcsegpipe
from imcsegpipe.utils import sort_channels_by_mass

# %% [markdown]
#
# # Preprocessing of IMC data for image segmentation
#

# %% [markdown]
# This script presents the first step of the IMC segmentation pipeline.
#  
# To get started, please refer to the [Get started guide](https://bodenmillergroup.github.io/ImcSegmentationPipeline/) and to download example data you can run the script `scripts/download_examples.ipynb`.
#  
# **Requirements for the input data:**
#  
# We recommend to supply the raw data in form of **one zip archive per acquisition session**.
# This zip archive should contain the `.mcd` file and all `.txt` files corresponding to individual acquisitions.
#  
# To understand the output format, please refer to the [Output](https://bodenmillergroup.github.io/ImcSegmentationPipeline/output.html) documentation.
#  
# Please raise an issue [here](https://github.com/BodenmillerGroup/ImcSegmentationPipeline/issues) for feedback, bug fixes and feature requests.

# %% [markdown]
# ## Specify the inputs
#
# Here, you will need to specify where the IMC raw data (in form of `.zip` archives) are stored.
# The `raw_dirs` variable describes the path (one or multiple) where the `.zip` archives are located.
# Here, we use the example data (located in the `raw` folder) to run the pre-processing part of the pipeline.
# The `file_regex` variable specifies a [glob](https://towardsdatascience.com/the-python-glob-module-47d82f4cbd2d) entry to select all files of interest from the input directory.
# As an example: if you want to select all files that contain the word "Patient", you would use the glob expression `"*Patient*.zip"`.
#  
# You will also need to specify the location of the panel file (`panel_file`) that contains information regarding the column that contains the metal/channel name (`panel_channel_col`), the column that contains an identifier if the channel should be used for ilastik training (`panel_ilastik_col`), and the column that contains an identifier if the channel should be used to generate the final stack of channels (`panel_keep_col`). The latter two arguments specify columns which contain 0s or 1s, 1 meaning the indicated channel is used and 0 meaning the channel is not used.

# %%
# the paths with the ziped acquisition files
raw_dirs = ["../raw"]
raw_dirs = [Path(raw_dir) for raw_dir in raw_dirs]

# regular expression to select files
file_regex = "*Patient*.zip"

# panel information
panel_file = "../raw/panel.csv"
panel_channel_col = "Metal Tag"
panel_keep_col = "full"
panel_ilastik_col = "ilastik"

# %% [markdown]
# ## Specify the outputs
#
# You will need to specify a single folder where the output files of the pipeline are written out to (`work_dir`).
# Within the working directory, the following sub-folder will be created:
#
# * `acquisitions_dir`: storing individual acquisitions as `.ome.tiff` files, panoramas as `.png` and acquisition metadata (default `analysis/ometiff`)
# * `ilastik_dir`: storing multi-channel images in `.tiff` format for ilastik training. The channel order for each image is written out in `.csv` format (default `analysis/ilastik`). Following the CellProfiler pipelines, all files related to the ilastik segmentation approach will be stored here. 
# * `crops_dir`: stores image crops for ilastik training after running the first CellProfiler pipeline (default `analysis/crops`)
# * `cellprofiler_input_dir`: all files needed for CellProfiler input (default `analysis/cpinp`)
# * `cellprofiler_output_dir`: all files written out by CellProfiler (default `analysis/cpout`)
# * `histocat_dir`: folders containing single-channel images for histoCAT upload (default `analysis/histocat`)
#
# Within the `cellprofiler_output_dir` three subfolders are created storing the final images:
#
# * `final_images_dir`: stores the hot pixel filtered multi-channel images containing selected channels (default `analysis/cpout/images`)
# * `final_masks_dir`: stores the final cell segmentation masks (default `analysis/cpout/masks`)
# * `final_probabilities_dir`: stores the downscaled pixel probabilities after ilastik classification (default `analysis/cpout/probabilities`)

# %%
# working directory storing all outputs
work_dir = "../analysis"
work_dir = Path(work_dir)
work_dir.mkdir(exist_ok=True)

# general output directories
acquisitions_dir = work_dir / "ometiff"
ilastik_dir = work_dir / "ilastik"
crops_dir = work_dir / "crops"
cellprofiler_input_dir = work_dir / "cpinp"
cellprofiler_output_dir = work_dir / "cpout"
histocat_dir = work_dir / "histocat"

# Final output directories
final_images_dir = cellprofiler_output_dir / "images"
final_masks_dir = cellprofiler_output_dir / "masks"
final_probabilities_dir = cellprofiler_output_dir / "probabilities"

# %% [markdown]
# The specified folder will now be created.

# %%
acquisitions_dir.mkdir(exist_ok=True)
crops_dir.mkdir(exist_ok=True)
ilastik_dir.mkdir(exist_ok=True)
cellprofiler_input_dir.mkdir(exist_ok=True)
cellprofiler_output_dir.mkdir(exist_ok=True)
histocat_dir.mkdir(exist_ok=True)

final_images_dir.mkdir(exist_ok=True)
final_masks_dir.mkdir(exist_ok=True)
final_probabilities_dir.mkdir(exist_ok=True)

# %% [markdown]
# ## Convert `.mcd` files to `.ome.tiff` files
#
# In the first step, the `.zip` archives containing `.mcd` files are converted to folders, which contain `.ome.tiff` files, channel metadata files, panoramas and slide overviews. The `.ome.tiff` files can be read in by commercial and open-source software such as `ImageJ` using the BioFormats importer. The `.csv` files contain the order of the channels as well as the antibody names. The `_pano.png` contain the acquired panoramas; the `_slide.png` contains the slide overview. The `_schema.xml` contains metadata regarding the acquisition session.  
# At this stage, only `.zip` files specified by `file_regex` will be processed.
#
# In the following chunk, individual acquisition metadata are written out as `acquisition_metadata.csv` file in the `cellprofiler_output_dir` folder. 

# %%
temp_dirs: List[TemporaryDirectory] = []

try:
    for raw_dir in raw_dirs:
        zip_files = list(raw_dir.rglob(file_regex))
        if len(zip_files) > 0:
            temp_dir = TemporaryDirectory()
            temp_dirs.append(temp_dir)
            for zip_file in sorted(zip_files):
                imcsegpipe.extract_zip_file(zip_file, temp_dir.name)
    acquisition_metadatas = []
    for raw_dir in raw_dirs + [Path(temp_dir.name) for temp_dir in temp_dirs]:
        mcd_files = list(raw_dir.rglob("*.mcd"))
        mcd_files=[(i) for i in mcd_files if not i.stem.startswith('.')]
        if len(mcd_files) > 0:
            txt_files = list(raw_dir.rglob("*.txt"))
            txt_files=[(i) for i in txt_files if not i.stem.startswith('.')]
            matched_txt_files = imcsegpipe.match_txt_files(mcd_files, txt_files)
            for mcd_file in mcd_files:
                acquisition_metadata = imcsegpipe.extract_mcd_file(
                    mcd_file,
                    acquisitions_dir / mcd_file.stem,
                    txt_files=matched_txt_files[mcd_file],
                )
                acquisition_metadatas.append(acquisition_metadata)
    acquisition_metadata = pd.concat(acquisition_metadatas, copy=False)
    acquisition_metadata.to_csv(cellprofiler_input_dir / "acquisition_metadata.csv")
finally:
    for temp_dir in temp_dirs:
        temp_dir.cleanup()
    del temp_dirs

# %% [markdown]
# Here, a copy of the panel file is transferred to the `cellprofiler_output_dir`. 

# %%
shutil.copy2(panel_file, cellprofiler_output_dir / "panel.csv")

# %% [markdown]
# ## Convert `.ome.tiff` files to `histoCAT` compatible format
#
# In the next step, we will convert the generated `.ome.tiff` files to a format that [histoCAT](https://bodenmillergroup.github.io/histoCAT/) can read.
# For each acquistion (each `.ome.tiff` file), the `export_to_histocat` function call produces one folder that contains single channel tiff files. All channels contained in the `.ome.tiff` files are written out.

# %%
for acquisition_dir in acquisitions_dir.glob("[!.]*"):
    if acquisition_dir.is_dir():
        imcsegpipe.export_to_histocat(acquisition_dir, histocat_dir)

# %% [markdown]
# ## Generate image stacks for downstream analyses
#
# Next, we will generate two stacks of multi-channel `.tiff` images:
#
# **1. Full stack:** The full stack contains all channels specified by the "1" entries in the `panel_keep_col` column of the panel file. This stack will be later used to measure cell-specific expression features of the selected channels.
#
# **2. Ilastik stack:** The ilastik stack contains all channels specified by the "1" entries in the `panel_ilastik_col` column of the panel file. This stack will be used to perform the ilastik training to generate cell, cytoplasm and background probability masks (see [Ilastik training](https://bodenmillergroup.github.io/ImcSegmentationPipeline/ilastik.html)).
#
# **Of note:** Both image stacks are now by default hot pixel filtered (see below). To write out the raw image data without filtering set `hpf=None`.
#
# The `create_analysis_stacks` function takes several arguments:
#
# * `acquisition_dir`: specifies the folder containing the `.ome.tiff` files.  
# * `analysis_dir`: specifies the folder where the `.tiff` stacks should be stored.  
# * `analysis_channels`: specifies the channel names used for the specific image stack.  
# * `suffix`: the suffix to be added at the end of the file name.
# * `hpf`: single number indicating the threshold for hot pixel filtering (see below). Setting `hpf=None` disables hot pixel filtering. 
#
# **Hot pixel filtering:** Each pixel intensity is compared against the maximum intensity of the 3x3 neighboring pixels. If the difference is larger than `hpf`, the pixel intensity is clipped to the maximum intensity in the 3x3 neighborhood. 

# %%
panel: pd.DataFrame = pd.read_csv(panel_file)

for acquisition_dir in acquisitions_dir.glob("[!.]*"):
    if acquisition_dir.is_dir():
        # Write full stack
        imcsegpipe.create_analysis_stacks(
            acquisition_dir=acquisition_dir,
            analysis_dir=final_images_dir,
            analysis_channels=sort_channels_by_mass(
                panel.loc[panel[panel_keep_col] == 1, panel_channel_col].tolist()
            ),
            suffix="_full",
            hpf=50.0,
        )
        # Write ilastik stack
        imcsegpipe.create_analysis_stacks(
            acquisition_dir=acquisition_dir,
            analysis_dir=ilastik_dir,
            analysis_channels=sort_channels_by_mass(
                panel.loc[panel[panel_ilastik_col] == 1, panel_channel_col].tolist()
            ),
            suffix="_ilastik",
            hpf=50.0,
        )

# %% [markdown]
# ## Export additional metadata
#
# Finally, we will copy a file that contains the correct order of channels for the exported full stacks to the `cellprofiler_input_dir`.

# %%
first_channel_order_file = next(final_images_dir.glob("[!.]*_full.csv"))
shutil.copy2(first_channel_order_file, cellprofiler_input_dir / "full_channelmeta.csv")

# %% [markdown]
# We will also generate channel metadata for the probability stack (see [Ilastik training](https://bodenmillergroup.github.io/ImcSegmentationPipeline/ilastik.html)).

# %%
probab_meta = ["CellCenter", "CellBorder", "Background"]
with open(cellprofiler_input_dir / "probab_channelmeta_manual.csv", "w") as f:
    f.write("\n".join(probab_meta))

# %% [markdown]
# This concludes the pre-processing of the raw image files. In [the next step](https://bodenmillergroup.github.io/ImcSegmentationPipeline/ilastik.html), we will prepare the images for ilastik pixel classification.

# %% [markdown]
# ## Generate the histocat folder with masks (optional)
#
# This function can be used to convert the `.ome.tiff` files together with the mask files, which are generated in the [segmentation step](https://bodenmillergroup.github.io/ImcSegmentationPipeline/segmentation.html) to a format that is recognized by the `histoCAT` software. To use the function you will need to remove `#` from the following code chunk.

# %%
#for acquisition_dir in acquisitions_dir.glob("[!.]*"):
#    if acquisition_dir.is_dir():
#        imcsegpipe.export_to_histocat(
#            acquisition_dir, histocat_dir, mask_dir=final_masks_dir
#        )

# %%
# !conda list

# %%
