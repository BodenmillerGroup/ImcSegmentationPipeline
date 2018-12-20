
# coding: utf-8

# In[1]:


from imctools.scripts import ometiff2analysis
from imctools.scripts import imc2tiff
from imctools.scripts import ome2micat
from imctools.scripts import probablity2uncertainty
from imctools.scripts import convertfolder2imcfolder
from imctools.scripts import exportacquisitioncsv


# In[2]:


import os
import logging
import re
import zipfile


# 
# # The IMC preprocessing pipeline for multiplexed image analysis
# 

# This is a pipeline to segment IMC data using Ilastik pixel classification as well as CellProfiler.
# 
# It requires:
# - CellProfiler 3.1.5: http://cellprofiler.org/releases/
# - Ilastik: http://ilastik.org/
# - The following Github repositories:
#     => Either Clone (e.g. using command line git or the github deskop client: https://desktop.github.com/) OR download and unzip these repositories to a local folder:
#     - ImcPluginsCP plugins of the development branch: develop-cp3, https://github.com/BodenmillerGroup/ImcPluginsCP/tree/develop-cp3
#           - This repository contains additional CellProfiller modules.
#           - **In the preferences of CellProfiller point the CellProfiler Plugins folder to `ImcPluginsCP/plugins`**
#       
#     - The ImcSegmentationPipeline repository: https://github.com/BodenmillerGroup/
#         - contains the conda environment that you will use bellow in the `setup` folder
#         - contains the CellProfiler pipelines to be used
# 
# 
# - Install the `imctools` conda environment
#     - If you have already an older version of this installed, please uninstall it first
#  
#     - To install the `imctools` envrionment:
#         -> Install conda: https://www.anaconda.com/download/#linux
#         -> The conda environment file is found in  `ImcSegmentationPipeline/Setup/conda_imctools.yml`
#         -> On a conda console type: `conda env create -f PATHTO/conda_imctools.yml` OR use the Anaconda GUI -> Environments -> Import -> choose `setup/conda_imctools.yml`
#         -> Start a Jupyter notebook instance *in this conda environment* and open this script: 
#             -`conda activate imctools`
#             -`conda jupyter notebook`
#             - OR in the GUI: choose the `imctools` environment, start `Jupyter Notebook`
#             - open the `ImcSegmentationPipeline/scripts/imc_preprocessing.ipynb`
#             - Execute the script cell by cell using `shift-enter`
# 
# - If compensation should be done (https://www.cell.com/cell-systems/abstract/S2405-4712(18)30063-2), the following additional requirements are needed:
#     - A spillover matrix specific to the isotope lots used for antibody conjugation
#         - Use the experimental protocol of:https://docs.google.com/document/d/195eViUqHoYRKrkoy_NkIdJPmyx1-OuDaSjiWQBy4weA/edit
#             -> Will result in a spillovermatrix in `.csv` format.
#         - Clone the Github repository: 
#         - R > 3.5 (https://cran.r-project.org/bin/windows/base/)
#         - Rstudio: https://www.rstudio.com/products/rstudio/download/
#         - CATALYST >= 1.4.2: https://bioconductor.org/packages/release/bioc/html/CATALYST.html
#         - 'tiff' R library: run `install.packages('tiff')`
# 
# 
# - Data requirements:
#     - This scripts assume that *each `.mcd`  acquisition and all `.txt` files corresponding to this '.mcd' acquisition* are saved in one a seperate `.zip` folder.
#         -> This is my recomended data format as it preserves and contains all original metadata and enforces a consistent naming scheme.
#     - see the example files that are downloaded bellow for an example
# 
# Note that the `description` image name can be found in the `..._Acquisition_meta.csv` generated together with the ome tiffs as well as in the `cpout` folder later in the script.
# After analysis the `Image.csv` metadata file generated in Cellprofiller will also contain the `Description` as well as other important metadata for each 
# image, such as acquisition frequency, time, location etc.
# 
# For working with `.txt` files only, please look at the older examples.
# 
# For any feedback please contact: Vito, vito.zanotelli@uzh.ch or even better raise an issue on this Github page!

# ### Input folders (Needs to be adapted for use)

# In[3]:


# the folders with the ziped acquisition files for the analysis
folders = ['../example_data']

# part that all considered acquisition files need to have in common
# -> can be adapted to only process a subset of the acquisitions
file_regexp = '.*.zip'

# output folder
folder_base = '/home/vitoz/Data/Analysis/201805_cp_segmentation_example'


# pannel
csv_pannel = '../config/example_pannel.csv'
csv_pannel_metal = 'Metal Tag'
csv_pannel_ilastik = 'ilastik'
csv_pannel_full = 'full'


# ### Other Input (only change if really necessary and you know what your doing)

