# Pre-processing

![prepro](img/prepro.png)
*An overview of the full segmentation pipeline*

## Input

This dataset are zipped input_data_folders_path_inputs of the `.mcd` and all `.txt` files corresponding to one acquisitions session.
This is my recomended data format as it preserves and contains all original metadata and enforces a consistent naming scheme.

2.3 Conversion of IMC data into a common file format

IMC data commonly comes as a vendor controlled .mcd or .txt file. To make the following pipeline
generally applicable to multiplexed imaging data and independent of the vendor format, the raw
files are first converted into an ome.tiff format [4].
For IMC data this one multiplane tiff file per acquisition. Each channel needs to have the
channel label attribute as well as the fluor attribute set. For IMC data the metal name followed
by the isotopic mass are used with the form: (IsotopeShortname)(Mass), e.g. Ir191 for Iridium
isotope 191.


2.4 Generation of the analysis stacks
In the next step the converted .ome.tiff files are converted in a stack format suitable for further
analysis, e.g. using CellProler. In a basic pipeline two stacks will be prepared: a 'Full' stack,
containing all the channels chosen for CellProfiler quantification as well as the 'Ilastik' stack,
containing all the channels selected for the Ilastik pixel classification. It is straight forward to
modify this step to generate additional stacks, e.g. for additional tissue structure segmentations.