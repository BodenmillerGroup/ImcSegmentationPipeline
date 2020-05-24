import re
import pathlib
import os
import shutil


### Varia
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

### Dynamic output helpers

def get_plugins(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['plugins']

def get_pipeline(wildcards):
    return CONFIG_BATCHRUNS[wildcards.batchname]['pipeline']

### Cellprofiler helpers

def get_chunks(lenght, chunk_size):
    """
    Given a lenght, split the range into chunks of chunk_size
    """

    chunks = list(range(1, lenght + 1, chunk_size))
    chunks.append(lenght + 1)
    for i in range(0, len(chunks) - 1):
        yield (chunks[i], chunks[i + 1] - 1)


def _copy_cp_file(path_source, fol_source, fol_target):
    """
    Copies a file from a source folder in a target folder, preserving the subfolder
    structure.
    If the file exists already, it is not overwritten but a warning is printed.
    If the file exists already and is a .csv file, it will be appended to the existing .csv
    without header

    Input:
        path_source: the full path to the source file
        fol_source: the base folder of the source file
        fol_target: the target folder
    Output:
        True: if copied/appended
        False: if not copied
    """
    CSV_SUFFIX = '.csv'

    fn_source_rel = os.path.relpath(path_source, fol_source)
    path_target = os.path.join(fol_target, fn_source_rel)
    if os.path.exists(path_target):
        if path_source.endswith(CSV_SUFFIX):
            with open(path_target, 'ab') as outfile:
                with open(path_source, 'rb') as infile:
                    infile.readline()  # Throw away header on all but first file
                    # Block copy rest of file from input to output without parsing
                    shutil.copyfileobj(infile, outfile)
                    print(path_source + " has been appended.")
            return True
        else:
            print('File: ', path_target, 'present in multiple outputs!')
            return False
    else:
        subfol = os.path.dirname(path_target)
        if not os.path.exists(subfol):
            # create the subfolder if it does not yet exist
            os.makedirs(os.path.dirname(path_target))
        shutil.copy(path_source, path_target)
        return True


def combine_cp_directories(fols_input, fol_out):
    """
    Combines a list of cellprofiler ouput directories into one output
    folder.
    This .csv files present in multiple output directories are appended
    to each other, ignoring the header. Other files present in multiple directories
    are only copied once.
    Input:
        fols_input: list of cp ouput folders
        fol_out: folder to recombine the output folders into
    """
    for d_root in fols_input:
        for dp, dn, filenames in os.walk(d_root):
            for f in filenames:
                _copy_cp_file(path_source=os.path.join(dp, f), fol_source=d_root, fol_target=fol_out)