# In[4]:


# parameters for resizing the images for ilastik

folder_analysis = os.path.join(folder_base, 'tiffs')
folder_ilastik = os.path.join(folder_base, 'ilastik')
folder_ome = os.path.join(folder_base, 'ometiff')
folder_cp = os.path.join(folder_base, 'cpout')
folder_histocat = os.path.join(folder_base, 'histocat')
folder_uncertainty = os.path.join(folder_base, 'uncertainty')

suffix_full = '_full'
suffix_ilastik = '_ilastik'
suffix_ilastik_scale = '_s2'
suffix_mask = '_mask.tiff'
suffix_probablities = '_Probabilities'


failed_images = list()

# Make a list of all the analysis stacks with format:
# (CSV_NAME, SUFFIX, ADDSUM)
# CSV_NAME: name of the column in the CSV to be used
# SUFFIX: suffix of the tiff
# ADDSUM: BOOL, should the sum of all channels be added as the first channel?
list_analysis_stacks =[
    (csv_pannel_ilastik, suffix_ilastik, 1),
    (csv_pannel_full, suffix_full, 0)
]


# Generate all the folders if necessary

# In[5]:


for fol in [folder_base, folder_analysis, folder_ilastik,
            folder_ome, folder_cp, folder_histocat, folder_uncertainty]:
    if not os.path.exists(fol):
        os.makedirs(fol)


# ### Optional step: download the example data
# This example comes with example data.
# => Diseable the cell if you are using your own data

# In[6]:


