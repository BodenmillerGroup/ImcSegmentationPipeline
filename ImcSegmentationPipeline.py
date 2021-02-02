#!/usr/bin/env python
# coding: utf-8

# In[1]:


from imctools.converters import ome2analysis
from imctools.converters import ome2histocat
from imctools.converters import mcdfolder2imcfolder
from imctools.converters import exportacquisitioncsv


# In[2]:


import sys
print(sys.path)
print(sys.executable)


# In[27]:


import os
import pathlib
import shutil
import re


# 
# # The IMC preprocessing pipeline for multiplexed image analysis
# 

# This is a pipeline to segment IMC data using Ilastik pixel classification as well as CellProfiler.
# 
# To run install the conda `imctools` envrionment found in `Setup/conda_imctools.yml`.   
# 
# -> Install conda  
# 
# -> On a conda console type: `conda env create -f setup/conda_imctools.yml`
# 
# Start a Jupyter instance in this environment to run this Jupyter Notebook.
# 
# This notebook will automatically download example data.
# 
# This dataset are zipped input_data_folders_path_inputs of the `.mcd` and all `.txt` files corresponding to one acquisitions session.
# This is my recomended data format as it preserves and contains all original metadata and enforces a consistent naming scheme.
# 
# Note that the `description` image name can be found in the `..._Acquisition_meta.csv` generated together with the ome tiffs
# as well as in the `cpinp` folder later in the script.
# After analysis the `Image.csv` metadata file generated in Cellprofiller will also contain the `Description` as well as other important metadata for each
# image, such as acquisition frequency, time, location etc.
# 
# For working with `.txt` files, please look at the older examples.
# 
# For any feedback please contact: Vito, vito.zanotelli@uzh.ch

# In[4]:


# the input_data_folders_path_inputs with the ziped acquisition files for the analysis
folders_path_inputs = ['../example_data']

# part that all considered files need to have in common
input_file_regexp = '.*.zip'

# output for OME tiffs
folder_path_base = '../analysis'


# pannel
file_path_csv_panel = '../config/example_panel.csv'
csv_panel_metal = 'Metal Tag'
csv_panel_ilastik = 'ilastik'
csv_panel_full = 'full'


# In[20]:


folder_path_base = pathlib.Path(folder_path_base)
folders_path_inputs = [pathlib.Path(f) for f in folders_path_inputs]
# parameters for resizing the images for ilastik

folder_path_analysis = folder_path_base / 'tiffs'
folder_path_ilastik= folder_path_base / 'ilastik'
folder_path_ome= folder_path_base / 'ometiff'
folder_path_cp = folder_path_base / 'cpout'
folder_path_cp_input = folder_path_base / 'cpinp'
folder_path_histocat = folder_path_base / 'histocat'

# Other output
file_path_cp_csv = folder_path_cp / 'panel.csv'
file_path_full_channels_csv = folder_path_cp_input / 'full_channelmeta.csv'
file_path_prob_channels_csv = folder_path_cp_input / 'probab_channelmeta_manual.csv'

suffix_full = '_full'
suffix_ilastik = '_ilastik'
suffix_ilastik_scale = '_s2'
suffix_mask = '_mask.tiff'
suffix_probablities = '_Probabilities'


failed_images = list()


# Generate all the input_data_folders_path_inputs if necessary

# In[7]:


for fol in [folder_path_base, folder_path_analysis, folder_path_ilastik,
            folder_path_ome, folder_path_cp, folder_path_histocat,
           folder_path_cp_input]:
    if not fol.exists():
        fol.mkdir(parents=True)


# In[8]:


