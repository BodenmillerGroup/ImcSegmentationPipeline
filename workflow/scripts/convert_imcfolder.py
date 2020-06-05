from imctools.converters import mcdfolder2imcfolder
import pathlib
import traceback

if __name__ == '__main__':
    fn_zip = snakemake.input.fn_zip
    fol_ome = snakemake.params.fol_ome
    try:
        mcdfolder2imcfolder.mcdfolder_to_imcfolder(
	        str(fn_zip), output_folder=str(fol_ome),
            create_zip=False)
    except:
        fn_failed = pathlib.Path(fol_ome) / (pathlib.Path(fn_zip).stem + '.failed')
        with open(fn_failed, 'w') as f:
            traceback.print_exc(file=f)

