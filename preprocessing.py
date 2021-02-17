#!/usr/bin/env python
# coding: utf-8

# # Preprocessing of IMC data for image segmentation

# This script presents the first step of the IMC segmentation pipeline.
# 
# To get started, please refer to the [Get started guide](docs/index.md).
# For more information on how to use the `imctools` package, please refer to this [documentation](https://bodenmillergroup.github.io/imctools/).
# 
# Following this script, you will find an option to download example data.
# 
# **Requirements for the input data:**
# 
# We recommend to supply the raw data in form of _one zip archive per acquisition session_.
# This zip archive should contain the `.mcd` file and all `.txt` files corresponding to one acquisition session.
# For working with `.txt` files, please look at the older examples.
# 
# To understand the output format, please refer to the [Output](docs/output.md) documentation.
# 
# For any feedback please contact: Vito, vito.zanotelli@uzh.ch

# ## Load required libraries
# 
# In the first step, we will load the python libraries that are required for processing the data.

# In[1]:


from imctools.converters import ome2analysis
from imctools.converters import ome2histocat
from imctools.converters import mcdfolder2imcfolder
from imctools.converters import exportacquisitioncsv


# In[2]:


import sys
import os
import pathlib
import shutil
import re


# ## (Optional) Obtain the example data
# 
# Here, a set of example data is downloaded. 
# These can be used to test the pipeline.
# When using your own data, please ignore the following code chunk.

# In[3]:


import urllib.request

# Specify example input directory
fol_example = pathlib.Path('example_data')
fol_example.mkdir(exist_ok=True)

