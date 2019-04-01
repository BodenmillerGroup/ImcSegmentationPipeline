# A flexible  image segmentation pipeline for heterogneous multiplexed tissue images based on pixel classification

I am currently remodelling the whole description/procedure and would be happy for any feedback!

#####
Please consider the current state of this repository as 'Beta'.
####

Notable changes to older version is change to CellProfiller 3 and that the ImcPluginsCP work now with any CP3 installation without special installation procedure.

The pipline is based on CellProfiler (http://cellprofiler.org/, v1.3.5) for segmentation and Ilastik (http://ilastik.org/) for
for pixel classification. It is streamlined by using the specially developped imctools python package (https://github.com/BodenmillerGroup/imctools) 
package as well as custom CellProfiler modules (https://github.com/BodenmillerGroup/ImcPluginsCP, develop-cp3 branch!).

This pipline was developped in the Bodenmiller laboratory of the University of Zurich (http://www.bodenmillerlab.org/) to segment hundereds of highly multiplexed
imaging mass cytometry (IMC) images. However we think it might also be usefull for other multiplexed imaging techniques.


The document to start can be found at 'scripts/imc_preprocessing.ipynb' (https://nbviewer.jupyter.org/github/BodenmillerGroup/ImcSegmentationPipeline/blob/development/scripts/imc_preprocessing.ipynb).
The pdf found in 'Documentation/201709_imctools_guide.pdf' is still conceptually valid, however the installation procedures described are outdated. Please follow the instructions in the imc_preprocessing.ipynb document!

We freely share this pipeline in the hope that it will be usefull for others to perform high quality image segmentation and serve as a basis to develop more complicated
open source IMC image processing workflows. In return we would like you to be considerate and give us and others feedback if you find a bug or issue  and raise a Github Issue on the affected projects or on this page.
