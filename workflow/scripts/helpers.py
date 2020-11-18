import re
import pathlib
import os
import shutil
from snakemake.io import regex, strip_wildcard_constraints, expand
import filecmp


### Varia
def get_filenames_by_re(folders, fn_regexp):
    """
    Retrieve all files matching the re.Path
    Args:
        folders: an iterable of input_data_folders
        fn_regexp: a regular expression to identify valid files
    Returns:
        Dict with key=Filename and values=Folders
    """
    fns = []
    re_fn = re.compile(fn_regexp)
    for fol in folders:
        for file in pathlib.Path(fol).rglob('*'):
            if re_fn.match(str(file)):
                fns.append(file)
    return fns


def get_derived_input_fkt(source_fkt, source_pattern, target_pattern, extra_wildcards=None):
    """
    Modify an input function to represent a new pattern.
    :param source_fkt: function to generate source filenames
    :param source_pattern: pattern to get wildcards from source filenames
    :param target_pattern: pattern to apply wildcards to target filenames
    :return: A function to generate filenames with the target pattern
    """
    if extra_wildcards is None:
        extra_wildcards = {}

    def get_fns_analysis(wildcards):
        fns = []
        re_fn = re.compile(regex(str(source_pattern)))
        for fn in source_fkt(wildcards):
            match = re.match(re_fn, fn).groupdict()
            pattern = strip_wildcard_constraints(str(target_pattern))
            fns.append(expand(pattern, **match, **extra_wildcards, allow_missing=True)[0])
        return fns

    return get_fns_analysis


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
        if (path_source.endswith(CSV_SUFFIX) and
                not filecmp.cmp(path_source, path_target)):
            # Append csv files but only if they are not identical files.
            with open(path_target, 'ab') as outfile:
                with open(path_source, 'rb') as infile:
                    infile.readline()  # Throw away header on all but first file
                    # Block copy rest of file from input to output without parsing
                    shutil.copyfileobj(infile, outfile)
                    print(path_source + " has been appended.")
            return True
        else:
            print('File: ', path_target, 'present in multiple outputs.')
            return False
    else:
        subfol = os.path.dirname(path_target)
        if not os.path.exists(subfol):
            # create the subfolder if it does not yet exist
            os.makedirs(os.path.dirname(path_target))
        shutil.move(path_source, path_target)
        return True


def combine_directories(fols_input, fol_out):
    """
    Combines a list of cellprofiler ouput directories into one output
    folder.
    This .csv files present in multiple output directories are appended
    to each other, ignoring the header. Other files present in multiple directories
    are only copied once.
    Input:
        fols_input: list of cp ouput input_data_folders
        fol_out: folder to recombine the output input_data_folders into
    """
    for d_root in fols_input:
        for dp, dn, filenames in os.walk(d_root):
            for f in filenames:
                _copy_cp_file(path_source=os.path.join(dp, f), fol_source=d_root, fol_target=fol_out)
