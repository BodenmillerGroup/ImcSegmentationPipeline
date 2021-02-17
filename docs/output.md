# The output of the IMC segmentation pipeline

Pipeline output

The pipeline output is all in the `cpout` folder.

Files and folders:
- Image.csv: Image level metadata
- var_Image.csv: Metadata for the colums in Image.csv.
    This contains also metadata from the IMC such as acquisition coordinates.

- {object}.csv: eg cell.csv, contains cell slice level measurements
- var_{object}.csv: eg var_cell.csv: contains metadata for the object measurements

- panel.csv: a copy of the panel used for the input

- Object relationships.csv: Object neighbourhood and other relationships

- Experiment.csv: Metadata about the actual measurement run (eg pipeline used,...)

Note that the `description` image name can be found in the `..._Acquisition_meta.csv` generated together with the ome tiffs
as well as in the `cpinp` folder later in the script.
After analysis the `Image.csv` metadata file generated in Cellprofiller will also contain the `Description` as well as other important metadata for each
image, such as acquisition frequency, time, location etc.