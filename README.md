[![DOI](https://zenodo.org/badge/103582813.svg)](https://zenodo.org/badge/latestdoi/103582813)
# A flexible  image segmentation pipeline for heterogeneous multiplexed tissue images based on pixel classification

## Introduction
The pipeline is based on CellProfiler (http://cellprofiler.org/, tested v4.0.6) for segmentation and Ilastik
(http://ilastik.org/, tested v1.3.5)
for pixel classification. It is streamlined by using the specially developed imctools python
package (https://github.com/BodenmillerGroup/imctools, >v2.1) as well as custom CellProfiler modules 
(https://github.com/BodenmillerGroup/ImcPluginsCP, release v4.2.1).

This repository showcases the basis of the workflow with step-by-step instructions. To run this more automatized, we recommend
our Snakemake implementation: https://github.com/BodenmillerGroup/ImcSegmentationSnakemake

This pipeline was developed in the Bodenmiller laboratory at the University of Zurich (http://www.bodenmillerlab.org/)
to segment hundreds of highly multiplexed imaging mass cytometry (IMC) images.
However we think that this concept also works well for other multiplexed imaging modalities..

The document to start can be found at 'scripts/imc_preprocessing.ipynb'
(https://nbviewer.jupyter.org/github/BodenmillerGroup/ImcSegmentationPipeline/blob/development/scripts/imc_preprocessing.ipynb).
The pdf found in 'Documentation/201709_imctools_guide.pdf' is still conceptually valid, however the installation
procedures described are outdated. Please follow the instructions in the imc_preprocessing.ipynb document!

This pipeline was presented at the 2019 Imaging Mass Cytometry User Group Meeting.
[The slides can be downloaded here](https://drive.google.com/file/d/1ajPzlJ2CUj6sFYSOq0HR2dOJehHIlCJt/view).
The slides briefly explain why we chose this approach to image segmentation and provide help to run the pipeline.

We freely share this pipeline in the hope that it will be useful for others to perform high quality image segmentation
and serve as a basis to develop more complicated open source IMC image processin17g workflows. In return we would like
you to be considerate and give us and others feedback if you find a bug or issue and raise a GitHub Issue
on the affected projects or on this page.

## Changelog
- v2.3:
    - Bugfixes:
        - 1_prepare_ilastik: Removed special characters from pipeline comments as this caused encoding issues.

- v2.1:
    - Bugfixes:
        - 1_prepare_ilastik: Fix range to 0-1 for mean image, preventing out of range errors

- v2.0:
    - Change to imctools v2:
        - Changes the structure of the folder to the new format, changing the
          naming of the .ome.tiff files => If you use this pipeline you need to re-generate the OME tiff
          
    - Change to Cellprofiler v4:
        - Requires the use of the ImcPluginsCP master branch or a release > v.4.1
        
    - Varia:
        - Updated documentation
        - Adds var_Cells.csv containing metadata for the measurements
        - Adds panel to cpout folder


## Citation
d
If you use this workflow for your research, please cite us:
```
@misc{ImcSegmentationPipeline,
    author       = {Vito RT Zanotelli, Bernd Bodenmiller},
    title        = {{ImcSegmentationPipeline: A pixelclassification based multiplexed image segmentation pipeline}},
    month        = Sept,
    year         = 2017,
    doi          = {10.5281/zenodo.3841961},
    version      = {0.9},
    publisher    = {Zenodo},
    url          = {https://doi.org/10.5281/zenodo.3841961}
    }
```

