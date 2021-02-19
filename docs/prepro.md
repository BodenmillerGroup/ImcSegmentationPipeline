# Pre-processing

![prepro](img/prepro.png)
*Conversion from raw .mcd files to .ome.tiff and .tiff files suitable for downstream analysis*

During the first step of the segmentation pipeline, raw imaging files need to be converted to file formats that can be read-in by external software (Fiji, R, python, histoCAT).

**Please follow the [preprocessing.ipynb](https://github.com/BodenmillerGroup/ImcSegmentationPipeline/blob/main/preprocessing.ipynb) script to pre-process the raw data**
To get started, please refer to the instructions [here](index.md).

## Input

The Hyperion Imaging System produces vendor controlled `.mcd` and `.txt` files in the following folder structure:

.
+-- XYZ_ROI_001_1.txt
+-- XYZ_ROI_002_2.txt
+-- XYZ_ROI_003_3.txt
+-- XYZ.mcd
+-- XYZ.schema

where `XYZ` defines the filename and `ROI_001`, `ROI_002`, `ROI_003` are names for the selected regions of interest (ROI). These can be sepcified in the Fluidigm software when selecting ROIs.
The `.mcd` file contains the raw imaging data of all acquired ROIs while each `.txt` file contains data of a single ROI.
To enforce a consistent naming scheme and to bundle all metadata, we recommend to zip the folder and specify the location of all `.zip` files for preprocessing.

## Conversion fom .mcd to .ome.tiff files

In the first step of the segmentation pipeline, raw `.mcd` files are converted into an `.ome.tiff` format [^fn1].
This serves the purpose to allow vendor independent downstream analysis and visualization of the images.
For IMC data this one multiplane tiff file per acquisition. Each channel needs to have the
channel label attribute as well as the fluor attribute set. For in-depth information  of the ome.tiff format see [here](https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html). For IMC data the metal name followed
by the isotopic mass are used with the form: (IsotopeShortname)(Mass), e.g. Ir191 for Iridium
isotope 191.

## Conversion from .ome.tiff to single-channel tiffs

For full documentation on the histoCAT format, please follow [the manual](https://github.com/BodenmillerGroup/histoCAT/releases/download/histoCAT_1.76/histoCATmanual_1.76.pdf).

## Conversion from .ome.tiff to multi-channel tiffs

2.4 Generation of the analysis stacks
In the next step the converted .ome.tiff files are converted in a stack format suitable for further
analysis, e.g. using CellProler. In a basic pipeline two stacks will be prepared: a 'Full' stack,
containing all the channels chosen for CellProfiler quantification as well as the 'Ilastik' stack,
containing all the channels selected for the Ilastik pixel classification. It is straight forward to
modify this step to generate additional stacks, e.g. for additional tissue structure segmentations.

## Output

Summarize output

[^fn1]: Goldberg I.G. _et al._ (2005) The open microscopy environment (OME) data model and XML le: open tools for informatics and quantitative analysis in biological imaging. Genome Biology 6(5), R47.