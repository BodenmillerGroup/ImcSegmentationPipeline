# Changelog

## [3.6, 08-03-2023]

 - allow handling MCD files with missing channel label entries
 - updated links to raw data on Zenodo
 - switched from `MCDFile.metadata` to `MCDFile.schema_xml` to keep up with the latest version of `readimc`

## [3.5, 07-11-2022]

 - exclude hidden files from processing

## [3.4, 02-06-2022]

 - removed `tifffile` version pinning

## [3.3, 27-04-2022]

 - fixed `tifffile` version

## [3.2]

 - sort channels by metal tag when creating the ilastik and full stacks

## [3.1]

 - fixed git submodule issue
 - specified in documentation to restart CellProfiler after setting the plugins

## [3.0]

 - replaced `imctools` by internal `imcsegpipe` package calling [readimc](https://github.com/BodenmillerGroup/readimc)
 - adjusted the pre-processing script in terms of function calls and documentation
 - added script to download raw IMC data from [zenodo.org/record/5949116](https://zenodo.org/record/5949116) and the ilastik pixel classifier from [zenodo.org/record/6043544](https://zenodo.org/record/6043544)
 - moved the hot pixel filtering step from the CellProfiler pipelines into the `create_analysis_stacks` function call
 - removed the default `tiffs` folder. All files related to ilastik pixel classification are stored in the `ilastik` folder and image crops are stored in `crops`
 - hot pixel filtered images are directly written out to `cpout/images`
 - segmentation masks are directly written out to `cpout/masks` in the second pipeline and read in as objects in the last pipeline
 - pixel probabilities are downscaled in the second pipeline and directly written into `cpout/probabilites`
 - cell segmentation is performed on downscaled pixel probabilities

## [2.3]

 - Bugfixes: `1_prepare_ilastik`: Removed special characters from pipeline comments as this caused encoding issues.

## [2.1]

 - Bugfixes: `1_prepare_ilastik`: Fix range to 0-1 for mean image, preventing out of range errors

## [2.0]

 - Change to imctools v2: Changes the structure of the folder to the new format, changing the naming of the .ome.tiff files
 - Change to Cellprofiler v4: Requires the use of the ImcPluginsCP master branch or a release > v.4.1
 - Updated documentation
 - Adds var_Cells.csv containing metadata for the measurements
 - Adds panel to cpout folder
