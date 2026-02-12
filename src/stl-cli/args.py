
import argparse

parser = argparse.ArgumentParser(
    prog='stl-cli',
    description='Decimate and remove metadata from STL files',
    epilog=''
)
parser.add_argument('-i', '--input', default='.', 
                    help='input folder; if ommitted, current directory')
parser.add_argument('-o', '--output', default=None, 
                    help='output folder; if same as input, will overwrite files; if ommitted, will use input folder')
parser.add_argument('-d', '--decimate', type=float, default=0.0, 
                    help='decimate factor, from 0 to 1, 0 means no decimation')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='display verbose logs')
parser.add_argument('-c', '--clean', action='store_true', default=False,
                    help='remove metadata')
parser.add_argument('-y', '--overwrite', action='store_true', default=False,
                    help='confirm inplace processing; if not set, will prompt for confirmation')
parser.add_argument('-r', '--repair', action='store_true', default=False,
                    help='repair (remove supports, experimental)')
parser.add_argument('-s', '--make-solid', type=float, default=0.0,
                    help='make solid (MeshMixer-style); value is voxel size, 0 disables stage')
parser.add_argument('-m', '--max-file-size', type=float, default=0.0,
                    help='attempt to reduce file size to provided value (in MB); will overwrite decimate value')

args = parser.parse_args()

args.input = args.input.rstrip('/')
args.output = args.output if args.output else args.input
args.output = args.output.rstrip('/')

if args.max_file_size<0:
    raise ValueError('args.decimate')

if args.decimate<0 or args.decimate>1:
    raise ValueError('args.decimate')

if args.make_solid<0:
    raise ValueError('args.make_solid')