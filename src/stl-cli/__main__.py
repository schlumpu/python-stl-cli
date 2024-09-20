
import argparse
from pathlib import Path

from process import process
from logger import logger

parser = argparse.ArgumentParser(
    prog='stl-cli',
    description='Decimate and remove metadata from STL files',
    epilog=''
)
parser.add_argument('-i', '--input', default='.', help='input folder')
parser.add_argument('-o', '--output', default=None, help='output folder')
parser.add_argument('-d', '--decimate', type=float, default=0.5, 
                                                        help='decimate factor')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                                                        help='display logging')
# TODO:
parser.add_argument('-c', '--clean', action='store_true', default=False,
                                                        help='remove metadata')
parser.add_argument('-y', '--overwrite', action='store_true', default=False,
                                            help='confirm inplace processing')
args = parser.parse_args()

args.input = args.input.rstrip('/')
args.output = args.output if args.output else args.input
args.output = args.output.rstrip('/')

if args.decimate<0 or args.decimate>1:
    raise ValueError('args.decimate')
if args.verbose:
    logger.info('arguments', args=vars(args))

pathlist = Path(f'{args.input}').glob('./**/*.stl')
for inputpath in pathlist:
    if args.input == '.':
        outputpath = Path.joinpath(Path(args.output), inputpath)
    else:
        outputpath = Path(str(inputpath).replace(args.input, args.output, 1))
    if inputpath != outputpath and not args.overwrite:
        pass
        # TODO: confirm overwrite for each file
    Path(outputpath.parents[0]).mkdir(parents=True, exist_ok=True)
    process(
        inputpath, 
        outputpath, 
        decimate_factor=args.decimate, 
        verbose=args.verbose
    )
