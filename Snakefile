import urllib.request
import os
import pathlib
from imctools.converters import ome2analysis
from imctools.converters import ome2histocat
from imctools.converters import mcdfolder2imcfolder
from imctools.converters import exportacquisitioncsv
import re
import json
import pandas as pd
import shutil
import glob



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
suffix_tiff = '.tiff'

SUFFIX_DONE = '.done'

FN_ACMETA = os.path.join(folder_cp, 'acquisition_metadata.csv')
FOL_OME = os.path.join(folder_ome, '{omefol}/',)
BASENAME_OME = '{omefol}_{omefile, s[0-9]+_a[0-9]+_ac}'
FN_OME = os.path.join(FOL_OME, BASENAME_OME+'.ome.tiff')
FN_MCDPARSE_DONE = os.path.join(folder_base, '{zipfol}' + SUFFIX_DONE)
FN_FULL = os.path.join(folder_analysis, BASENAME_OME + '_full.tiff')
FN_ILASTIK = os.path.join(folder_analysis, BASENAME_OME + '_ilastik.tiff')
FN_ILASTIK_SCALED = os.path.join(folder_analysis, BASENAME_OME +'_ilastik_s2.tiff')

CONFIG_BATCHRUNS = {
    'prepilastik': {
        'batchsize': 10,
        'plugins': '/home/vitoz/Git/ImcPluginsCP/plugins',
        'fns_fkt': lambda dynamic_fns: [fn for k in ['ilastik'] for fn in dynamic_fns[k](None)],
        'pipeline': 'cp3_pipelines/1_prepare_ilastik.cppipe'
    }
}


failed_images = list()

urls = [('20170905_Fluidigmworkshopfinal_SEAJa.zip',
         'https://www.dropbox.com/s/awyq9p7n7dexgyt/20170905_Fluidigmworkshopfinal_SEAJa.zip?dl=1') ,
       ('20170906_FluidigmONfinal_SE.zip',
        'https://www.dropbox.com/s/0pdt1ke4b07v7zd/20170906_FluidigmONfinal_SE.zip?dl=1')]

def get_filenames_by_re(folders, fn_regexp):
    """
    Retrieve all files matching the re.Path
    Args:
        folders: an iterable of folders
        fn_regexp: a regular expression to identify valid files
    Returns:
        Dict with key=Filename and values=Folders
    """
    fns = {}
    re_fn = re.compile(fn_regexp)
    for fol in folders:
        for file in pathlib.Path(fol).rglob('*'):
            if re_fn.match(file.name):
                fns[file.name] = file
    return fns

def __group_by_limit(li, limit):
    """
    Helper:
    Concatenates consecutive sublists of a list
    until a size limit has been reached
    """
    if not li:
        return []
    out = [[]]
    for sublist in li:
        if len(out[-1]) < limit:
            out[-1].extend(sublist)
        else:
            out.append(sublist[:])

    # check for the last element length
    if len(out) > 1 and len(out[-1]) < limit:
        out[-2].extend(out.pop())

    return out

def _get_chunks(data, chunk_size):
    """
    Get chunk of images based on the chunk_size
    """
    images_list = [element[1] for element in data]
    chunks_list = __group_by_limit(images_list, chunk_size)
    for chunk in chunks_list:
        yield(chunk[0],chunk[-1])
        
def __csv_handler(source, destination):
    """
    Checks for presence of csv files in the source dir.
    If found:
        - Copies/appends them to the destination dir
    Input:
        source: full path to the source dir
        destination: full path to the destination dir
    Output:
        True: if csv files are copied/appended
        False: if csv files not found
    """
    # Get all csv files in the source NOT recursively
    csv_files = glob.glob(os.path.join(source,'*.csv'))

    if csv_files:
        print("csv files found at '{0}'".format(source))
        for csv_file_source in csv_files:
            csv_file_dest = os.path.join(destination, os.path.basename(csv_file_source))
            if not os.path.exists(csv_file_dest):
                # copy source file to destination
                print("Copying '{0}' to '{1}'".format(csv_file_source, csv_file_dest))
                shutil.copy2(csv_file_source, csv_file_dest)
            else:
                # append source file to dest file
                data = pd.read_csv(csv_file_source)
                print("Appending content of '{0}' to '{1}'".format(csv_file_source, csv_file_dest))
                with open(csv_file_dest, 'a') as f:
                    data.to_csv(csv_file_dest, mode='a', header=f.tell()==0)
        return True
    return False


def _combine_cp_directory(source, destination):
    """
    Copies files from a source folder to destination folder, preserving the subfolder
    structure.
    If the file exists already, it is not overwritten but a warning is printed.
    """
    # check for csv files
    __csv_handler(source, destination)
    # Copy all data from source to destination
    shutil.copytree(source, destination)

fns_zip = get_filenames_by_re(folders, file_regexp)

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
        for fn in files_zip.keys():
            checkpoints.mcdfolder2imcfolder.get(zipfol=fn, **wildcards).output
        fns_ome = [str(p) for p in  get_filenames_by_re([folder_ome], '.*.ome.tiff').values()]
        for fn in fns_ome:
            print(fn)
            base_fn = pathlib.Path(fn).name[:-len('.ome.tiff')]
            fns.append(str(pathlib.Path(folder) / f'{base_fn}{suffix}'))
        print('b')
        return fns
    return get_fns_analysis

