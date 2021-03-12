# Pre-processing

![prepro](img/prepro.png)
*Conversion from raw .mcd files to .ome.tiff and .tiff files suitable for downstream analysis*

During the first step of the segmentation pipeline, raw imaging files need to be converted to file formats that can be read-in by external software (Fiji, R, python, histoCAT).

**Please follow the [preprocessing.ipynb](https://github.com/BodenmillerGroup/ImcSegmentationPipeline/blob/main/preprocessing.ipynb) script to pre-process the raw data**
To get started, please refer to the instructions [here](index.md).

## Input

**The zipped .mcd files**

The Hyperion Imaging System produces vendor controlled `.mcd` and `.txt` files in the following folder structure:

```
.
+-- XYZ_ROI_001_1.txt
+-- XYZ_ROI_002_2.txt
+-- XYZ_ROI_003_3.txt
+-- XYZ.mcd
```

where `XYZ` defines the filename and `ROI_001`, `ROI_002`, `ROI_003` are names for the selected regions of interest (ROI). These can be sepcified in the Fluidigm software when selecting ROIs.
The `.mcd` file contains the raw imaging data of all acquired ROIs while each `.txt` file contains data of a single ROI.
To enforce a consistent naming scheme and to bundle all metadata, **we recommend to zip the folder** and specify the location of all `.zip` files for preprocessing.

**The panel file**

The panel file (in `.csv` format) specifies the type of antibodies that were used in the experiment.
The first few entries to the panel file can look like this:

|  Metal Tag | Target | full | ilastik |
|  :---      | :---   | :--- | :---    | 
|  Dy161     | Ecad   | 1    | 1       |
|  Dy162     | CD45   | 1    | 0       |
|  Er166     | CD3    | 1    | 1       |

Usually there are more columns but the important ones in this case are `Metal Tag`, `full` and `ilastik`.
The `1` in the `full` column specifies channels that should be written out to an image stack that will be later on used to extract features. 
Here, please specify all channels with `1` that you want to have included in the analysis.
The `1` in the `ilastik` column indicates channels that will be used for Ilastik pixel classification therefore being used for image segmentation.
During the pre-processing steps, you will need to specify the name of the panel column that contains the metal isotopes, the name of the column that contains the `1` or `0` entries for the channels to be analysed and the name of the column that indicates the channels used for Ilastik training as seen above.

**Naming conventions**

The pipeline relies on `_ilastik` as ilastik suffix. 

## Conversion fom .mcd to .ome.tiff files

In the first step of the segmentation pipeline, raw `.mcd` files are converted into an `.ome.tiff` format [^fn1].
This serves the purpose to allow vendor independent downstream analysis and visualization of the images.
For in-depth information of the `.ome.tiff` file format see [here](https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html). 
Each `.mcd` file can contain multiple acquisitions. This means that multiple multi-channel `.ome.tiff` files per `.mcd` file are produced. 
The `Fluor` and `Name` of each channel is set.
Here `Name` contains the actual name of the antibody as defined in the panel file and `Fluor` contains the metal tag of the antibody.
For IMC data, the metal tag is defined as: `(IsotopeShortname)(Mass)`, e.g. Ir191 for Iridium
isotope 191.

To perform this conversion, we use the [mcdfolder_to_imcfolder](https://bodenmillergroup.github.io/imctools/converters/mcdfolder2imcfolder.html#imctools.converters.mcdfolder2imcfolder.mcdfolder_to_imcfolder) converter function of the [imctools](https://bodenmillergroup.github.io/imctools/) package.
It uses the [xtiff](https://github.com/BodenmillerGroup/xtiff) python package to write the `.ome.tiff` files.

The output folder for each sample has the following form:

```
.
+-- XYZ_s0_ac1_ac.ome.tiff
+-- XYZ_s0_ac1_ac.ome.tiff
+-- XYZ_s0_ac1_ac.ome.toff
+-- XYZ_s0_p1_pano.png
+-- XYZ_s0_slide.png
+-- XYZ_schema.xml
+-- XYZ_session.json
```

**TODO: Explain what these files and what the nameing is**

## Conversion from .ome.tiff to single-channel tiffs

We also export the images in a format that is supported by the [histoCAT](https://bodenmillergroup.github.io/histoCAT/) software[^fn2].
To load images into `histoCAT`, they need to be stored as unsigned 16-bit or unsigned 32-bit single-channel `.tiff` files. 
For each acquisition (each `.ome.tiff` file), the [ome2histocat](https://bodenmillergroup.github.io/imctools/converters/ome2histocat.html) converter exports one folder containing all measured channels as single-channel `.tiff` files.
The naming convention of these `.tiff` files is `Name_Fluor`, where `Name` is the name of the antibody (or the metal if no name is available) and `Fluor` is the name of the metal isotope.
For full documentation on the histoCAT format, please follow [the manual](https://github.com/BodenmillerGroup/histoCAT/releases/download/histoCAT_1.76/histoCATmanual_1.76.pdf).

## Conversion from .ome.tiff to multi-channel tiffs

2.4 Generation of the analysis stacks
In the next step the converted .ome.tiff files are converted in a stack format suitable for further
analysis, e.g. using CellProler. In a basic pipeline two stacks will be prepared: a 'Full' stack,
containing all the channels chosen for CellProfiler quantification as well as the 'Ilastik' stack,
containing all the channels selected for the Ilastik pixel classification. It is straight forward to
modify this step to generate additional stacks, e.g. for additional tissue structure segmentations.

## Export of acquisition-specific metadata

## Output

Summarize output

[^fn1]: Goldberg I.G. _et al._ (2005) The open microscopy environment (OME) data model and XML file: open tools for informatics and quantitative analysis in biological imaging. Genome Biology 6(5), R47.
[^fn2]: Shapiro D. _et al._ (2017) histoCAT: analysis of cell phenotypes and interactions in multiplex image cytometry data. Nature Methods 14, pages873–876.