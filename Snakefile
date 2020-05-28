import urllib.request
import pathlib
from imctools.converters import ome2analysis
from imctools.converters import ome2histocat
from imctools.converters import mcdfolder2imcfolder
from imctools.converters import exportacquisitioncsv

from scripts import helpers as hpr
from snakemake.utils import validate

# Cellprofiler/Ilastik rules
include: 'rules/cellprofiler.smk'
include: 'rules/ilastik.smk'

# Read Configuration
configfile: 'config/config_pipeline.yml'
validate(config, "config/config_pipeline.schema.yml")

# Extract variables from configuration
## Input/output
input_data_folders = config['input_data_folders']
input_file_regexp = config['input_file_regexp']

folder_base = pathlib.Path(config['output_folder'])

fn_cell_classifier = config['fn_cell_classifier']

# Optional example data folder
fol_example = pathlib.Path(input_data_folders[0])

## Panel
csv_panel = config['csv_panel']
csv_panel_metal = config['csv_panel_metal']
csv_panel_ilastik = config['csv_panel_ilastik']
csv_panel_full = config['csv_panel_full']

## Ilastik run config
ilastik_threads = config['ilastik_threads']
ilastik_mem_mb = config['ilastik_mem_mb']

# Cellprofiler default config
cp_plugins = config['cellprofiler_plugins']
# Define hardcoded variables
## Define basic folder structrue
folder_analysis = folder_base / 'tiffs'
folder_ilastik = folder_base / 'ilastik'
folder_ome = folder_base / 'ometiff'
folder_tmp = folder_base / 'tmp'
folder_cp = folder_base / 'cpout'
folder_histocat = folder_base / 'histocat'
folder_uncertainty = folder_base / 'uncertainty'
folder_crop = folder_base / 'ilastik_training_data'
folder_classifiers = folder_base / 'classifiers'

## Define Output files
fn_image = folder_cp / 'Image.csv'
fn_cell = folder_cp / 'cell.csv'
fn_experiment = folder_cp / 'Experiment.csv'
fn_object_rel = folder_cp / 'Object relationships.csv'
fn_cell_class_ut = folder_classifiers / 'cell_untrained.ilp'
fn_acmeta = folder_cp / 'acquisition_metadata.csv'
# Identify a dictionary of input folders/zips containing .mcd files to process
dict_zip_fns = hpr.get_filenames_by_re(input_data_folders, input_file_regexp)
# Produce a list of all cellprofiler output files
cp_meas_output = [fn_image, fn_cell, fn_experiment, fn_object_rel]


## Define suffixes
suffix_full = '_full'
suffix_ilastik = '_ilastik'
suffix_scale = '_s2'
suffix_mask = '_mask'
suffix_probablities = '_Probabilities'
suffix_tiff = '.tiff'
suffix_h5 = '.h5'
suffix_done = '.done'
suffix_crop = '_{crop, x[0-9]+_y[0-9]+_w[0-9]+_h[0-9]+}'

## Define derived file patterns
pat_basename_image = '{img_session}_{img_acquisition, s[0-9]+_a[0-9]+_ac}'
pat_fol_ome = folder_ome / '{img_session}'
pat_fn_ome = pat_fol_ome / (pat_basename_image + '.ome.tiff')
pat_fn_full = folder_analysis / (f'{pat_basename_image}{suffix_full}{suffix_tiff}')
pat_fn_ilastik = folder_analysis / (f'{pat_basename_image}{suffix_ilastik}{suffix_tiff}')
pat_fn_ilastik_scaled = folder_analysis / (f'{pat_basename_image}{suffix_ilastik}{suffix_scale}{suffix_h5}')
pat_fn_ilastik_crop = folder_crop / '{batchname}' / (f'{pat_basename_image}{suffix_ilastik}{suffix_scale}{suffix_crop}{suffix_h5}')
pat_fn_cell_probabilities = folder_analysis / (f'{pat_basename_image}{suffix_ilastik}{suffix_scale}{suffix_probablities}{suffix_tiff}')
pat_fn_mask= folder_analysis / (f'{pat_basename_image}{suffix_ilastik}{suffix_scale}{suffix_probablities}{suffix_mask}{suffix_tiff}')
pat_fn_mask_cpout= folder_cp / (f'{pat_basename_image}{suffix_ilastik}{suffix_scale}{suffix_probablities}{suffix_mask}{suffix_tiff}')
pat_fn_mcdparse_done = folder_base / 'zips' / ('{zipfol}' + suffix_done)

