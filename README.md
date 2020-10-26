# A flexible  image segmentation pipeline for heterogneous multiplexed tissue images based on pixel classification
*This is the experimental `snakemake` branch*

[![Snakemake](https://img.shields.io/badge/snakemake-≥5.7.0-brightgreen.svg)](https://snakemake.bitbucket.io)
[![Build Status](https://travis-ci.org/snakemake-workflows/misegmentation.svg?branch=master)](https://travis-ci.org/snakemake-workflows/misegmentation)

The pipeline is based on `CellProfiler` (http://cellprofiler.org/) for segmentation and `Ilastik` (http://ilastik.org/) for
for pixel classification. It is streamlined by using the specially developed `imctools` python package (https://github.com/BodenmillerGroup/imctools) 
package as well as custom CellProfiler modules (https://github.com/BodenmillerGroup/ImcPluginsCP, develop-cp3 branch!).

This pipeline was developed in the Bodenmiller laboratory of the University of Zurich (http://www.bodenmillerlab.org/) to segment hundereds of highly multiplexed
imaging mass cytometry (IMC) images. However it also has been already been sucessfully applied to other multiplexed
imaging modalities..

The PDF found describes the conceptual basis: 'Documentation/201709_imctools_guide.pdf'. While still conceputually valid the installation procedures described are outdated.

## Usage
If you use this workflow in a paper, don't forget to give credits to the authors by citing the URL of this (original) repository and, if available, its DOI (see above).

### Step 0: install systems requirements
To run the pipeline, the following software needs to be installed:
- `conda`: A reproducible package manager
   - Installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
- `singularity`: A container platform
   - Documentation: https://sylabs.io/guides/3.5/user-guide/introduction.html
   - Installation: https://sylabs.io/guides/3.5/admin-guide/installation.html
   - Note: Installation via conda currently gives lots of issues and thus is not recommended.

Make sure this software packages work.

### Step 1: Obtain a copy of this workflow

1. Create a new github repository using this workflow [as a template](https://help.github.com/en/articles/creating-a-repository-from-a-template).
2. [Clone](https://help.github.com/en/articles/cloning-a-repository) the newly created repository
to your local system, into the place where you want to perform the data analysis.


###  Step2: Install Snakemake
Install Snakemake using [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html):

    conda create -c bioconda -c conda-forge -n snakemake snakemake

For installation details, see the [instructions in the Snakemake documentation](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html).

### Step 3: Configure workflow

Configure the workflow according to your needs via editing the files in the `config/` folder.
Adjust `config.yaml` to configure the workflow execution.

### Step 4: Execute workflow

Activate the conda environment:

    conda activate snakemake

Test your configuration by performing a dry-run via

    snakemake --use-conda -n --use-singularity


Execute the workflow locally via

    snakemake --use-conda --cores $N --use-singularity

using `$N` cores or run it in a cluster environment via

    snakemake --use-conda --cluster qsub --jobs 100 --use-singularity

or

    snakemake --use-conda --drmaa --jobs 100 --use-singularity

The Cellprofiler output will be in `results/cpout`. All other folders should be considered
temporary output.

See section 'UZH slurm cluster' to get more details how to run this on the cluster
of the University of Zurich


## Optional:

### Step: download the example data

```
snakemake download_example_data --use-singularity --cores 32
```

### Step: Run the pipeline until the Ilastik classifier

```
snakemake prepare_cell_classifier --use-singularity --cores 32
```

This will generate random crops to train the Ilastik cell pixel classifier in `results/ilastik_training_data`

Use these cropped images to train an ilastik classifier for pixel classes: `nuclei`, `cytoplasm/membrane/nucleiborder`, `background`
and save the trained classifier under the `fn_cell_classifier` in the configuration file.

### Step: UZH cluster: How to run this workflow on a slurm cluster (UZH science cluster)

First retrieve the github repository & install the conda environment as above.

#### Make a default configuration

Generate this file in the path `~/.config/snakemake/cluster_config.yml`
```
__default__:
  time: "00:15:00"
```
This defines the default batch run parameters.

#### Install the slurm cluster profile

Follow the instructions from:  
`https://github.com/Snakemake-Profiles/slurm`

Use the following settings:  
`profile_name`: slurm  
`sbatch_defaults`:  
`cluster_config`: ../cluster_config.yml  
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

