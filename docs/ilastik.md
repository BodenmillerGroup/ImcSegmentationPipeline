# Ilastik pixel classification

## Prepare images for pixel classification

This is a CellProfiler module

In this module we prepare the data for Ilastik pixel classification, by first removing strong outlier pixels, then scaling the images 2x and then taking random 500x500 crops to do the train the pixel classifier.

Note: for large datasets 250x250 crops or smaler should suffice!

The following parts of this module need to be adapted:

1) File list: choose all files in the `tiff` subfolder

2) Click on default output settings and specify the Default input 


Default Output Folder: Choose the `ilastik` subfolder

No further parts need to be adapted.
In our 16 core computer this step takes ca 5 min for the example dataset.

**TODO: more detailed explanation what to do and what the steps are**

1. hot pixel removal
2. Summarize stack: What, why and does it matter for the pixel-classification?


## Train a pixel classifier

This uses the random crops generated in the last step.

1) Make a new `pixel classification project`. -> An example project that works with the example data can be found in the 'analysis' subfolder.

2) Add the `.h5` random crops: Raw data -> Add Seperate Images -> Select all `.h5` images in the `ilastik` subfolder.

3) Proceed to `Feature Selection`

For a detailed overview on ilastik pixel classification refer to the [manual](https://www.ilastik.org/documentation/pixelclassification/pixelclassification).

4) Select suitable features (or just everything sigma >= 1 pixels) **What do you mean?**

5) Proceed to the classification:

    - Add 3 labels:
        - 1: Nuclei
        - 2: Cytoplasma/membrane
        - 3: Background
        - -> For large datasets adding the labels can take a while
    - Start labeling:
        - The box next to `Input Data` can change the channels. What each channel corresponds to can be seen when looking in any of the `..._ilastik.csv` files in the `tiff` folder. The 0 channel correspond to the sum of all channels, very usefull to label the background.
        - Use window leveling change the contrast. Right click on the `Input Data` -> `Adjust Thresholds` is also very usefull
        - Label opiniated: If you see in the nucleus channel that two nuclei are stuck together but have a faint dip in intensity in between, label this as 2: Cytoplasma. Encyrcle nuclei with Cytoplasma
        - Diseable `Live Update` for performance
        - Frequently check the `Uncertainties`: This indicates which pixels the classifier profits most if they are labeled. A well trained classifier has low uncertainty within class regions (e.g. Nuclei) and high uncertainty at class borders (e.g. between nuclei and cytoplasma).

    - If you think the classifier is well trained, export the probabilities:
        - Export Settings -> Source: Probabilities -> Choose Export Image Settings:
            - Convert to datatype: Unsigned Integer 16 bit
            - Renormalize: check
            - Format: Tiff
            - File: leave default
        - Export all: This generates `_Probabilities.tiff` in the `ilastik` folder. They can be checked using any image viewer
            - To generate uncertainty maps (good to identify regions that need training),
            run the `Convert probabilities to uncertainties` section `#For training` below. This will put uncertainties in the uncertainty folder.
            -> Well trained classifiers have low uncertainty (transparent) everywhere but at class borders which should be white.

        - Optional: Train again regions with high uncertainty, then proceed.

        - Batch processing: -> Select raw data files -> select all `_s2.h5` files in the `tiff` folder. (sort by filetype, select all `H5` files).
            -> This step takes a while and is computationally intensive!
            -> Ca 15 min on 10 cores on the example data

        - Optional: use the below probability to uncertainty `#For the data` to convert all proabilities to uncertainties, check if there are any regions of high uncertainty and optionally crop the corresponding image part in imagej and add it to the training data.
        - Note: store the `ilastik` folder with all the random crops and the trained classifier for reproducibility reasons.
        
        - A trained