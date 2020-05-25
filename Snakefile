import urllib.request
import pathlib
from imctools.converters import ome2analysis
from imctools.converters import ome2histocat
from imctools.converters import mcdfolder2imcfolder
from imctools.converters import exportacquisitioncsv
import json
from snakemake.io import regex, strip_wildcard_constraints

from helpers import *

### Config (should be changed)
# TODO: Add to configuration file and write configuration file schema

## Required
# Data input
input_data_folders = ['example_data']
input_file_regexp = '.*.zip'

# pannel
csv_panel = 'config/example_pannel.csv'
csv_panel_metal = 'Metal Tag'
csv_panel_ilastik = 'ilastik'
csv_panel_full = 'full'

## Optional
example_data_urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
                     ('20170906_FluidigmONfinal_SE.zip',
         'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]

### Variables (only adapt if pipeline is adapted)
# Example data folder
fol_example = pathlib.Path(input_data_folders[0])

# Define input_data_folders
folder_base = pathlib.Path('data')
folder_analysis = folder_base / 'tiffs'
folder_ilastik = folder_base / 'ilastik'
folder_ome = folder_base / 'ometiff'
folder_tmp = folder_base / 'tmp'
folder_cp = folder_base / 'cpout'
folder_histocat = folder_base / 'histocat'
folder_uncertainty = folder_base / 'uncertainty'
folder_crop = folder_base / 'crops'

# Define suffixes
suffix_full = '_full'
suffix_ilastik = '_ilastik'
suffix_scale = '_s2'
suffix_mask = '_mask'
suffix_probablities = '_Probabilities'
suffix_tiff = '.tiff'
suffix_h5 = '.h5'
suffix_done = '.done'
suffix_crop = '_{crop, x[0-9]+_y[0-9]+_w[0-9]+_h[0-9]+}'
basename_ome = '{omefol}_{omefile, s[0-9]+_a[0-9]+_ac}'

# Define derived file patterns
FOL_OME = folder_ome / '{omefol}'
FN_OME = FOL_OME / (basename_ome + '.ome.tiff')
FN_FULL = folder_analysis / (f'{basename_ome}{suffix_full}{suffix_tiff}')
FN_ILASTIK = folder_analysis / (f'{basename_ome}{suffix_ilastik}{suffix_tiff}')
FN_ILASTIK_SCALED = folder_analysis / (f'{basename_ome}{suffix_ilastik}{suffix_scale}{suffix_h5}')
FN_ILASTIK_CROP = folder_crop / '{batchname}' / (f'{basename_ome}{suffix_ilastik}{suffix_scale}{suffix_crop}{suffix_h5}')

FN_ACMETA = folder_cp / 'acquisition_metadata.csv'
FN_MCDPARSE_DONE = folder_base / 'zips' / ('{zipfol}' + suffix_done)

FOL_PLUGINS = 'data/batch_{batchname}/plugins'


### Dynamic output helpers functions
def get_plugins(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['plugins']

def get_pipeline(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['pipeline']

def get_fns_ome_fkt(files_zip):
    def fkt(wildcards):
        checkpoints.all_mcd_converted.get()
        fns = [str(p) for p in  get_filenames_by_re([folder_ome], '.*.ome.tiff').values()]
        return fns
    return fkt

dict_zip_fns = get_filenames_by_re(input_data_folders, input_file_regexp)
FNS_OME = get_fns_ome_fkt(dict_zip_fns)
FNS_FULL = get_derived_input_fkt(FNS_OME, FN_OME, FN_FULL)
FNS_ILASTIK = get_derived_input_fkt(FNS_OME, FN_OME, FN_ILASTIK)
FNS_ILASTIK_SCALED = get_derived_input_fkt(FNS_OME, FN_OME, FN_ILASTIK_SCALED)

def get_fns_crop_fkt(batchname):
    def fkt(wildcards):
        fol_out = checkpoints.cp_combine_batch_output.get(batchname=batchname).output[0]
        fol_out = pathlib.Path(fol_out)
        pat_name = FN_ILASTIK_CROP.name
        pat = fol_out / pat_name

        fkt_cropfol = get_derived_input_fkt(FNS_OME, FN_OME, pat, extra_wildcards={'batchname': batchname})
        fkt_target = get_derived_input_fkt(FNS_OME, FN_OME, FN_ILASTIK_CROP, extra_wildcards={'batchname': batchname})
        fns_out = []
        for fn_crop, fn_target in zip(fkt_cropfol(wildcards), fkt_target(wildcards)):
            wcs = glob_wildcards(fn_crop)
            fns_out.append(expand(fn_target, crop=wcs.crop)[0])
        print(fns_out)
        return fns_out
    return fkt

FNS_ILASTIK_CROP = get_fns_crop_fkt('prepilastik')


CONFIG_BATCHRUNS = {
    'prepilastik': {
        'batchsize': 3,
        'plugins': '/home/vitoz/Git/ImcPluginsCP/plugins',
        'pipeline': 'cp3_pipelines/1_prepare_ilastik.cppipe',
        'input_files': (FNS_ILASTIK, FNS_FULL),
        'output_files': [FN_ILASTIK_SCALED, FN_ILASTIK_CROP],
        'output_script': #'mkdir -p  $(dirname {output}) && '
            'cp {input}/$(basename {output}) $(dirname {output})'

    }
}
# Target rules
rule all:
    input: FNS_OME, FNS_FULL, FNS_ILASTIK, FNS_ILASTIK_SCALED

rule files_ilastik_scaled:
    input: FNS_ILASTIK_SCALED

rule files_ilastik:
    input: FNS_ILASTIK

rule files_ome:
    input: FNS_OME

rule files_crops:
    input: FNS_ILASTIK_CROP

# MCD to ome conversion
rule mcdfolder2imcfolder:
    output: touch(FN_MCDPARSE_DONE)
    threads: 1
    run:
        # TODO: add asserts to not overwrite
        mcdfolder2imcfolder.mcdfolder_to_imcfolder(
	        str(dict_zip_fns[wildcards.zipfol]), output_folder=folder_ome,
            create_zip=False)

checkpoint all_mcd_converted:
    input: expand(str(FN_MCDPARSE_DONE), zipfol=dict_zip_fns.keys())
    output:
        touch('data/all_mcd_converted.done')

# OME to analysis tiff conversion
rule ome2full:
    input:
        image=FN_OME,
        panel=csv_panel
    output:
        FN_FULL
    params:
        outname =basename_ome + suffix_full
    threads: 1
    run:
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                                              basename=params.outname, panel_csv_file=input.panel,
                                              metalcolumn=csv_panel_metal, usedcolumn=csv_panel_full, dtype='uint16')

rule ome2ilastik:
    input:
        image=FN_OME,
        panel=csv_panel
    output:
        FN_ILASTIK
    params:
          outname =basename_ome + suffix_ilastik
    threads: 1
    run:
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                                              basename=params.outname, panel_csv_file=input.panel,
                                              metalcolumn=csv_panel_metal, usedcolumn=csv_panel_ilastik, dtype='uint16')

# rule
rule prepare_cell_classifier:
    input:
        FNS_ILASTIK_CROP
    output:
        'classifiers/cell_untrained.ilp'

rule exportacmeta:
    input: FNS_OME
    output: FN_ACMETA
    run:
        exportacquisitioncsv.export_acquisition_csv(folder_ome, output_folder=folder_cp)


## Rules to target Cellprofiler batch runs
# Define the Cellprofiler run
for batchname, cp_config in CONFIG_BATCHRUNS.items():
    rule:
        input:  *cp_config['input_files']
        output: expand('data/batch_{batchname}/filelist.txt', batchname=batchname)
        shell:
            'for f in {input}\n'
            '        do\n'
            '            echo $(realpath $f) >> {output}\n'
            '        done\n'

    for i, outfile in enumerate(cp_config['output_files']):
        rule:
            input:
                 fol_combined=expand('data/batch_{batchname}/combined', batchname=batchname)
            output: outfile
            message: 'Define CP pipeline output files'
            threads: 1
            shell:
                 cp_config['output_script']

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
    threads: 1
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

checkpoint cp_combine_batch_output:
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
        for fn, url in example_data_urls:
            fn = fol_example / fn
            if ~fn.exists():
                urllib.request.urlretrieve(url, fn)
