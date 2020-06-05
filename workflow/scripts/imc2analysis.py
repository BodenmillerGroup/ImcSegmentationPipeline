import multiprocessing
import pathlib
import traceback

import tifffile
from imctools.converters import ome2analysis


def check_minsize(img, minsize):
    with tifffile.TiffFile(img) as im:
        size = im.series[0].shape[1:]
    return min(size) > minsize


if __name__ == '__main__':
    fol_ome = snakemake.input.fol_ome
    panel = snakemake.input.panel
    fol_out = snakemake.output[0]
    column_used = snakemake.params.column_used
    column_metal = snakemake.params.column_metal
    suffix = snakemake.params.suffix
    min_imgsize = snakemake.params.min_imgsize

    threads = snakemake.threads


    def convert_img(path):
        basename = path.name.rstrip('.ome.tiff')
        pathlib.Path(fol_out).mkdir(parents=True, exist_ok=True)
        if not check_minsize(str(path), min_imgsize):
            print('Skip: ', basename, 'as image to small.')
            return
        try:
            ome2analysis.omefile_2_analysisfolder(str(path),
                                                  output_folder=fol_out,
                                                  basename=basename+suffix,
                                                  panel_csv_file=panel,
                                                  metalcolumn=column_metal,
                                                  usedcolumn=column_used,
                                                  dtype='uint16')
        except:
            print('Error in', path)
            traceback.print_exc()


    with multiprocessing.Pool(snakemake.threads) as pool:
        pool.map(convert_img, pathlib.Path(fol_ome).rglob('*.ome.tiff'))
