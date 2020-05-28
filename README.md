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

Initialize the conda snakemake environment:

```
conda env create -f envs/env_snakemake_imc.yml
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