FNS_OME = get_fns_ome_fkt(fns_zip)
FNS_FULL = get_fns_analysis_fkt(fns_zip, folder_analysis, suffix_full+suffix_tiff)
FNS_ILASTIK = get_fns_analysis_fkt(fns_zip, folder_analysis, suffix_ilastik+suffix_tiff)
FNS_ILASTIK_SCALED = get_fns_analysis_fkt(fns_zip, folder_analysis, suffix_ilastik+suffix_ilastik_scale+suffix_tiff)

DYNAMIC_FNS = {
    'ome': FNS_OME,
    'full': FNS_FULL,
    'ilastik': FNS_ILASTIK,
    'ilastik_scaled': FNS_ILASTIK_SCALED
}

rule all:
    input: FNS_OME, FNS_FULL, FNS_ILASTIK

rule files_ilastik_scaled:
    input: FNS_OME, FNS_ILASTIK, FNS_ILASTIK_SCALED

rule files_ilastik:
    input: FNS_ILASTIK

rule files_ome:
    input: FNS_OME

checkpoint mcdfolder2imcfolder:
    output: touch(FN_MCDPARSE_DONE)
    run:
        # TODO: add asserts to not overwrite
        mcdfolder2imcfolder.mcdfolder_to_imcfolder(
	        str(fns_zip[wildcards.zipfol]), output_folder=folder_ome,
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
        print(params.outname)
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                basename=params.outname, panel_csv_file=input.panel,
                metalcolumn=csv_pannel_metal, usedcolumn=csv_pannel_full)

rule ome2ilastik:
    input:
        image=FN_OME,
        panel=csv_pannel
    output:
        FN_ILASTIK
    params:
          outname = BASENAME_OME + suffix_ilastik
    run:
        print(params.outname)
        ome2analysis.omefile_2_analysisfolder(input.image, output_folder=folder_analysis,
                basename=params.outname, panel_csv_file=input.panel,
                metalcolumn=csv_pannel_metal, usedcolumn=csv_pannel_ilastik)

rule prepare_ilastik:
    input: FN_ILASTIK, 'batch_prepilastik/combined'
    output: FN_ILASTIK_SCALED

#rule prepare_cpbatch:
#    input:
#        pipeline=fn_pipe
#    params:
#        plugins=fol_plugins
#    output:
#        cpbatch
#    shell:
#        'cellprofiler  -p {pipeline} -i {image_data} -w {cp_plugins} -d {docker_image}'
#

rule exportacmeta:
    input: FNS_OME
    output: FN_ACMETA
    run:
        exportacquisitioncsv.export_acquisition_csv(folder_ome, output_folder=folder_cp)

### Batch run
def get_plugins(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['plugins']

def get_batch_files(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['fns_fkt'](DYNAMIC_FNS)

def get_pipeline(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['pipeline']

rule create_filelist:
    input: FNS_ILASTIK, FNS_FULL
    output: 'batch_prepilastik/filelist.txt'
    run:
        # write filenames into a txt file
        print(input)
        with open(output[0], 'w') as f:
            for fn in input:
                f.write(fn)

rule create_batch:
    input:
        filelist='batch_{batchname}/filelist.txt',
        pipeline=get_pipeline,
        plugins=get_plugins
    output:
        batchfile='batch_{batchname}/Batch_data.h5'
    params:
        outfolder='batch_{batchname}'
    container:
        "docker://cellprofiler/cellprofiler:3.1.9"
    message: 'Prepares a batch file'
    shell:
        "cellprofiler -c -r --file-list={input.filelist} --plugins-directory {input.plugins} -p {input.pipeline} -o {params.outfolder}"

rule run_batchgroup:
    input:
        batchfile='batch_{batchname}/Batch_data.h5',
        plugins=get_plugins
    output:
        outfolder=temporary(directory('batch_{batchname}/run_{start}_{end}'))
    container:
        "docker://cellprofiler/cellprofiler:3.1.9"
    shell:
        "cellprofiler -c -r -p {input.batchfile} -f {wildcards.start} -l {wildcards.end} --do-not-write-schema --plugins-directory={input.plugins} -o {output.outfolder}"

checkpoint get_groups_from_batch:
    input: 'batch_{batchname}/Batch_data.h5'
    output: 'batch_{batchname}/result.json'
    message: 'Creates grouped output based on batch'
    container:
        "docker://cellprofiler/cellprofiler:3.1.9"
    shell:
        "cellprofiler -c --print-groups={input[0]}  > {output[0]}"

def get_batchgroups(wildcards):
    fn_grpfile = checkpoints.get_groups_from_batch.get(**wildcards).output[0]
    batchname = wildcards.batchname
    batchsize = CONFIG_BATCHRUNS[wildcards.batchname]['batchsize']
    # from gc3apps: https://github.com/BodenmillerGroup/gc3apps/blob/master/gc3apps/pipelines/gcp_pipeline.py
    with open(fn_grpfile) as json_file:
        data = json.load(json_file)
        fns_batch = []
        for start,end in _get_chunks(data, batchsize):
            fns_batch.append(f'batch_{batchname}/run_{start}_{end}')
    return fns_batch

rule combine_batch_output:
    input: get_batchgroups # function that retrieves all groups for a batch
    output: directory('batch_{batchname}/combined')
    

rule run_as_batch:
    input: 'fn_input_{pattern}', 'combined_{batchname}'
    output: 'fn_ouptut_{pattern}'



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