# Define dynamic files
## Define (dynamic) input file functions
def fkt_fns_ome(wildcards):
    """
    Generates dynamically a list of .ome.tiff files once the `all_mcd_converted` checkpoint
    is finished.
    :param wildcards: wildcards dynamically provided by snakemake
    :return: A list of all `.ome.tiffs` generated.
    """
    checkpoints.all_mcd_converted.get()
    fns = [str(p) for p in  hpr.get_filenames_by_re([folder_ome], '.*.ome.tiff').values()]
    return fns


## Define derived (dynamic) input files functions
## This generates functions to define input filenames based on other input filename functions
fkt_fns_full = hpr.get_derived_input_fkt(fkt_fns_ome, pat_fn_ome, pat_fn_full)
fkt_fns_ilastik = hpr.get_derived_input_fkt(fkt_fns_ome, pat_fn_ome, pat_fn_ilastik)
fkt_fns_ilastik_scaled = hpr.get_derived_input_fkt(fkt_fns_ilastik, pat_fn_ilastik,
                                                   pat_fn_ilastik_scaled)
fkt_fns_cell_probabilities = hpr.get_derived_input_fkt(fkt_fns_ome, pat_fn_ome,
                                                       pat_fn_cell_probabilities)
fkt_fns_mask = hpr.get_derived_input_fkt(fkt_fns_ome, pat_fn_ome, pat_fn_mask)
fkt_fns_mask_cpout = hpr.get_derived_input_fkt(fkt_fns_ome, pat_fn_ome, pat_fn_mask_cpout)


def get_fkt_fns_crop(batchname):
    def fkt(wildcards):
        fol_out = checkpoints.cp_combine_batch_output.get(batchname=batchname).output[0]
        fol_out = pathlib.Path(fol_out)
        pat_name = pat_fn_ilastik_crop.name
        pat = fol_out / pat_name

        fkt_cropfol = hpr.get_derived_input_fkt(fkt_fns_ome, pat_fn_ome, pat, extra_wildcards={'batchname': batchname})
        fkt_target = hpr.get_derived_input_fkt(fkt_fns_ome, pat_fn_ome, pat_fn_ilastik_crop, extra_wildcards={'batchname': batchname})
        fns_out = []
        for fn_crop, fn_target in zip(fkt_cropfol(wildcards), fkt_target(wildcards)):
            wcs = glob_wildcards(fn_crop)
            fns_out.append(expand(fn_target, crop=wcs.crop)[0])
        return fns_out
    return fkt

fkt_fns_ilastik_crop = get_fkt_fns_crop('prepilastik')

# Configuration for cellprofiler pipeline steps
# (Please look at rules/cellprofiler.smk for the documentation of this structure)
config_dict_cp = {
    'prepilastik': {
        'run_size': 3,
        'plugins': cp_plugins,
        'pipeline': 'cp3_pipelines/1_prepare_ilastik.cppipe',
        'input_files': [fkt_fns_ilastik],
        'output_patterns': [pat_fn_ilastik_scaled, pat_fn_ilastik_crop],
    },
    'segmasks': {
        'run_size': 2,
        'plugins': cp_plugins,
        'pipeline': 'cp3_pipelines/2_segment_ilastik.cppipe',
        'input_files': [fkt_fns_cell_probabilities],
        'output_patterns': [pat_fn_mask],
    },
    'measuremasks': {
        'run_size': 2,
        'plugins': cp_plugins,
        'pipeline': 'cp3_pipelines/3_measure_mask_basic.cppipe',
        'input_files': [fkt_fns_mask, fkt_fns_full, fkt_fns_cell_probabilities],
        'output_patterns': cp_meas_output + [pat_fn_mask_cpout],
    }
}

