from scripts import helpers as hpr
from snakemake.io import get_flag_value
import pathlib
import functools

def define_ilastik_rules(configs_ilastik, folder_base,
                         threads=8,
                         mem_mb=10000,
                         bin_ilastik = '/ilastik-release/run_ilastik.sh',
                         container_ilastik ='docker://ilastik/ilastik-from-binary:1.3.3b1'
                         ):
    """
    Defines rules for ilastik batch runs.
    the configuration is done via a dictionary with structure:
    {
        batch_name: # identifier for the run
            {'project': 'path/to/trained/ilastk project',
             'run_size': integer, # how many images to run together
             'output_format' str, # output format, see ilastik command line argument
             'output_filename': str, # output filename format
             'export_source': str, # ilastik command line argument
             'export_dtype': str, # ilastik command line argument
             'pipeline_result_drange': str, # ilastik command line argument
             'export_drange': '"(0, 65535)"', # ilastik command line argumetn
             'input_files: str list/fkt, # snakemake input file definition
             'output_files': str, # snakemake output file pattern
    }


    this will write rules to :
        - collect input files (1 rule per batchname)
        - run the batch as runs of size 'run_size'
        - collect all the output images
        - write a rule to move the files from the output folder
          to the target output location. (1 rule per output/batchname)

    :param configs_ilastik: a dictionary containing the configuration
        for the cellprofiler runs
    :param folder_base: the base folder for output
    :param bin_ilastik: string for ilastik run function
    :param: container_ilastik: singularity container_ilastik for ilastik
    :return: a set of rules to run ilastik projects
    """
    # Define file/folder patterns
    pat_fol_batch = folder_base / 'ilastik_{batchname}'
    pat_fol_run = pat_fol_batch / 'run_{start}_{end}'
    pat_fol_combined = pat_fol_batch / 'combined'
    pat_fn_hasinput = pat_fol_batch / 'hasinput.done'

    # Define file functions
    def fkt_fn_project(wildcards):
        """Function to retrieve project filename"""
        return str(configs_ilastik[wildcards.batchname]['project'])

    def fkt_resourcs(wildcards):
        return configs_ilastik[wildcards.batchname].get('resources', {})

    def fkt_resources_mem_mb(wildcards):
        return fkt_resourcs(wildcards).get('mem_mb', mem_mb)

    def fkt_resources_threads(wildcards):
        return fkt_resourcs(wildcards).get('threads', threads)

    @functools.lru_cache()
    def list_fns(folder):
        fns = [str(fn) for fn in pathlib.Path(folder).rglob('*') if not fn.stem.startswith('.')]
        return fns

    def get_fns(wildcards):
        checkpoints.ilastik_input_exists.get(**wildcards).output
        var_input = configs_ilastik[wildcards.batchname]['input_files']
        if callable(var_input):
            fns = configs_ilastik[wildcards.batchname]['input_files'](wildcards)
        else:
            fns = list_fns(var_input)
        return fns


    def fkt_ilastik_input(wildcards):
        var_input = configs_ilastik[wildcards.batchname]['input_files']
        if callable(var_input):
            fns = configs_ilastik[wildcards.batchname]['input_files'](wildcards)
        else:
            fns = str(pathlib.Path(var_input))
        return fns

    def fkt_fols_run(wildcards):
        """
        :param wildcards:
        :return:
        """
        fns = get_fns(wildcards)
        run_size = configs_ilastik[wildcards.batchname]['run_size']
        fols_run = []
        for start, end in hpr.get_chunks(len(fns), run_size):
            fols_run.append(expand(str(pat_fol_run), start=start, end=end,
                                        **wildcards)[0])
        return fols_run

    def fkt_fns_run(wildcards):
        fns = get_fns(wildcards)
        start = int(wildcards.start)-1
        end = int(wildcards.end)
        return fns[start:end]

    # Define batch specific rules
    for batchname in configs_ilastik.keys():
        outval = configs_ilastik[batchname]['output_pattern']
        if get_flag_value(outval, 'directory') == True:
            rule:
                input:
                     expand(str(pat_fol_combined), batchname=batchname)
                output: outval
                message: f'Move output folder {outval} for Ilastik run "{batchname}"'
                params:
                shell:
                    """
                    mv {input[0]} {output[0]}
                    """
        else:
            rule:
                input:
                     expand(str(pat_fol_combined), batchname=batchname)
                output: outval
                message: f'Move output file {outval} for Ilastik run "{batchname}"'
                shell:
                    """
                    mv {input[0]}/"$(basename "{output[0}")" "{output[0]}"'
                    """

    # Define rules
    rule ilastik_run_batch:
        message: 'Run image sets {wildcards.start} to {wildcards.end} for Ilastik run "{wildcards.batchname}"'
        input:
             fns = fkt_fns_run,
             project = fkt_fn_project
        output:
              outfolder = temporary(directory(pat_fol_run))
        container: container_ilastik
        threads: fkt_resources_threads
        resources:
            mem_mb = fkt_resources_mem_mb
        params:
            bin_ilastik=bin_ilastik,
            output_format=lambda wildcards: configs_ilastik[wildcards.batchname].get('output_format', "tiff"),
            output_filename=lambda wildcards: configs_ilastik[wildcards.batchname]['output_filename'],
            export_source=lambda wildcards: configs_ilastik[wildcards.batchname].get('export_source', "Probabilities"),
            export_dtype=lambda wildcards: configs_ilastik[wildcards.batchname].get('export_dtype', "uint16"),
            export_drange=lambda wildcards: configs_ilastik[wildcards.batchname].get('export_drange', '"[0, 65535]"'),
            pipeline_result_drange=lambda wildcards: configs_ilastik[wildcards.batchname].get('pipeline_result_drange', '"[0.0, 1.0]"'),
            fkt_fns = lambda wildcards: [f'"{fn}"' for fn in fkt_fns_run(wildcards)]
        shell:
            'LAZYFLOW_THREADS={threads} LAZYFLOW_TOTAL_RAM_MB={resources.mem_mb} {params.bin_ilastik} --headless --project={input.project} '
            '--output_format={params.output_format} '
            '--output_filename_format={output.outfolder}/{params.output_filename} '
            '--export_source={params.export_source} '
            '--export_dtype={params.export_dtype} '
            '--export_drange={params.export_drange} '
            '--pipeline_result_drange={params.pipeline_result_drange} '
            '--readonly 1 '
            '{params.fkt_fns}'
            #'{input.fns} {input.fns[0]}' # Above is a temporary fix for issue #55 of snakemake
            # The first file is added again as Ilastik seems to ignore the first input file :/

    checkpoint ilastik_combine_batch_output:
        message: 'Combine output for Ilastik run "{wildcards.batchname}"'
        input:
            fkt_fols_run  # function that retrieves all groups for a batch
        output: temporary(directory(pat_fol_combined))
        params:
            fkt_input=fkt_fols_run
        run:
            hpr.combine_directories(params.fkt_input, output[0])

    checkpoint ilastik_input_exists:
        message: 'Verify that all input files exist for Ilastik run "{wildcards.batchname}"'
        input: fkt_ilastik_input
        output: touch(pat_fn_hasinput)