# Specify urls
urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
        ('20170906_FluidigmONfinal_SE.zip',
         'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]

# Download the data to the example input directory
for fn, url in urls:
    fn = fol_example / fn
    if not fn.exists():
        urllib.request.urlretrieve(url, fn)


# ## Specify the inputs
# 
# Here, you will need to specify where the IMC raw data (in form of `.zip` archives) are stored.
# The `folders_path_inputs` describes the path where the `.zip` archives are located.
# Here, we use the example data to run the pre-processing part of the pipeline.
# The `input_file_regexp` parameter specifies a [regular expression](https://docs.python.org/3/library/re.html) to select all files of interest from the input directory.
# As an example: if you want to select all files that contain the word "test", you would use the regular expression `'.*test.*.zip'`.
# 
# You will also need to specify the location of the panel file (`file_path_panel`) that contains information regarding the column that contains the metal name (`metal_colname`), the column that contains an identifier if the channel should be used for ilastik training (`ilastik_colname`), and the column that contains an identifier if the channel should be used to generate the final stack of channels (`full_colname`). The latter two arguments specify columns which contain 0s or 1s, 1 meaning the indicated channel is used and 0 meaning the channel is not used.

# In[10]:


# Path to input folder
folders_path_inputs = ['example_data']

# Regular expression to select files of interest
input_file_regexp = '.*.zip'

# Specifications of the panel file
file_path_panel = 'config/example_panel.csv'
metal_colname = 'Metal Tag'
ilastik_colname = 'ilastik'
full_colname = 'full'


# ## Specify the outputs
# 
# You will need to specify a single folder where the output files of the pipeline are written out to.
# Furthermore, we will need to specify a suffix, which will be added to the names of the `.tiff` stacks that are needed for ilastik training and object measurements (see *Generate image stacks for downstream analysis* section below).

# In[13]:


# output for OME tiffs
folder_path_base = 'analysis'

# Suffix to be added to output tiff stacks
suffix_full = '_full'
suffix_ilastik = '_ilastik'


# In the next chunk, all sub-folders for the output files are generated automatically.

# In[17]:


folder_path_base = pathlib.Path(folder_path_base)
folders_path_inputs = [pathlib.Path(f) for f in folders_path_inputs]

# Output sub-folders
folder_path_tiffs = folder_path_base / 'tiffs'
folder_path_ilastik= folder_path_base / 'ilastik'
folder_path_ome= folder_path_base / 'ometiff'
folder_path_cp = folder_path_base / 'cpout'
folder_path_cp_input = folder_path_base / 'cpinp'
folder_path_histocat = folder_path_base / 'histocat'

# Other output
file_path_cp_csv = folder_path_cp / 'panel.csv'
file_path_full_channels_csv = folder_path_cp_input / 'full_channelmeta.csv'
file_path_ilastik_channels_csv = folder_path_cp_input / 'ilastik_channelmeta.csv'
file_path_prob_channels_csv = folder_path_cp_input / 'probab_channelmeta_manual.csv'

for fol in [folder_path_base, folder_path_analysis, folder_path_ilastik,
            folder_path_ome, folder_path_cp, folder_path_histocat,
           folder_path_cp_input]:
    if not fol.exists():
        fol.mkdir(parents=True)


# ## Convert `.mcd` files to `.ome.tiff` files
# 
# In the first step, we will convert the `.zip` archives containing `.mcd` files to folders, which contain `.ome.tiff` files, panoramas and slide overviews using the [mcdfolder_to_imcfolder](https://bodenmillergroup.github.io/imctools/converters/mcdfolder2imcfolder.html#imctools.converters.mcdfolder2imcfolder.mcdfolder_to_imcfolder) function. The `.ome.tiff` files can be read in by commercial and open-source software such as ImageJ using the BioFormats importer. 
# We will store files that can't be processed in the `failed_images` list object to allow quality control.
# At this stage, only images specified by `input_file_regexp` will be processed.

# In[6]:


failed_images = list()
re_fn = re.compile(input_file_regexp)

for fol in folders_path_inputs:
    for fn in fol.glob('*'):
        if re_fn.match(fn.name):
            
            try:
                mcdfolder2imcfolder.mcdfolder_to_imcfolder(input=fn, 
                                                           output_folder=folder_path_ome,
                                                           create_zip=False)
                print(fn.name)
                
            except:
                print(fn.name + " can't be processed!")
                failed_images.append(fn.name)


# We can also now observe the failed conversions:

# In[7]:


print(failed_images)


# ### Export additional metadata
# 
# In the next section, we will export the metadata associated with the different acquisitions using the [export_acquisition_csv](https://bodenmillergroup.github.io/imctools/converters/exportacquisitioncsv.html#imctools.converters.exportacquisitioncsv.export_acquisition_csv) function as well as a copy of the panel file.

# In[11]:


# Export acquisition metadata
exportacquisitioncsv.export_acquisition_csv(root_folder=folder_path_ome, 
                                            output_folder=folder_path_cp_input)

# Copy panel to output folder
shutil.copy(file_path_panel, file_path_cp_csv)


# ## Convert `.ome.tiff` files to `histoCAT` compatible format
# 
# In the next step, we will convert the generated `.ome.tiff` files to a format that [histoCAT](https://bodenmillergroup.github.io/histoCAT/) can recognize.
# For each acquistion (each `.ome.tiff` file), the [omefolder_to_histocatfolder](https://bodenmillergroup.github.io/imctools/converters/ome2histocat.html#imctools.converters.ome2histocat.omefolder_to_histocatfolder) function call produces one folder that contains single channel tiff files. Here, all channels contained in the `.ome.tiff` files are written out.

# In[12]:


for fol in folder_path_ome.iterdir():
    if fol.is_dir():
        ome2histocat.omefolder_to_histocatfolder(input_folder=fol, 
                                                 output_folder=folder_path_histocat)


# ## Generate image stacks for downstream analyses
# 
# Next, we will generate two stacks of multi-channel `.tiff` images:
# 
# **1. Full stack:** The full stack contains all channels specified by the "1" entries in the `full_colname` column of the panel file. This stack will be later used to measure cell-specific expression features of the selected channels.
# 
# **2. Ilastik stack:** The ilastik stack contains all channels specified by the "1" entries in the `ilastik_colname` column of the panel file. This stack will be used to perform the ilastik training to generate cell, cytoplasm and background probability masks (see [Ilastik training](https://bodenmillergroup.github.io/ImcSegmentationPipeline/ilastik.html)).
# 
# The [omefolder_to_analysisfolder](https://bodenmillergroup.github.io/imctools/converters/ome2analysis.html#imctools.converters.ome2analysis.omefolder_to_analysisfolder) function takes several arguments:
# 
# `input_folder` specifies the folder containing the `.ome.tiff` files.  
# `output_folder` specifies the folder where the `.tiff` stacks should be stored.  
# `panel_csv_file` specifies the path to the panel file.  
# `analysis_stacks` takes an array of analysis stack definitions in a tuple format (column, suffix). Here, column specifies the panel column containing 0s and 1s indicating which channels to use and suffix spcifies the suffix to add at the end of the output stacks.
# `metalcolumn` specifies the panel column that contains the metal tags.
# 
# We will first generate the stack definition before calling the converter function.

# In[16]:


# Define stacks
list_analysis_stacks =[
    (ilastik_colname, suffix_ilastik),
    (full_colname, suffix_full)]

# Convert ome.tiffs to tiff stacks
ome2analysis.omefolder_to_analysisfolder(input_folder=folder_path_ome, 
                                         output_folder=folder_path_tiffs, 
                                         panel_csv_file=file_path_panel,
                                         analysis_stacks=(list_analysis_stacks), 
                                         metalcolumn=metal_colname)


# ### Export additional metadata
# 
# Finally, we will copy a file that contains the correct order of channels for the exported full stacks and ilastik stacks to the input folder.

# In[18]:


fn_full = next(folder_path_analysis.glob(f'*{suffix_full}.csv'))
fn_ilastik = next(folder_path_analysis.glob(f'*{suffix_ilastik}.csv'))

shutil.copy(fn_full, file_path_full_channels_csv)
shutil.copy(fn_ilastik, file_path_ilastik_channels_csv)


# We will also generate channel metadata for the probability stack.

# In[19]:


probab_meta = ["CellCenter", "CellBorder", "Background"]
with open(file_path_prob_channels_csv, 'w') as f:
    f.write('\n'.join(probab_meta))


# This concludes the pre-processing of the raw image files. In [the next step](https://bodenmillergroup.github.io/ImcSegmentationPipeline/ilastik.html), we will prepare the images for ilastik pixel classification.

# ## Generate the histocat folder with masks
# 
# This function can be used to convert the `.ome.tiff` files together with the mask files, which are generated in the [segmentation step](https://bodenmillergroup.github.io/ImcSegmentationPipeline/cellprofiler.html) to a format that is recognized by the `histoCAT` software.

# In[1]:


#suffix_mask = '_mask.tiff'
#for fol in folder_path_ome.glob('*'):
#    ome2histocat.omefolder_to_histocatfolder(fol, folder_path_histocat,
#                                    mask_folder=folder_path_analysis, mask_suffix=suffix_mask, dtype='uint16')

