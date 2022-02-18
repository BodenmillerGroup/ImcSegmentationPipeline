# Cell segmentation

To segment individual objects (here these are cells) in images, the following CellProfiler pipeline reads in pixel probabilities (generated in [Ilastik pixel classification](ilastik.md)) for segmentation.
Set up the pipeline by importing the `resources/pipelines/2_segment_ilastik.cppipe` pipeline into CellProfiler and perform following steps:

1. Drag and drop the `analysis/ilastik` folder into the `Images` window.
2. In the `Output Settings` adjust the `Default Output Folder` to `analysis/cpout`.  

The following steps are part of the pipeline:

1. The files ending with `_Probabilities.tiff` are read in as part of the `NamesAndTypes` module.
2. In `ColorToGray` these 3 channel probability images are split into their individual channels: channel 1 - nucleus; channel 2 - cytoplasm; channel 3 - background.  
3. The nulcear and cytoplasmic channels are summed up to form a single channel indicating the full cell probability.  
4. The nuclear probabilities are smoothed using a gaussian filter. This step can be adjusted or removed to increase segmentation success. 
5. The `IdentifyPrimaryObjects` is crucial to correctly identifying nuclei. Use the test mode and enable the "eye" icon next to the module to observe if nuclei are correctly segmented. The advanced settings can be adjusted to improve segmentation.  
6. The `MeasureObjectSizeShape` module measures the size of the nuclei and the `FilterObjects` filters nuclei below a specified thresholds. At this point the images are still upscaled by a factor of 2 and the object size will differ in the downscaled segmentation mask. 
7. The `IdentifySecondaryObjects` module expands from the identified nuclei to the border of the full cell probability generated in step 3 or until touching the neighboring cell. This step generates the upscaled segmentation masks.
8. The upscaled segmentation masks are downscaled by a factor of 0.5 to match the initial image dimensions. 
9. The downscaled segmentation masks are converted to 16-bit images. 
10. The images containing pixel probabilities are downscaled by a factor of 0.5 to match the initial image dimensions.
11. The downscaled segmentation masks are written out as 16-bit, single-channel `.tiff` images to the `analysis/cpout/masks` folder.
12. The downscaled pixel probability images are written out as 16-bit, 3 channel `.tiff` images to the `analysis/cpout/probabilities` folder.

## Output