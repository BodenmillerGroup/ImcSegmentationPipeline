from imctools.scripts import convertfolder2imcfolder
import pathlib
import traceback

if __name__ == '__main__':
    fn_zip = snakemake.input.fn_zip
    fol_ome = snakemake.params.fol_ome
    try:
        convertfolder2imcfolder.convert_folder2imcfolder(str(fn_zip),
                out_folder=str(fol_ome),
                dozip=False)
    except:
        fn_failed = pathlib.Path(fol_ome) / (pathlib.Path(fn_zip).stem + '.failed')
        with open(fn_failed, 'w') as f:
            traceback.print_exc(file=f)


