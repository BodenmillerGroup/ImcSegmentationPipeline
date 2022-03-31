# Final output files

The IMC Segmentation Pipeline produces a number of output files during pre-processing, ilastik pixel classification, segmentation and measurement. 
They are listed below:

    analysis
    |
    ├── cpinp 
        ├── acquisition_metadata.csv 
        ├── full_channelmeta.csv
        ├── probab_channelmeta_manual.csv
    ├── cpout      
        ├── images
            ├── {XYZ}_s0_a1_ac_full.tiff
            ├── {XYZ}_s0_a1_ac_full.csv
            ├── ...
        ├── masks
            ├── {XYZ}_s0_a1_ac_ilastik_s2_Probabilities_mask.tiff
            ├── ...
        ├── probabilities
            ├── {XYZ}_s0_a1_ac_ilastik_s2_Probabilities_s1.tiff
            ├── ...
        ├── cell.csv
        ├── Experiment.csv
        ├── Image.csv
        ├── Object relationships.csv
        ├── panel.csv
        ├── var_cell.csv
        ├── var_Image.csv
    ├── crops 
        ├── {XYZ}_s0_a1_ac_ilastik_x{X}_y{Y}_w{W}_h{H}.tiff
        ├── ...
    ├── histocat
        ├── {XYZ}_s0_a1_ac
            ├── {channel_label}_{channel_name}.tiff
            ├── ...
        ├── ...
    ├── ilastik
        ├── {XYZ}_s0_a1_ac_ilastik.tiff
        ├── {XYZ}_s0_a1_ac_ilastik.csv
        ├── {XYZ}_s0_a1_ac_ilastik_s2.h5
        ├── {XYZ}_s0_a1_ac_ilastik_s2_Probabilities.tiff
        ├── ...
    ├── ometiff
        ├── {XYZ}
            ├── {XYZ}_s0_a1_ac.ome.tiff
            ├── {XYZ}_s0_a1_ac.ome.csv
            ├── ...
            ├── {XYZ}_s0_p1_pano.png
            ├── ...
            ├── {XYZ}_s0_slide.png
            ├── {XYZ}_schema.xml
    

Here `XYZ` indicates the sample name.

## The main output folder

The `cpout` folder contains all relevant output files:

* `cpout/images`: contains the hot pixel filtered full stacks for analysis as well as `.csv` files indicating the channel order. 
* `cpout/masks`: contains single-channel segmentation masks in 16-bit `.tiff` format. Segmentation masks are single-channel images that match the input images in size, with non-zero grayscale values indicating the IDs of segmented objects. 
* `cpout/probabilities`: contains 3 channel images in 16-bit `.tiff` format representing the downscaled pixel probabilities after Ilastik pixel classification.
* `cpout/cell.csv`: contains features (columns) for each cell (rows).
* `cpout/Experiment.csv`: contains metadata related to the CellProfiler version used.
* `cpout/Image.csv`: contains image-level measurements (e.g. channel intensities) and acquisition metadata. 
* `cpout/Object relationships.csv`: contains neighbor information in form of an edge list between cells.
* `cpout/panel.csv`: a copy of the panel file used for the experiment.
* `cpout/var_cell.csv`: contains feature metadata for all single-cell features.
* `cpout/var_Image.csv`: contains feature metadata for all image features.

## The CellProfiler input folder

The `cpinp` folder contains metadata files for CellProfiler input:

* `cpinp/acquisition_metadata.csv`: containing acquisition metadata.
* `cpinp/full_channelmeta.csv`: containing full stack channel metadata.
* `cpinp/probab_channelmeta_manual.csv`: containing probability stack channel metadata.

## Ilastik folder

The following folders contain files for Ilastik pixel classification:

* `analysis/ilastik`: contains the Ilastik stacks (`{XYZ}_s0_a1_ac_ilastik.tiff`), matched `.csv` files indicating the correct channel order (`{XYZ}_s0_a1_ac_ilastik.csv`), the upscaled ilastik stacks in `.h5` format (`XYZ}_s0_a1_ac_ilastik_s2.h5`) and upscaled pixel probabilities (`{XYZ}_s0_a1_ac_ilastik_s2_Probabilities.tiff`).
* `analysis/crops`: this folder contains the image crops of the Ilastik stack in `.h5` format for Ilastik training.

## Image data folders

The following folders contain data in different formats for use with other software or [histoCAT](https://bodenmillergroup.github.io/histoCAT/).

* `analysis/ometiff`: contains individual folders (one per sample) of which each contains multiple `.ome.tiff` files (one per acquisition).  
* `analysis/histocat`: contains individual folders (one per acquisition) of which each contains multiple single-channel `.tiff` files for upload to histoCAT.  