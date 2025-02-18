
from pathlib import Path
import sys
import shutil

from alive_progress import alive_bar
import pymeshfix

from process import decimate, clean
from logger import logger
from args import args

if args.verbose:
    logger.info('arguments', args=vars(args))

pathlist = Path(f'{args.input}').glob('./**/*.stl')
pathlist = list(pathlist)

columns = shutil.get_terminal_size().columns/2
with alive_bar(len(pathlist), enrich_print=False, length=columns, spinner=None, dual_line=True) as bar:
    for inputpath in pathlist:
        if args.input == '.':
            outputpath = Path.joinpath(Path(args.output), inputpath)
        else:
            outputpath = Path(str(inputpath).replace(args.input, args.output, 1))
        if inputpath == outputpath and not args.overwrite:
            sys.stdout.write(f'confirm overwrite {outputpath} [y/N]')
            choice = input().lower()
            if choice != 'y':
                continue

        bar.text(f'{inputpath}')

        Path(outputpath.parents[0]).mkdir(parents=True, exist_ok=True)
        if args.decimate is not None:
            decimate(
                inputpath, 
                outputpath, 
                decimate_factor=args.decimate, 
                verbose=args.verbose
            )
        if args.clean:
            clean(outputpath, verbose=args.verbose)

        if args.repair:
            # pymeshfix.clean_from_file(str(outputpath), str(outputpath))
            tin = pymeshfix.PyTMesh()
            tin.load_file(str(outputpath))
            
            v, f = tin.return_arrays()
            meshfix = pymeshfix.MeshFix(v, f)
            meshfix.repair()
            meshfix.save(str(outputpath))

            # tin.join_closest_components()
            # tin.fill_small_boundaries()
            # tin.clean()
            # tin.save_file(str(outputpath))
        
        bar()   # update progress bar