# Configuration for Ilastik steps
# (Please look at rules/cellprofiler.smk for the documentation of this structure)
config_dict_ilastik = {
    'cell':
        {'project': fn_cell_classifier,
         'run_size': 5,
         'output_format': 'tiff',
         'output_filename': f'{{nickname}}{suffix_probablities}{suffix_tiff}',
         'export_source': 'Probabilities',
         'export_dtype': 'uint16',
         'pipeline_result_drange': '"(0.0, 1.0)"',
         'input_files': fkt_fns_ilastik_scaled,
         'output_pattern': pat_fn_cell_probabilities
         }
}
# Target rules
rule all:
    input: fkt_fns_ome, fkt_fns_full, fkt_fns_ilastik, fkt_fns_ilastik_scaled, fkt_fns_cell_probabilities, fkt_fns_mask, \
         cp_meas_output, fkt_fns_mask_cpout, fkt_fns_ilastik_crop

rule cell_probabilities:
    input: fkt_fns_cell_probabilities

rule prep_cell_classifier:
    input: fkt_fns_ilastik_crop

rule files_ilastik_scaled:
    input: fkt_fns_ilastik_scaled

rule files_ilastik:
    input: fkt_fns_ilastik

rule files_ome:
    input: fkt_fns_ome

rule files_crops:
    input: fkt_fns_ilastik_crop


# MCD to ome conversion
rule mcdfolder2imcfolder:
    output: touch(pat_fn_mcdparse_done)
    threads: 1
    run:
        mcdfolder2imcfolder.mcdfolder_to_imcfolder(
	        str(dict_zip_fns[wildcards.zipfol]), output_folder=folder_ome,
            create_zip=False)

checkpoint all_mcd_converted:
    input: expand(str(pat_fn_mcdparse_done), zipfol=dict_zip_fns.keys())
    output:
        touch('data/all_mcd_converted.done')


# OME to analysis tiff conversion
rule ome2full:
    input:
        image = pat_fn_ome,
         panel = csv_panel
    output:
        pat_fn_full
    params:
        outname =pat_basename_image + suffix_full
    threads: 1
    run:
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                                              basename=params.outname, panel_csv_file=input.panel,
                                              metalcolumn=csv_panel_metal, usedcolumn=csv_panel_full, dtype='uint16')

rule ome2ilastik:
    input:
        image = pat_fn_ome,
         panel = csv_panel
    output:
        pat_fn_ilastik
    params:
          outname =pat_basename_image + suffix_ilastik
    threads: 1
    run:
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                                              basename=params.outname, panel_csv_file=input.panel,
                                              metalcolumn=csv_panel_metal, usedcolumn=csv_panel_ilastik, dtype='uint16')

# rule
rule prepare_cell_classifier:
    input:
        fkt_fns_ilastik_crop

rule exportacmeta:
    input: fkt_fns_ome
    output: fn_acmeta
    run:
        exportacquisitioncsv.export_acquisition_csv(folder_ome, output_folder=folder_cp)


## Rules to target Cellprofiler batch runs
define_cellprofiler_rules(config_dict_cp, folder_base)
define_ilastik_rules(config_dict_ilastik, folder_base, threads=ilastik_threads,
                     mem_mb=ilastik_mem_mb)

### Varia

rule clean:
    shell:
        "rm -R {folder_base}"

rule download_example_data:
    run:
        fol_example.mkdir(parents=True, exist_ok=True)
        for fn, url in config['example_data_urls']:
            fn = fol_example / fn
            if ~fn.exists():
                urllib.request.urlretrieve(url, fn)
