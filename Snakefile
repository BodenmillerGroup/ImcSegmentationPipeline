import urllib.request
import os
import pathlib
from imctools.converters import ome2analysis
from imctools.converters import ome2histocat
from imctools.converters import mcdfolder2imcfolder
from imctools.converters import exportacquisitioncsv
import json
import shutil

from helpers import *


# the folders with the ziped acquisition files for the analysis
folders = ['example_data']
fol_example = folders[0] 
# part that all considered files need to have in common
file_regexp = '.*.zip'

# output for OME tiffs
folder_base = os.path.abspath('./data')


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
suffix_tiff = '.tiff'
suffix_h5 = '.h5'

SUFFIX_DONE = '.done'

FN_ACMETA = os.path.join(folder_cp, 'acquisition_metadata.csv')
FOL_OME = os.path.join(folder_ome, '{omefol}/',)
BASENAME_OME = '{omefol}_{omefile, s[0-9]+_a[0-9]+_ac}'
FN_OME = os.path.join(FOL_OME, BASENAME_OME+'.ome.tiff')
FN_MCDPARSE_DONE = os.path.join(folder_base, 'zips','{zipfol}' + SUFFIX_DONE)
FN_FULL = os.path.join(folder_analysis, BASENAME_OME + '_full.tiff')
FN_ILASTIK = os.path.join(folder_analysis, BASENAME_OME + '_ilastik.tiff')
FN_ILASTIK_SCALED = os.path.join(folder_analysis, BASENAME_OME +'_ilastik_s2'+suffix_h5)

FOL_PLUGINS = 'data/batch_{batchname}/plugins'

CONFIG_BATCHRUNS = {
    'prepilastik': {
        'batchsize': 3,
        'plugins': '/home/vitoz/Git/ImcPluginsCP/plugins',
        'pipeline': 'cp3_pipelines/1_prepare_ilastik.cppipe'
    }
}


failed_images = list()

urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
       ('20170906_FluidigmONfinal_SE.zip',
        'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]





### Dynamic output helpers functions
def get_plugins(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['plugins']

def get_pipeline(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['pipeline']

def get_fns_ome_fkt(files_zip):
    def get_fns_ome(wildcards=None):
        for fn in files_zip.keys():
            cpout = checkpoints.mcdfolder2imcfolder.get(zipfol=fn).output
        fns = [str(p) for p in  get_filenames_by_re([folder_ome], '.*.ome.tiff').values()]
        return fns
    return get_fns_ome

def get_fns_analysis_fkt(files_zip, folder, suffix):
    def get_fns_analysis(wildcards):
        fns = []
        for fn in get_fns_ome_fkt(files_zip)(None):
            base_fn = pathlib.Path(fn).name[:-len('.ome.tiff')]
            fns.append(str(pathlib.Path(folder) / f'{base_fn}{suffix}'))
        return fns
    return get_fns_analysis



dict_zip_fns = get_filenames_by_re(folders, file_regexp)
FNS_OME = get_fns_ome_fkt(dict_zip_fns)
FNS_FULL = get_fns_analysis_fkt(dict_zip_fns, folder_analysis, suffix_full + suffix_tiff)
FNS_ILASTIK = get_fns_analysis_fkt(dict_zip_fns, folder_analysis, suffix_ilastik + suffix_tiff)
FNS_ILASTIK_SCALED = get_fns_analysis_fkt(dict_zip_fns, folder_analysis, suffix_ilastik + suffix_ilastik_scale + suffix_h5)

# Start rules

rule all:
    input: FNS_OME, FNS_FULL, FNS_ILASTIK, FNS_ILASTIK_SCALED

rule files_ilastik_scaled:
    input: FNS_ILASTIK_SCALED

rule files_ilastik:
    input: FNS_ILASTIK

rule files_ome:
    input: FNS_OME

checkpoint mcdfolder2imcfolder:
    output: touch(FN_MCDPARSE_DONE)
    run:
        # TODO: add asserts to not overwrite
        mcdfolder2imcfolder.mcdfolder_to_imcfolder(
	        str(dict_zip_fns[wildcards.zipfol]), output_folder=folder_ome,
            create_zip=False)

rule ome2full:
    input:
        image=FN_OME,
        panel=csv_pannel
    output:
        FN_FULL
    params:
        outname = BASENAME_OME + suffix_full
    run:
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                basename=params.outname, panel_csv_file=input.panel,
                metalcolumn=csv_pannel_metal, usedcolumn=csv_pannel_full, dtype='uint16')

rule ome2ilastik:
    input:
        image=FN_OME,
        panel=csv_pannel
    output:
        FN_ILASTIK
    params:
          outname = BASENAME_OME + suffix_ilastik
    run:
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                basename=params.outname, panel_csv_file=input.panel,
                metalcolumn=csv_pannel_metal, usedcolumn=csv_pannel_ilastik, dtype='uint16')

# Define the Cellprofiler run
rule cp_prepare_ilastik_input:
    input:  FNS_ILASTIK
    output: 'data/batch_prepilastik/filelist.txt'
    message: 'Define CP pipeline input files'
    shell:
         'for f in {input}\n'
         '        do\n'
         '            echo $f >> {output}\n'
         '        done\n'

rule cp_prepare_ilastik_output:
    input:
        fol_combined='data/batch_prepilastik/combined'
    output:
        fn=FN_ILASTIK_SCALED
    message: 'Define CP pipeline output files'
    run:
        fn = pathlib.Path(output.fn).name
        shutil.copy(pathlib.Path(input.fol_combined) / fn, output.fn)

rule exportacmeta:
    input: FNS_OME
    output: FN_ACMETA
    run:
        exportacquisitioncsv.export_acquisition_csv(folder_ome, output_folder=folder_cp)


## Rules to enable Cellprofiler batch runs

rule cp_get_plugins:
    input: get_plugins
    output: directory(FOL_PLUGINS)
    shell:
        'mkdir -p {output} && '
        'cp -R {input}/* {output}'

rule cp_create_batch_data:
    input:
        filelist='data/batch_{batchname}/filelist.txt',
        pipeline=get_pipeline,
        plugins=FOL_PLUGINS
    output:
        batchfile='data/batch_{batchname}/Batch_data.h5'
    params:
        outfolder='data/batch_{batchname}',
    container:
        "docker://cellprofiler/cellprofiler:3.1.9"
    message: 'Prepares a batch file'
    shell:
        ("cellprofiler -c -r --file-list={input.filelist} --plugins-directory {input.plugins} "
        "-p {input.pipeline} -o {params.outfolder} || true")

rule cp_run_batch:
    input:
        batchfile='data/batch_{batchname}/Batch_data.h5',
        plugins=FOL_PLUGINS
    output:
        outfolder=directory('data/batch_{batchname}/run_{start}_{end}')
    container:
        "docker://cellprofiler/cellprofiler:3.1.9"
    threads:
        1
    shell:
        ("cellprofiler -c -r -p {input.batchfile} -f {wildcards.start} -l {wildcards.end}"
        " --do-not-write-schema --plugins-directory={input.plugins} -o {output.outfolder} || true")

checkpoint cp_get_groups:
    input: 'data/batch_{batchname}/Batch_data.h5'
    output: 'data/batch_{batchname}/result.json'
    message: 'Creates grouped output based on batch'
    container:
        "docker://cellprofiler/cellprofiler:3.1.9"
    shell:
        "cellprofiler -c --print-groups={input[0]}  > {output[0]} || true"

def get_cp_batch_groups(wildcards):
    """
    Todo: Adapt to respect grouping!
    :param wildcards:
    :return:
    """
    fn_grpfile = checkpoints.cp_get_groups.get(**wildcards).output[0]
    batchname = wildcards.batchname
    batchsize = CONFIG_BATCHRUNS[wildcards.batchname]['batchsize']
    # from gc3apps: https://github.com/BodenmillerGroup/gc3apps/blob/master/gc3apps/pipelines/gcp_pipeline.py
    with open(fn_grpfile) as json_file:
        data = json.load(json_file)
        total_size = len(data)
    fns_batch = []
    for start, end in get_chunks(total_size, batchsize):
        fns_batch.append(f'data/batch_{batchname}/run_{start}_{end}')
    return fns_batch

rule cp_combine_batch_output:
    input: get_cp_batch_groups  # function that retrieves all groups for a batch
    output: directory('data/batch_{batchname}/combined')
    run:
        combine_cp_directories(input, output[0])

### Varia

rule clean:
    shell:
        "rm -R {folder_base}"

rule download:
    run:
        for fn, url in urls:
            fn = os.path.join(fol_example, fn)
            if os.path.exists(fn) == False:
                urllib.request.urlretrieve(url, fn)
