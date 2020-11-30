"""
Create a new project from scratch for 3 class cell segmentation
pixel classification using multichannel h5 files.
./ilastik-1.1.7-Linux/bin/python train_headless.py MyNewProject.ilp "/folder/*"
Example usage:
"""
from __future__ import print_function
import pathlib
import os

DEFAULT_LABEL_NAMES = ('CellCenter', 'CellBorder', 'Background')

def main():
    # Cmd-line args to this script.
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("new_project_name")
    parser.add_argument("raw_data_folder")
    parsed_args = parser.parse_args()

    project_file = pathlib.Path(parsed_args.new_project_name)
    parent_folder = project_file.parent
    raw_files = [str(p)
                  for p in pathlib.Path(parsed_args.raw_data_folder).glob('*.h5')]

    # FIXME: This function returns hard-coded features for now.
    feature_selections = prepare_feature_selections()

    generate_untrained_project_file(
        project_file.resolve(),
        raw_files,
        feature_selections,
        DEFAULT_LABEL_NAMES
    )
    print("DONE.")


# Don't touch these constants!
ScalesList = [0.3, 0.7, 1, 1.6, 3.5, 5.0, 10.0]
FeatureIds = [
    "GaussianSmoothing",
    "LaplacianOfGaussian",
    "GaussianGradientMagnitude",
    "DifferenceOfGaussians",
    "StructureTensorEigenvalues",
    "HessianOfGaussianEigenvalues",
]


def prepare_feature_selections():
    """
    Returns a matrix of hard-coded feature selections.
    To change the features, edit the lines below.
    """
    import numpy

    # #                    sigma:   0.3    0.7    1.0    1.6    3.5    5.0   10.0
    # selections = numpy.array( [[False, False, False, False, False, False, False],
    #                            [False, False, False, False, False, False, False],
    #                            [False, False, False, False, False, False, False],
    #                            [False, False, False, False, False, False, False],
    #                            [False, False, False, False, False, False, False],
    #                            [False, False, False, False, False, False, False]] )

    # Start with an all-False matrix and apply the features we want.
    selections = numpy.zeros((len(FeatureIds), len(ScalesList)), dtype=bool)

    selections[:, 1: ] = True
    return selections


def generate_untrained_project_file(
    new_project_path, raw_data_paths, feature_selections, label_names
):
    """
    Create a new project file from scratch, add the given raw data files,
    inject the corresponding labels, configure the given feature selections,
    and (if provided) override the classifier type ('factory').
    Finally, request the classifier object from the pipeline (which forces training),
    and save the project.
    new_project_path: Where to save the new project file
    raw_data_paths: A list of paths to the raw data images to train with
    label_data_paths: A list of paths to the label image data to train with
    feature_selections: A matrix of bool, representing the selected features
    labels: list of label names

    """
    import ilastik_main as app
    from ilastik.workflows.pixelClassification import PixelClassificationWorkflow
    from ilastik.applets.dataSelection.opDataSelection import RelativeFilesystemDatasetInfo
    ##
    ## CREATE PROJECT
    ##

    # Manually configure the arguments to ilastik, as if they were parsed from the command line.
    # (Start with empty args and fill in below.)
    ilastik_args = app.parse_args([])
    ilastik_args.new_project = new_project_path
    ilastik_args.headless = True
    ilastik_args.workflow = "Pixel Classification"

    shell = app.main(ilastik_args)
    assert isinstance(shell.workflow, PixelClassificationWorkflow)

    ##
    ## CONFIGURE FILE PATHS
    ##

    data_selection_applet = shell.workflow.dataSelectionApplet
    input_infos = [RelativeFilesystemDatasetInfo(filePath=path) for path
                    in raw_data_paths]

    opDataSelection = data_selection_applet.topLevelOperator

    existing_lanes = len(opDataSelection.DatasetGroup)
    opDataSelection.DatasetGroup.resize(max(len(input_infos), existing_lanes))
    # Not sure if assuming role_index = 0 is allways valid
    role_index = 0
    for lane_index, info in enumerate(input_infos):
        if info:
            opDataSelection.DatasetGroup[lane_index][role_index].setValue(info)

    ##
    ## APPLY FEATURE MATRIX (from matrix above)
    ##

    opFeatures = shell.workflow.featureSelectionApplet.topLevelOperator
    opFeatures.Scales.setValue(ScalesList)
    opFeatures.FeatureIds.setValue(FeatureIds)
    opFeatures.SelectionMatrix.setValue(feature_selections)

    ##
    ## CUSTOMIZE CLASSIFIER TYPE
    ##

    opPixelClassification = shell.workflow.pcApplet.topLevelOperator

    ##
    ## READ/APPLY LABEL VOLUMES
    ##

    opPixelClassification.LabelNames.setValue(label_names)

    # save project file (includes the new classifier).
    shell.projectManager.saveProject(force_all_save=False)


if __name__ == "__main__":
    main()