## This will download the example data - remove if you work with your own data!
import urllib.request
fol_example = folders[0]
os.makedirs(os.path.abspath(fol_example), exist_ok=True)
urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
       ('20170906_FluidigmONfinal_SE.zip',
        'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]
       
for fn, url in urls:
    fn = os.path.join(fol_example, fn)
    if os.path.exists(fn) == False:
        urllib.request.urlretrieve(url, fn)


# ### Convert zipped IMC acquisitions to input format
# 
# This script works with zipped IMC acquisitions:
# Each acquisition session = (1 mcd file) should be zipped in a folder containing:
# - The `.mcd` file
# - All associated `.txt` file generated during the acquisition of this `.mcd` file -> Don't change any of the filenames!!

# Convert mcd containing folders into imc zip folders

# In[7]:


get_ipython().run_cell_magic('time', '', "failed_images = list()\nre_fn = re.compile(file_regexp)\n\nfor fol in folders:\n    for fn in os.listdir(fol):\n        if re_fn.match(fn):\n            fn_full = os.path.join(fol, fn)\n            print(fn_full)\n            try:\n                convertfolder2imcfolder.convert_folder2imcfolder(fn_full, out_folder=folder_ome,\n                                                                   dozip=False)\n            except:\n                logging.exception('Error in {}'.format(fn_full))")


# Generate a csv with all the acquisition metadata

# In[8]:


exportacquisitioncsv.export_acquisition_csv(folder_ome, fol_out=folder_cp)


# Convert ome.tiffs to a HistoCAT compatible format, e.g. to do some visualization and channel checking.

# In[9]:


get_ipython().run_cell_magic('time', '', "if not(os.path.exists(folder_histocat)):\n    os.makedirs(folder_histocat)\nfor fol in os.listdir(folder_ome):\n    ome2micat.omefolder2micatfolder(os.path.join(folder_ome,fol), folder_histocat, dtype='uint16')")


# Generate the analysis stacks

# In[10]:


get_ipython().run_cell_magic('time', '', "for fol in os.listdir(folder_ome):\n    sub_fol = os.path.join(folder_ome, fol)\n    for img in os.listdir(sub_fol):\n        if not img.endswith('.ome.tiff'):\n            continue\n        basename = img.rstrip('.ome.tiff')\n        print(img)\n        for (col, suffix, addsum) in list_analysis_stacks:\n            try:\n                ometiff2analysis.ometiff_2_analysis(os.path.join(sub_fol, img), folder_analysis,\n                                                basename + suffix, pannelcsv=csv_pannel, metalcolumn=csv_pannel_metal,\n                                                usedcolumn=col, addsum=addsum, bigtiff=False,\n                                               pixeltype='uint16')\n            except:\n                logging.exception('Error in {}'.format(img))\n            \n")


# # Next steps
# 
# This concludes the conversion of the IMC rawdata into usable TIFFs.
# 
# The pipelines can be found in the `cp3_pipeline` folder in this repository. They were tested in `cellprofiler 3.1.5`.
# 
# The next steps are:
# 
# ### A) Cellprofiler: 1_prepare_ilastik
# 
# In this module we prepare the data for Ilastik pixel classification, by first removing strong outlier pixels, then scaling the images 2x and then taking random 500x500 crops to do the train the pixel classifier.
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
# 1) Make a new `pixel classification project`. Save the project file in the `ilastik` subfolder.
# 
# 2) Add the `.h5` random crops: Raw data -> Add Seperate Images -> Select all `.h5` images in the `ilastik` subfolder.
# 
# 3) Proceed to `Feature Selection`
# 
# 4) Select suitable features (or just everythin > 1 pixels)
# 
# 5) Proceed to the classification:
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
# 6) If you think the classifier is well trained, export the probabilities:
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
# 7) If you think that you are finished with classification, you need to apply the classifier to your whole dataset usingBatch processing:
#         - Make sure the Export Settings are still the same as in the step 6), then go to the 'Batch Processing' step in ilastik.
#         - Select raw data files -> select all `_s2.h5` files in the `tiff` folder. (sort by filetype, select all `H5` files).
#         => This step takes a while and is computationally intensive!
#         => Ca 15 min on 10 cores on the example data
#             
#         - Optional: use the below probability to uncertainty `#For the data` to convert all proabilities to uncertainties, check if there are any regions of high uncertainty and optionally crop the corresponding image part in imagej and add it to the training data.
#         - Note: store the `ilastik` folder with all the random crops and the trained classifier for reproducibility reasons.
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
# 2) View Output settings: set the `Default output folder` to the `cpout` folder
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
# #### 3_measure_mask_compensation
# This will do measurements and also single cell data compensation
# 0) Run the script: https://github.com/BodenmillerGroup/cyTOFcompensation/blob/master/scripts/imc_adaptsm.Rmd in R:
#     - Adapt the path to the spillover matrix `fn_sm='.../path/to/sm/spillmat.csv'`. In this example data it can be found at:
#         `fn_sm = 'PATHTO/ImcSegmentationPipeline/config/20170707_example_spillmat.csv'`
#     - Choose any `_full.csv` file, generated during the `Generate analysis stacks` step in the output folder, for the `fn_imc_metals = '/path/to/anyfile_full.csv' `.
#         In this example this could be: `fn_imc_metals = 'PATHTO/tiffs/20170905_Fluidigmworkshopfinal_SEAJa_s0_p0_r0_a0_ac_full.csv'`
#     - Run the script and this will produce an `PATHTO/tiffs/imc_full_sm.tiff` file
# 
# 1) File list: choose again all files from the `tiffs` folder
# 
# 2) View Output settings: set the `Default output folder` to the `cpout` folder
# 
# 3) Metadata: update - this will automatically merge the mcd metadata .csv generated earlier in the script with your images.
# 
# 4) Names and types:  Make sure that in `NamesAndTypes` the `PATHTO/tiffs/imc_full_sm.tiff` file is selected, click update
# 
# 5) `Measure Object Intensity Multichannel`: Adapt the channel numbers. Check the `_full.csv` files in the `tiffs` folder to see how many channels the stack have and adapt accordingly.
# 
# 6) `Measure Image Intensity Multichannel`: Adapt the channel numbers. Check the `_full.csv` files in the `tiffs` folder to see how many channels the stack have and adapt accordingly.
# 
# 7) `CorrectSpilloverApply`: This will generate a corrected image stack, this can be used e.g. to do measurements of intensity distribution. For measurements of intensity it is however better to correct the measurement afterward using the `CorrectSpilloverMeasurement`.
# 
# 8) `CorrectSpilloverMeasurement`: Here the intensity measurement can be spillover corrected. Note that this makes only sense for linear combinations of intensity measurements such as `MeanIntensity` or `TotalIntensity`. For these it is more accurate to do this after measurement than doing it on the pixel level beforehand. Note that for things with non linear transformations as `MedianIntensity`, this will not result in valid results and these measurements should be done on beforehand corrected images from `CorrectSpilloverApply`.

# ## Convert probabilities to uncertainties

# In[11]:


# For training
for fn in os.listdir(folder_ilastik):
    if fn.endswith(suffix_probablities+'.tiff'):
        print(fn)
        probablity2uncertainty.probability2uncertainty(os.path.join(folder_ilastik,fn), folder_uncertainty)


# In[12]:


# For the data
for fn in os.listdir(folder_analysis):
    if fn.endswith(suffix_probablities+'.tiff'):
        print(fn)
        probablity2uncertainty.probability2uncertainty(os.path.join(folder_analysis,fn), folder_uncertainty)


# ## Generate the histocat folder with masks

# In[13]:


get_ipython().run_cell_magic('time', '', "for fol in os.listdir(folder_ome):\n    ome2micat.omefolder2micatfolder(os.path.join(folder_ome,fol), folder_histocat, \n                                         fol_masks=folder_analysis, mask_suffix=suffix_mask, dtype='uint16')")

