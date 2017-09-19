# A flexible  image segmentation pipeline for heterogneous multiplexed tissue images based on pixel classification

This pipline was developped in the Bodenmiller laboratory of the University of Zurich (http://www.bodenmillerlab.org/) to segment hundereds of highly multiplexed
imaging mass cytometry (IMC) images. However we think it might also be usefull for other multiplexed imaging techniques.

The pipline is based on CellProfiler (http://cellprofiler.org/) for segmentation and Ilastik (http://ilastik.org/) for
for pixel classification. It is streamlined by using the specially developped imctools python package (https://github.com/BodenmillerGroup/imctools) 
package as well as custom CellProfiler modules (https://github.com/BodenmillerGroup/ImcPluginsCP).

In our lab we use this pipeline setup on Ubuntu (example setup file for Ubuntu 14.04 can be found in setup_configurations/). However it should also be possible to set it up on a Windows or MacOS machine.

Please read the draft document describing the pipeline in the 'Documents' folder for further information about the pipeline and consider the example configuration jupyter file (configuration_files/201709_imctutorial.ipynb) and Cellprofiler Pipeline examples.

We freely share this pipeline in the hope that it will be usefull for others to perform high quality image segmentation and serve as a basis to develop more complicated
open source IMC image processing workflows. In return we would like you to be considerate and give us and others feedback if you find a bug or issue  and raise a Github Issue on the affected projects or on this page.

This site will soon be updated with more informations!
