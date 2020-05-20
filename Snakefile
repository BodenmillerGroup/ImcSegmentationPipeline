import urllib.request
import os
import pathlib

from imctools.converters import ome2analysis
from imctools.converters import ome2histocat
from imctools.converters import mcdfolder2imcfolder
from imctools.converters import exportacquisitioncsv


# the folders with the ziped acquisition files for the analysis
folders = ['example_data']
fol_example = folders[0] 
# part that all considered files need to have in common
file_regexp = '{zipfol}.zip'

# output for OME tiffs
folder_base = '/home/vitoz/Data/Analysis/2020_cp_segmentation_example_sm'


# pannel
csv_pannel = '../config/example_pannel.csv'
csv_pannel_metal = 'Metal Tag'
csv_pannel_ilastik = 'ilastik'
csv_pannel_full = 'full'

# parameters for resizing the images for ilastik

folder_analysis = os.path.join(folder_base, 'tiffs')
folder_ilastik = os.path.join(folder_base, 'ilastik')
folder_ome = os.path.join(folder_base, 'ometiff')
folder_tmp = os.path.join(folder_base, 'tmp')
folder_cp = os.path.join(folder_base, 'cpout')
folder_histocat = os.path.join(folder_base, 'histocat')
folder_uncertainty = os.path.join(folder_base, 'uncertainty')

suffix_full = '_full'
suffix_ilastik = '_ilastik'
suffix_ilastik_scale = '_s2'
suffix_mask = '_mask.tiff'
suffix_probablities = '_Probabilities'


failed_images = list()

urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
       ('20170906_FluidigmONfinal_SE.zip',
        'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]

rule all:
    input: dynamic(os.path.join(folder_ome , '{omefile}.ome.tiff'))
    
rule download:
    output: dynamic(os.path.join(folders[0], '{zipfol}.zip'))
    run:
        for fn, url in urls:
            fn = os.path.join(fol_example, fn)
            if os.path.exists(fn) == False:
                urllib.request.urlretrieve(url, fn)
                
rule mcdfolder2imcfolder:
    input: os.path.join(folders[0], '{zipfol}.zip')
    output: os.path.join(folder_base, '{zipfol}.txt')
    
    run:
        print(input)
        mcdfolder2imcfolder.mcdfolder_to_imcfolder(
            input[0], output_folder=folder_tmp, 
            create_zip=False)
        Path(output[0]).touch()

rule listimcfiles:
    input: dynamic(os.path.join(folder_base, '{zipfol}.txt'))
    output: dynamic(os.path.join(folder_ome , '{omefile}.ome.tiff'))
    
    shell:
        'mv {folder_tmp}/* {folder_ome}' 
        
rule clean:
    shell:
        "rm -R {folder_base}"
