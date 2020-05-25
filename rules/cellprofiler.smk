def define_cellprofiler_rules(cp_configs, base_folder):
    """
    Defines rules for Cellprofiler batch runs.
    These runs will
    The configuration is done via a dictionary with structure:
    {
        BATCH_NAME: # identifier for the run
            {'pipeline': 'path/to/cppipe or cpproj',
             'batchsize': integer, # How many image groups to proces
                                   # as a batch
             'plugins': 'path/to/plugins folder',
             'input_files: (input_files_a, # tuple of snakemake
                            input_files_b, # input file definitions
                            input_filec_c
                            ),
             'output_files': [pattern_a, # list of output file
                              pattern_b], # patterns
             'output_script': 'shell script to move files from'
                             'input to output directory'
    }


    This will write rules to :
        - collect input files (1 rule per batchname)
        - create a Cellprofiler batch file
        - run the batch as subbatches of size 'batchsize'
        - collect all the output images and append all the output .csv files
        - write a rule to move the files from the output folder
          to the target output location. (1 rule per output/batchname)

    :param cp_configs: a dictionary containing the configuration
        for the cellprofiler runs
    :param base_folder: the base folder for output
    :return: A set of rules to run cellprofiler pipelines
    """
    FOL_PLUGINS = base_folder / 'batch_{batchname}/plugins'

    def get_plugins(wildcards):
        """Function to retrieve plugin folders"""
        return cp_configs[wildcards.batchname]['plugins']

    def get_pipeline(wildcards):
        """Function to retrieve pipeline filename"""
        return cp_configs[wildcards.batchname]['pipeline']

    for batchname, cur_config in cp_configs.items():
        """
        Initializes all rules for the defined CellProfiler pipelines.
        """
        rule:
            input:  *cur_config['input_files']
            output: expand('data/batch_{batchname}/filelist.txt', batchname=batchname)
            shell:
                'for f in {input}\n'
                '        do\n'
                '            echo $(realpath $f) >> {output}\n'
                '        done\n'

        for i, outfile in enumerate(cur_config['output_files']):
            rule:
                input:
                     fol_combined=expand('data/batch_{batchname}/combined', batchname=batchname)
                output: outfile
                message: 'Define CP pipeline output files'
                threads: 1
                shell:
                     cur_config['output_script']

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
        batchsize = cp_configs[wildcards.batchname]['batchsize']
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

