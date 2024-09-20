
from pathlib import Path
import sys

from process import decimate, clean
from logger import logger
from args import args

if args.verbose:
    logger.info('arguments', args=vars(args))

pathlist = Path(f'{args.input}').glob('./**/*.stl')
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
    Path(outputpath.parents[0]).mkdir(parents=True, exist_ok=True)
    if args.decimate:
        decimate(
            inputpath, 
            outputpath, 
            decimate_factor=args.decimate, 
            verbose=args.verbose
        )
    if args.clean:
        clean(outputpath, verbose=args.verbose)
