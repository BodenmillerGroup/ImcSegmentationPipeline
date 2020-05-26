import helpers as hpr
import pathlib

def define_ilastik_rules(ilastik_configs, base_folder):
    fol_batch = base_folder/ 'ilastik' / 'batch_{batchname}'
    bin_ilastik = '/ilastik-release/run_ilastik.sh'

    def get_project(wildcards):
        """Function to retrieve pipeline filename"""
        return ilastik_configs[wildcards.batchname]['project']

    def get_ilastik_batch_groups(wildcards):
        """
        :param wildcards:
        :return:
        """
        fns = ilastik_configs[wildcards.batchname]['input_files'](wildcards)
        batchsize = ilastik_configs[wildcards.batchname]['batchsize']
        fols_subbatch = []
        for start, end in hpr.get_chunks(len(fns), batchsize):
            fols_subbatch.append(str(fol_batch / f'run_{start}_{end}'))
        return fols_subbatch

    def get_input_files(wildcards):
        fns = ilastik_configs[wildcards.batchname]['input_files'](wildcards)
        start = int(wildcards.start)-1
        end = int(wildcards.end)
        return fns[start:end]

    rule ilastik_run_batch:
        input:
             fns=get_input_files,
             project=get_project
        output:
              outfolder=directory(fol_batch / 'run_{start}_{end}')
        container:
            'docker://ilastik/ilastik-from-binary:1.3.3b1'
        threads: 8
        resources:
            mem_mb=30000
        params:
            bin_ilastik=bin_ilastik,
            output_format=lambda wildcards: ilastik_configs[wildcards.batchname]['output_format'],
            output_filename=lambda wildcards: ilastik_configs[wildcards.batchname]['output_filename'],
            export_source=lambda wildcards: ilastik_configs[wildcards.batchname]['export_source'],
            export_dtype=lambda wildcards: ilastik_configs[wildcards.batchname]['export_dtype'],
            pipeline_result_drange=lambda wildcards: ilastik_configs[wildcards.batchname]['pipeline_result_drange']

        shell:
            'LAZYFLOW_THREADS={threads} LAZYFLOW_TOTAL_RAM_MB={resources.mem_mb} {params.bin_ilastik} --headless --project={input.project} '
            '--output_format={params.output_format} '
            '--output_filename_format={output.outfolder}/{params.output_filename} '
            '--export_source={params.export_source} '
            '--export_dtype={params.export_dtype} '
            '--pipeline_result_drange={params.pipeline_result_drange} '\
            '--readonly '
            '{input.fns} {input.fns[0]}'

    checkpoint ilastik_combine_batch_output:
        input:
            get_ilastik_batch_groups  # function that retrieves all groups for a batch
        output: directory(fol_batch / 'combined')
        params:
            script='combine'
        script:
                '../helpers.py'


    for batchname in ilastik_configs.keys():
        rule:
            input:
                 expand(str(fol_batch / 'combined'), batchname=batchname)
            output:
                  ilastik_configs[batchname]['output_pattern']
            shell:
                 'cp {input}/"$(basename "{output}")" "{output}"'


