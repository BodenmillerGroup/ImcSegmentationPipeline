# A complete segmentation approach for imaging mass cytometry data

Measuring objects and their features in images is a basic step in many quantitative tissue image analysis workflows. 
This repository presents a flexible and scalable image processing pipeline tailored to highly multiplexed images facilitating the segmentation of single cells across hundreds of images. 
It is based on supervised pixel classification using [Ilastik](https://www.ilastik.org/) to distill segmentation relevant information from multiplexed images in a semi-supervised, automated fashion. 
This feature reduction step is followed by standard image segmentation using [CellProfiler](https://cellprofiler.org/).
The segmentation pipeline is accompanied by the helper python package [imctools](https://github.com/BodenmillerGroup/imctools) as well as customized [CellProfiler modules](https://github.com/BodenmillerGroup/ImcPluginsCP), which facilitate the analysis of highly multiplexed images. 
The pipeline is entirely build on open source tool, can be easily adapted to more specific problems and forms a solid basis for quantitative multiplexed tissue image analysis.
For a more detailed introduction, please refer to the [Introduction](intro.md).

This site gives detailed explanations on the 5 step (A-E, [see below](#overview)) pipeline to generate single-cell measurements from raw imageing data. 

## Getting started

For the main part of the analysis, you will need to install [Ilastik](https://www.ilastik.org/download.html) and [CellProfiler](https://cellprofiler.org/releases).
The current setup is tested with Ilastik v1.3.5 and CellProfiler v4.0.6.

Furthermore, before running the analysis, you will need to setup a `conda` environment:

1. [Install conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)

2. Clone the `ImcSegmentationPipeline` repository: 

```bash
git clone https://github.com/BodenmillerGroup/ImcSegmentationPipeline.git
```

3. Setup the conda environment: 

```bash
cd ImcSegmentationPipeline
conda env create -f conda_imctools.yml
```

4. Activate the environment and start a jupyter instance

```bash
conda activate ImcSegmentationPipeline
jupyter notebook
```

## A - Pre processing

To work with the generated imaging data, they will first be converted into `.ome.tiff`, multi-channel `.tiff` and single-channel `.tiff` formats that are compatible with most imaging software.
A key step of the pre-processing pipeline is also the selection of channels for (i) downstream cell measurements and (ii) ilastik pixel classification.

Please follow the [pre-processing guide](prepro.md) for more information. 

## B/C - Ilastik training

## D/E - CellProfiler image segmentation

![full_pipeline](img/Full_pipeline.png)
*<a name="overview">An overview of the full segmentation pipeline</a>*

## Contributors

Vito Zanotelli [:fontawesome-brands-github:](https://github.com/votti) [:fontawesome-brands-twitter:](https://twitter.com/ZanotelliVRT)
Nils Eling [:fontawesome-brands-github:](https://github.com/nilseling) [:fontawesome-brands-twitter:](https://twitter.com/NilsEling) [:fontawesome-solid-home:](https://nilseling.github.io/)

Whoever wants to contribute

## Citation

To come...
