# A flexible  image segmentation pipeline for heterogneous multiplexed tissue images based on pixel classification
*This is the experimental `snakemake` branch*

The pipline is based on `CellProfiler` (http://cellprofiler.org/, v1.3.5) for segmentation and `Ilastik` (http://ilastik.org/) for
for pixel classification. It is streamlined by using the specially developped `imctools` python package (https://github.com/BodenmillerGroup/imctools) 
package as well as custom CellProfiler modules (https://github.com/BodenmillerGroup/ImcPluginsCP, develop-cp3 branch!).

This pipline was developped in the Bodenmiller laboratory of the University of Zurich (http://www.bodenmillerlab.org/) to segment hundereds of highly multiplexed
imaging mass cytometry (IMC) images. However we think it might also be usefull for other multiplexed imaging techniques.

The PDF found describes the conceptual basis: 'Documentation/201709_imctools_guide.pdf'. While still conceputually valid the installation procedures described are outdated.

## Requirements
To run the pipeline, the following software needs to be installed:
- `conda`: A reproducible package manager
   - Installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
- `singularity`: A container platform
   - Documentation: https://sylabs.io/guides/3.5/user-guide/introduction.html
   - Installation: https://sylabs.io/guides/3.5/admin-guide/installation.html
   - Note: Installation via conda currently gives lots of issues and thus is not recommended.

Make sure this software packages work.

## Setup the environment
Clone the github repository and the submodules.

```
git clone --recurse-submodules -b snakemake git@github.com:BodenmillerGroup/ImcSegmentationPipeline.git
```
Change directory into the Git folder

```
cd ImcSegmentationPipeline
```

Initialize the conda snakemake environment:

```
conda env create -f envs/env_imcsegpipe.yml
```

Activate the environment

```
conda activate snakemake_imc
```

## Edit the configuration
To customize your analysis run, edit the configuration file: `config_pipeline.yml`

## Run the pipeline

### Optional: download the example data

```
snakemake download_example_data --use-singularity --cores 32
```

### Run the pipeline until the Ilastik classifier

```
snakemake prepare_cell_classifier --use-singularity --cores 32
```

This will generate random crops to train the Ilastik cell pixel classifier in `data/ilastik_training_data`

Use these cropped images to train an ilastik classifier for pixel classes: `nuclei`, `cytoplasma/membrane/nucleiborder`, `background`
and save the trained classifier under the `fn_cell_classifier` in the configuration file.

### Run the full pipeline

```
snakemake --use-singularity --cores 32
```

The Cellprofiler output will be in `data/cpout`


# How to run this workflow on a slurm cluster (UZH science cluster)

First retrieve the github repository & install the conda environment as above.

## Make a default configuration

Generate this file in the path `~/.config/snakemake/cluster_config.yml`
```
__default__:
  time: "00:15:00"
```
This defines the default batch run parameters.

## Install the slurm cluster profile

Follow the instructions from:  
`https://github.com/Snakemake-Profiles/slurm`

Use the following settings:  
`profile_name`: slurm  
`sbatch_defaults`:  
`cluster_config`: ../cluser_config.yml  
`advanced_argument_conversion`: 1 (Actually I have never tried this, might be worth a try) 

To run the pipeline, the following modules are required and need to be loaded in this order:
```
module load generic
module load anaconda3 
module load singularity
conda activate snakemake_imc
```


To run the snakemake command on the cluster, the following flags are needed:
- `--profile slurm` flag to specify the profile
- `--use-singularity` to use singularity
- `--singularity-args "\-u"` to use non-privileged singularity mode
- `--jobs #` to have at most # number of concurrent jobs submitted (eg `--jobs 50`)

After the example data has been downloaded (see above) the following command would run the full pipeline:

```
snakemake --profile slurm --use-singularity --singularity-args "\-u" --jobs 50
```

