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
file_regexp = '.*.zip'

# output for OME tiffs
folder_base = '/home/vitoz/Data/Analysis/2020_cp_segmentation_example_sm'


# pannel
csv_pannel = 'config/example_pannel.csv'
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


FN_ACMETA = os.path.join(folder_cp, 'acquisition_metadata.csv')
OUTFOLS_OME = os.path.join(folder_ome,'{omefile}.ome.tiff')
OUTFN_ZIP = os.path.join(folder_base, '{zipfol}.txt')
FN_FULL = os.path.join(folder_analysis, '{omefile}_full.tiff')
FN_ILASTIK = os.path.join(folder_analysis, '{omefile}_ilastik.tiff')
FN_ILASTIK_SCALED = os.path.join(folder_analysis, '{omefile}_ilastik_s2.tiff')


failed_images = list()

urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
       ('20170906_FluidigmONfinal_SE.zip',
        'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]

re_fn = re.compile(file_regexp)
fns_zip = {}
for fol in folders:
   for fn in os.listdir(fol):
       if re_fn.match(fn): 
           fns_zip[fn[:-4]] = fol

rule all:
    input: dynamic(OUTFOLS_OME), dynamic(FN_FULL), dynamic(FN_ILASTIK)

rule prepare_cp:
    input: dynamic(FN_FULL), dynamic(FN_ILASTIK)

rule prepare_ome:
    input: dynamic(OUTFOLS_OME)
    

rule listzips:
    output: '{zipfol}.zip'
    run:
       for f in fns_zip.keys():
           Path(f + '.zip').touch()
                
rule mcdfolder2imcfolder:
    input: '{zipfol}.zip'
    output: OUTFN_ZIP 
    
    run:
        mcdfolder2imcfolder.mcdfolder_to_imcfolder(
	    os.path.join(fns_zip[wildcards.zipfol], input[0]), output_folder=folder_tmp, 
            create_zip=False)
        Path(output[0]).touch()

rule listimcfiles:
    input: expand(OUTFN_ZIP, zipfol=fns_zip.keys())
    output: dynamic(OUTFOLS_OME)
    #'mv {folder_tmp}/* {folder_ome} && echo 1' 
    shell:
        'find {folder_tmp} -type f -print0 | xargs -0 mv -t {folder_ome}'

rule ome2full:
    input:
        image=OUTFOLS_OME,
        panel=csv_pannel
    output:
        FN_FULL
    run:
        outname=wildcards.omefile+suffix_full
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                basename=outname, panel_csv_file=input.panel,
                metalcolumn=csv_pannel_metal, usedcolumn=csv_pannel_full)

rule ome2ilastik:
    input:
        image=OUTFOLS_OME,
        panel=csv_pannel
    output:
        FN_ILASTIK
    run:
        outname=wildcards.omefile+suffix_ilastik
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                basename=outname, panel_csv_file=input.panel,
                metalcolumn=csv_pannel_metal, usedcolumn=csv_pannel_ilastik)

rule exportacmeta:
    input: dynamic(OUTFOLS_OME)
    output: FN_ACMETA
    run:
        print(1)
        exportacquisitioncsv.export_acquisition_csv(folder_ome, output_folder=folder_cp)
        
rule clean:
    shell:
        "rm -R {folder_base}"

rule download:
    run:
        for fn, url in urls:
            fn = os.path.join(fol_example, fn)
            if os.path.exists(fn) == False:
                urllib.request.urlretrieve(url, fn)
