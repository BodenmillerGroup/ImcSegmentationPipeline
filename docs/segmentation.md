# CellProfiler segmentation

Cellprofiler: 2_segment_ilastik

This step will segment the probabilities into masks.

Things to adapt:

1) File list: choose again all files from the `tiffs` folder

2) It is important to check the `IdentifyPrimaryObjects` step, if the segmentation settings are suitable!
    This might vary strongly between cell/tissue/training and needs attention! Use the test mode and try various settings.
    Also note the `smooth` step immediately before: This can be also removed, I just happen get good results with this additional step.

3) Also the `MeasureObjectSizeShape` combined with `FilterObjects` is just some personal preference of mine, feel free to change

4) `IdentifySecondaryObjects`: Here th mask is expanded to the full cell.

5) `Rescale objects`: note that our segmentation was done on 2x upscaled images, this scales the masks down again. Note that potentially also the nuclei mask could be scaled down and further exported and used.

6) The `Default Output Path` does not need to be adapted for this module.


Note1: Seperating mask generation from mask measurement adds modularity and is thus highly recommended, as generating masks is one of the most resource intensive steps.