# Cellprofiler: 3_measure_mask

This step is not necessary for `HistoCat` only analysis. If `HistoCat` should be used, use the `Generate the histocat folder with masks` section below.

#### 3_measure_mask_basic

This module measures without considering spillover correction.

1) File list: choose again all files from the `tiffs` folder

2) View Output settings: set the `Default output folder` to the `cpout` folder and the
    `Default input folder` to the `cpint` folder.

3) Metadata: update - this will automatically merge the mcd metadata .csv generated earlier in the script with your images.

4) Names and types: click update

5) `Measure Object Intensity Multichannel`: Adapt the channel numbers. Check the `_full.csv` files in the `tiffs` folder to see how many channels the stack have and adapt accordingly.

6) `Measure Image Intensity Multichannel`: Adapt the channel numbers. Check the `_full.csv` files in the `tiffs` folder to see how many channels the stack have and adapt accordingly.

Notes:
- In this pipeline all the intesities are scaled by `1/(2**16)`
- The mapping between channel number c1, c2, c3 corresponds to the position in the `_full.csv`s found in the `tiffs` folder.
- The original acquisition description, acquisition frequencies etc can be found in the `Image.csv` output as `Metdata_...` columns.
- This outputs a lot of measurements that are acutally of little interest - usually we only look at `meanintensity` per channel and cell.
    To reduce the outputs, select in `Export To Spreadsheet` -> `Select Measurements to Export` -> Only the measurements you want (usually all Image measurements and only the `MeanIntensity` fullstack measurements).
- The `FullStack` can also be not measured, as it is almost identical to the `FullStackFiltered`.

#### 3_measure_mask_compensated
This will also have a spillover corrections step - stay tuned!

