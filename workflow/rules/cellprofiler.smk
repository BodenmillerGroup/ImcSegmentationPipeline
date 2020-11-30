import json
from scripts import helpers as hpr
import pathlib
from snakemake.io import get_flag_value
import shutil

def define_cellprofiler_rules(configs_cp, folder_base,
                              container_cp="docker://cellprofiler/cellprofiler:3.1.9"):
    """
    Defines rules for cellprofiler batch runs.
    the configuration is done via a dictionary with structure:
    {
        batch_name: # identifier for the run
            {'pipeline': 'path/to/cppipe or cpproj',
             'run_size': integer, # how many image groups to proces
                                   # as a batch
             'plugins': 'path/to/plugins folder',
             'input_files: (input_files_a, # tuple of snakemake
                            input_files_b, # input file definitions
                            input_filec_c
                            ),
             'output_files': {'.': # Dictionary with folder location relative to
                                    # output folder
                                [pattern_a, # list of output file
                              pattern_b]}, # patterns
             'input_folder': 'path/to/inputfolder' # Path to cellprofiler
                                                   # Input folder
                                                   # -> required if eg metadata
                                                   # file paths specified
                                                   # relative to input folder.
    }


    this will write rules to :
        - collect input files (1 rule per batchname)
        - create a cellprofiler batch file
        - run the batch as subbatches of size 'run_size'
        - collect all the output images and append all the output .csv files
        - write a rule to move the files from the output folder
          to the target output location. (1 rule per output/batchname)

    :param configs_a dictionary containing the configuration
        for the cellprofiler runs
    :param folder_base: the base folder for output
    :param container_singularity container_ilastik for cellprofiler
    :return: a set of rules to run cellprofiler pipelines
    """

    # Define file/folder patterns
    pat_fol_batch = folder_base / 'cp_{batchname}'
    pat_fol_plugins = pat_fol_batch / 'plugins'
    pat_fn_filelist = pat_fol_batch / 'filelist.txt'
    pat_fol_run = pat_fol_batch / 'run_{start}_{end}'
    pat_fol_batch_combined = pat_fol_batch / 'combined'
    pat_fn_batchfile = pat_fol_batch / 'Batch_data.h5'
    pat_fn_batchgroups = pat_fol_batch / 'result.json'
    
    # A dummy file that enables the user to open a project
    # to explore it interactively
    pat_openproject = folder_base / 'cp_{batchname}_open.sh'

    # Define file functions
    def fkt_fol_plugins(wildcards):
        """Function to retrieve plugin folders"""
        return configs_cp[wildcards.batchname]['plugins']

    def fkt_resourcs(wildcards):
        return configs_cp[wildcards.batchname].get('resources', {})

    def fkt_resources_mem_mb(wildcards):
        return fkt_resourcs(wildcards).get('mem_mb', 8000)

    def fkt_fn_pipeline(wildcards):
        """Function to retrieve pipeline filename"""
        return configs_cp[wildcards.batchname]['pipeline']

    def fkt_input_folder(wildcards):
        """Function to retrieve plugin folders"""
        return configs_cp[wildcards.batchname].get('input_folder', '.')

    def fkt_input_files(wildcards):
        """Unpack input files"""
        input_files = configs_cp[wildcards.batchname]['input_files']
        return_list = []
        for inp in input_files:
            if callable(inp):
                # If this is a function, call it to get the
                # output
                inp = inp(wildcards)
            if (isinstance(inp, str) | isinstance(inp, pathlib.Path)):
                # If it is neither a string or a path
                # convert it to a list
                inp = [inp]
            return_list += inp
        return [str(val) for val in return_list]

    def fkt_fols_run(wildcards):
        """
        Function to dynamically generate batch filenames based on the
        `cp_get_groups` checkpoint.
        :param wildcards:
        :return:
        """
        fn_grpfile = checkpoints.cp_get_groups.get(**wildcards).output[0]
        run_size = configs_cp[wildcards.batchname]['run_size']
        # from gc3apps: https://github.com/BodenmillerGroup/gc3apps/blob/master/gc3apps/pipelines/gcp_pipeline.py
        with open(fn_grpfile) as json_file:
            data = json.load(json_file)
            total_size = len(data)
        fols_run = []
        for start, end in hpr.get_chunks(total_size, run_size):
            fols_run.append(expand(str(pat_fol_run), start=start, end=end,
                                    **wildcards)[0])
        return fols_run

    # Define batch specific rules
    for batchname, cur_config in configs_cp.items():
        """
        Initializes all rules for the defined CellProfiler pipelines.
        """
        for subfol, outval in cur_config['output_patterns'].items():
            if get_flag_value(outval, 'directory') == True:
                rule:
                    input:
                         fol_combined=expand(str(pat_fol_batch_combined), batchname=batchname)
                    output: outval
                    message: f'Move output folder {outval} for CellProfiler run "{batchname}"'
                    threads: 1
                    params:
                          subfol = subfol
                    run:
                        shutil.move(pathlib.Path(input.fol_combined[0]) / params.subfol, output[0])
            else:
                for outfile in outval:
                    rule:
                        input:
                             fol_combined=expand(str(pat_fol_batch_combined), batchname=batchname)
                        output: outfile
                        message: f'Move output file {outval} for CellProfiler run "{batchname}"'
                        threads: 1
                        params:
                              subfol = subfol
                        run:
                            shutil.move(((pathlib.Path(input.fol_combined[0]) / params.subfol) / pathlib.Path(output[0]).name).resolve(),
                                        output[0])

    # Define Cellprofiler specific rules
    rule cp_get_plugins:
        message: 'Prepare plugins folder for CellProfiler run "{wildcards.batchname}"'
        input: fkt_fol_plugins
        output: directory(pat_fol_plugins)
        shell:
             'mkdir -p {output} && '
             'cp -R {input}/* {output}'

    rule generate_file_list:
        message: f'Generate a file list of input files for CellProfiler run "{batchname}"'
        input:  fkt_input_files
        output: pat_fn_filelist
        run:
            with open(output[0], mode='w') as f:
                fns_list = [inp for inp in input]
                for pfn in fns_list:
                    pfn = pathlib.Path(pfn)
                    if pfn.is_dir():
                        fns = pfn.rglob('*')
                    else:
                        fns = [pfn]
                    for fn in fns:
                        f.write("%s\n" % fn.resolve())

    rule cp_create_batch_data:
        message: 'Prepare batch file from file list for CellProfiler run "{wildcards.batchname}"'
        input:
            filelist=pat_fn_filelist,
            pipeline=fkt_fn_pipeline,
            plugins=pat_fol_plugins
        output:
            pat_fn_batchfile
        params:
            outfolder=str(pat_fol_batch),
            inputfolder=fkt_input_folder
        container: container_cp

        message: 'Prepares a batch file'
        shell:
            """
            set +e
            cellprofiler -c -r --file-list={input.filelist} \
                --plugins-directory {input.plugins}  \
                -p {input.pipeline} -o {params.outfolder} -i {params.inputfolder}
            exitcode=$?
            if [ $exitcode -ge 0 ]
            then
                exit 0
            else
                echo "No valid image set identified! Check the input files\
                      or pipeline!"
                exit 1
            fi
            """

    rule cp_run_batch:
        message: 'Run image sets {wildcards.start} to {wildcards.end} for CellProfiler run "{wildcards.batchname}"'
        input:
             batchfile=pat_fn_batchfile,
             plugins=pat_fol_plugins,
             batchgroups=pat_fn_batchgroups
        output:
              outfolder=temporary(directory(pat_fol_batch / 'run_{start}_{end}'))
        params:
              inputfolder=fkt_input_folder
        container: container_cp
        threads: 1
        resources:
            mem_mb=fkt_resources_mem_mb
        shell:
            """
            set +e
            cellprofiler -c -r -p {input.batchfile} -f {wildcards.start} -l {wildcards.end} \
                --do-not-write-schema --plugins-directory={input.plugins} -o {output.outfolder} \
                -i {params.inputfolder}
            exitcode=$?
            if [ $exitcode -ge 0 ]
            then
                exit 0
            else
                exit 1
            fi
            """


    checkpoint cp_get_groups:
        input: pat_fn_batchfile,
        output: pat_fn_batchgroups
        message: 'Prepare image group file for CellProfiler run "{wildcards.batchname}"'
        container: container_cp
        shell:
            "cellprofiler -c --print-groups={input[0]}  > {output[0]} || true"


    checkpoint cp_combine_batch_output:
        message: 'Combine output for CellProfiler run "{wildcards.batchname}"'
        input: fkt_fols_run  # function that retrieves all groups for a batch
        output: temporary(directory(pat_fol_batch_combined))
        params:
              fkt_input=fkt_fols_run
        run:
            hpr.combine_directories(params.fkt_input, output[0])
            
    rule open_project:
        input:
             pipeline=fkt_fn_pipeline,
             plugins=pat_fol_plugins,
             file_list=pat_fn_filelist
        output:
             pat_openproject
        params:
              inputfolder=fkt_input_folder,
        shell:
             """
             echo "\
                 cellprofiler \
                     -p {input.pipeline} \
                     --plugins-directory={input.plugins} \
                     -i {params.inputfolder} \
                     --file-list={input.file_list}" > {output[0]}
             chmod +x {output[0]}
             """
