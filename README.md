[![DOI](https://zenodo.org/badge/103582813.svg)](https://zenodo.org/badge/latestdoi/103582813)
# A flexible  image segmentation pipeline for heterogeneous multiplexed tissue images based on pixel classification

I am currently remodelling the whole description/procedure and would be happy for any feedback!

#####
Please consider the current state of this repository as 'Beta'.
####

Notable changes to older version is change to CellProfiler 3 and that the ImcPluginsCP work now with any CP3 installation without special installation procedure.

The pipeline is based on CellProfiler (http://cellprofiler.org/, v1.3.5) for segmentation and Ilastik (http://ilastik.org/) for
for pixel classification. It is streamlined by using the specially developped imctools python package (https://github.com/BodenmillerGroup/imctools) as well as custom CellProfiler modules (https://github.com/BodenmillerGroup/ImcPluginsCP/tree/master-cp3, master-cp3 branch!).

This pipeline was developped in the Bodenmiller laboratory at the University of Zurich (http://www.bodenmillerlab.org/) to segment hundreds of highly multiplexed imaging mass cytometry (IMC) images. However we think it might also be usefull for other multiplexed imaging techniques.

The document to start can be found at 'scripts/imc_preprocessing.ipynb' (https://nbviewer.jupyter.org/github/BodenmillerGroup/ImcSegmentationPipeline/blob/development/scripts/imc_preprocessing.ipynb).
The pdf found in 'Documentation/201709_imctools_guide.pdf' is still conceptually valid, however the installation procedures described are outdated. Please follow the instructions in the imc_preprocessing.ipynb document!

This pipeline was presented at the 2019 Imaging Mass Cytometry User Group Meeting. [The slides can be downloaded here](https://drive.google.com/file/d/1ajPzlJ2CUj6sFYSOq0HR2dOJehHIlCJt/view). The slides briefly explain why we chose this approach to image segmentation and provide help to run the pipeline.

We freely share this pipeline in the hope that it will be usefull for others to perform high quality image segmentation and serve as a basis to develop more complicated open source IMC image processin17g workflows. In return we would like you to be considerate and give us and others feedback if you find a bug or issue and raise a GitHub Issue on the affected projects or on this page.

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

