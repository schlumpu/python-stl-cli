
import argparse

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