# A complete segmentation approach for imaging mass cytometry data

Measuring objects and their features in images is a basic step in many quantitative tissue image analysis workflows. 
This repository presents a flexible and scalable image processing pipeline tailored to highly multiplexed images facilitating the segmentation of single cells across hundreds of images. 
It is based on supervised pixel classification using [Ilastik](https://www.ilastik.org/) to distill segmentation relevant information from multiplexed images in a semi-supervised, automated fashion. 
This feature reduction step is followed by standard image segmentation using [CellProfiler](https://cellprofiler.org/).
The segmentation pipeline is accompanied by the helper python package [imctools](https://github.com/BodenmillerGroup/imctools) as well as customized [CellProfiler modules](https://github.com/BodenmillerGroup/ImcPluginsCP), which facilitate the analysis of highly multiplexed images. 
The pipeline is entirely build on open source tool, can be easily adapted to more specific problems and forms a solid basis for quantitative multiplexed tissue image analysis.
For a more detailed introduction, please refer to the [Introduction](intro.md).

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

## Pre processing

## Ilastik training

## CellProfiler image segmentation

## Contributors

Vito Zanotelli [:fontawesome-brands-github:](https://github.com/votti) [:fontawesome-brands-twitter:](https://twitter.com/ZanotelliVRT) []
Nils Eling [:fontawesome-brands-github:](https://github.com/nilseling) [:fontawesome-brands-twitter:](https://twitter.com/NilsEling) [:fontawesome-solid-home:](https://nilseling.github.io/)

Whoever wants to contribute

## Citation

To come...

[^fn1]: Giesen C. _et al._ (2014) Highly multiplexed imaging of tumor tissues with subcellular resolution by mass cytometry. Nat. Methods, 11, 417–422.