## This will download the example data - remove if you work with your own data!
import urllib.request
fol_example = folders_path_inputs[0]
fol_example.mkdir(exist_ok=True)
urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
        ('20170906_FluidigmONfinal_SE.zip',
         'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]

for fn, url in urls:
    fn = fol_example / fn
    if not fn.exists():
        urllib.request.urlretrieve(url, fn)


# Convert mcd containing input_data_folders_path_inputs into imc zip input_data_folders_path_inputs

# In[10]:


get_ipython().run_cell_magic('time', '', "failed_images = list()\nre_fn = re.compile(input_file_regexp)\n\nfor fol in folders_path_inputs:\n    for fn in fol.glob('*'):\n        if re_fn.match(fn.name):\n            mcdfolder2imcfolder.mcdfolder_to_imcfolder(fn, output_folder=folder_path_ome,\n                                                       create_zip=False)")


# Generate a csv with all the acquisition metadata

# In[13]:


exportacquisitioncsv.export_acquisition_csv(folder_path_ome, output_folder=folder_path_cp_input)


# Export a copy of the panel to the output folder

# In[14]:


shutil.copy(file_path_csv_panel, file_path_cp_csv)


# Convert ome.tiffs to a HistoCAT compatible format, e.g. to do some visualization and channel checking.
# 
# -> Only required if HistoCAT is used as an image browser

# In[16]:


get_ipython().run_cell_magic('time', '', 'for fol in folder_path_ome.iterdir():\n    if fol.is_dir():\n        ome2histocat.omefolder_to_histocatfolder(fol, folder_path_histocat)')


# Generate the analysis stacks

# In[17]:


list_analysis_stacks =[
    (csv_panel_ilastik, suffix_ilastik, 0),
    (csv_panel_full, suffix_full, 0)]


# In[23]:


get_ipython().run_cell_magic('time', '', 'ome2analysis.omefolder_to_analysisfolder(folder_path_ome, folder_path_analysis, panel_csv_file=file_path_csv_panel,\n                                         analysis_stacks=(list_analysis_stacks), metalcolumn=csv_panel_metal)\n')


# Copy one csv containing the channel order of the full stack in to the cellprofiler input folder

# In[24]:


fn = next(folder_path_analysis.glob(f'*{suffix_full}.csv'))

shutil.copy(fn, file_path_full_channels_csv)


# Generate channel metadata for the probability stack

# In[25]:


probab_meta = ["CellCenter", "CellBorder", "Background"]
with open(file_path_prob_channels_csv, 'w') as f:
    f.write('\n'.join(probab_meta))


# # Next steps
# 
# This concludes the conversion of the IMC rawdata into usable TIFFs.
# 
# The pipelines can be found in the `cp4_pipeline` folder in this repository. They were tested in `cellprofiler 4.0.6).
# 
# The next steps are:
# 
# ### A) Cellprofiler: 1_prepare_ilastik
# 
# In this module we prepare the data for Ilastik pixel classification, by first removing strong outlier pixels, then scaling the images 2x and then taking random 500x500 crops to do the train the pixel classifier.
# 
# Note: for large datasets 250x250 crops or smaler should suffice!
# 
# The following parts of this module need to be adapted:
# 
# 1) File list: choose all files in the `tiff` subfolder
# 
# 2) Default Output Folder: Choose the `ilastik` subfolder
# 
# No further parts need to be adapted.
# In our 16 core computer this step takes ca 5 min for the example dataset.
# 
# 
# ### B) Ilatik: Train a pixel classifier
# 
# This uses the random crops generated in the last step.
# 
# 1) Make a new `pixel classification project`. -> An example project that works with the example data can be found in the 'analysis' subfolder.
# 
# 2) Add the `.h5` random crops: Raw data -> Add Seperate Images -> Select all `.h5` images in the `ilastik` subfolder.
# 
# 3) Proceed to `Feature Selection`
# 
# 4) Select suitable features (or just everything >= 1 pixels)
# 
# 5) Proceed to the classification:
# 
#     - Add 3 labels:
#         - 1: Nuclei
#         - 2: Cytoplasma/membrane
#         - 3: Background
#         - -> For large datasets adding the labels can take a while
#     - Start labeling:
#         - The box next to `Input Data` can change the channels. What each channel corresponds to can be seen when looking in any of the `..._ilastik.csv` files in the `tiff` folder. The 0 channel correspond to the sum of all channels, very usefull to label the background.
#         - Use window leveling change the contrast. Right click on the `Input Data` -> `Adjust Thresholds` is also very usefull
#         - Label opiniated: If you see in the nucleus channel that two nuclei are stuck together but have a faint dip in intensity in between, label this as 2: Cytoplasma. Encyrcle nuclei with Cytoplasma
#         - Diseable `Live Update` for performance
#         - Frequently check the `Uncertainties`: This indicates which pixels the classifier profits most if they are labeled. A well trained classifier has low uncertainty within class regions (e.g. Nuclei) and high uncertainty at class borders (e.g. between nuclei and cytoplasma).
# 
#     - If you think the classifier is well trained, export the probabilities:
#         - Export Settings -> Source: Probabilities -> Choose Export Image Settings:
#             - Convert to datatype: Unsigned Integer 16 bit
#             - Renormalize: check
#             - Format: Tiff
#             - File: leave default
#         - Export all: This generates `_Probabilities.tiff` in the `ilastik` folder. They can be checked using any image viewer
#             - To generate uncertainty maps (good to identify regions that need training),
#             run the `Convert probabilities to uncertainties` section `#For training` below. This will put uncertainties in the uncertainty folder.
#             -> Well trained classifiers have low uncertainty (transparent) everywhere but at class borders which should be white.
# 
#         - Optional: Train again regions with high uncertainty, then proceed.
# 
#         - Batch processing: -> Select raw data files -> select all `_s2.h5` files in the `tiff` folder. (sort by filetype, select all `H5` files).
#             -> This step takes a while and is computationally intensive!
#             -> Ca 15 min on 10 cores on the example data
# 
#         - Optional: use the below probability to uncertainty `#For the data` to convert all proabilities to uncertainties, check if there are any regions of high uncertainty and optionally crop the corresponding image part in imagej and add it to the training data.
#         - Note: store the `ilastik` folder with all the random crops and the trained classifier for reproducibility reasons.
#         
#         - A trained
# 
# ### C) Cellprofiler: 2_segment_ilastik
# 
# This step will segment the probabilities into masks.
# 
# Things to adapt:
# 
# 1) File list: choose again all files from the `tiffs` folder
# 
# 2) It is important to check the `IdentifyPrimaryObjects` step, if the segmentation settings are suitable!
#     This might vary strongly between cell/tissue/training and needs attention! Use the test mode and try various settings.
#     Also note the `smooth` step immediately before: This can be also removed, I just happen get good results with this additional step.
# 
# 3) Also the `MeasureObjectSizeShape` combined with `FilterObjects` is just some personal preference of mine, feel free to change
# 
# 4) `IdentifySecondaryObjects`: Here th mask is expanded to the full cell.
# 
# 5) `Rescale objects`: note that our segmentation was done on 2x upscaled images, this scales the masks down again. Note that potentially also the nuclei mask could be scaled down and further exported and used.
# 
# 6) The `Default Output Path` does not need to be adapted for this module.
# 
# 
# Note1: Seperating mask generation from mask measurement adds modularity and is thus highly recommended, as generating masks is one of the most resource intensive steps.
# 
# 
# ### D) Cellprofiler: 3_measure_mask
# 
# This step is not necessary for `HistoCat` only analysis. If `HistoCat` should be used, use the `Generate the histocat folder with masks` section below.
# 
# #### 3_measure_mask_basic
# 
# This module measures without considering spillover correction.
# 
# 1) File list: choose again all files from the `tiffs` folder
# 
# 2) View Output settings: set the `Default output folder` to the `cpout` folder and the
#     `Default input folder` to the `cpint` folder.
# 
# 3) Metadata: update - this will automatically merge the mcd metadata .csv generated earlier in the script with your images.
# 
# 4) Names and types: click update
# 
# 5) `Measure Object Intensity Multichannel`: Adapt the channel numbers. Check the `_full.csv` files in the `tiffs` folder to see how many channels the stack have and adapt accordingly.
# 
# 6) `Measure Image Intensity Multichannel`: Adapt the channel numbers. Check the `_full.csv` files in the `tiffs` folder to see how many channels the stack have and adapt accordingly.
# 
# Notes:
# - In this pipeline all the intesities are scaled by `1/(2**16)`
# - The mapping between channel number c1, c2, c3 corresponds to the position in the `_full.csv`s found in the `tiffs` folder.
# - The original acquisition description, acquisition frequencies etc can be found in the `Image.csv` output as `Metdata_...` columns.
# - This outputs a lot of measurements that are acutally of little interest - usually we only look at `meanintensity` per channel and cell.
#     To reduce the outputs, select in `Export To Spreadsheet` -> `Select Measurements to Export` -> Only the measurements you want (usually all Image measurements and only the `MeanIntensity` fullstack measurements).
# - The `FullStack` can also be not measured, as it is almost identical to the `FullStackFiltered`.
# 
# #### 3_measure_mask_compensated
# This will also have a spillover corrections step - stay tuned!
# 
# 
# ### E) Pipeline output
# 
# The pipeline output is all in the `cpout` folder.
# 
# Files and folders:
# - Image.csv: Image level metadata
# - var_Image.csv: Metadata for the colums in Image.csv.
#     This contains also metadata from the IMC such as acquisition coordinates.
# 
# - {object}.csv: eg cell.csv, contains cell slice level measurements
# - var_{object}.csv: eg var_cell.csv: contains metadata for the object measurements
# 
# - panel.csv: a copy of the panel used for the input
# 
# - Object relationships.csv: Object neighbourhood and other relationships
# 
# - Experiment.csv: Metadata about the actual measurement run (eg pipeline used,...)

# ## Generate the histocat folder with masks

# In[31]:


get_ipython().run_cell_magic('time', '', "for fol in folder_path_ome.glob('*'):\n    ome2histocat.omefolder_to_histocatfolder(fol, folder_path_histocat,\n                                    mask_folder=folder_path_analysis, mask_suffix=suffix_mask, dtype='uint16')")

