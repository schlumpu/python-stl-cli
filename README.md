
# Install
```bash
$git clone <repository>
$cd <repository>
$python3 -m venv venv
$pip install -r requirements.txt
```

# Run
```bash
$python src/stl-cli/ -h
usage: stl-cli [-h] [-i INPUT] [-o OUTPUT] [-d DECIMATE] [-v] [-c] [-y] [-r]

Decimate and remove metadata from STL files

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        input folder; if ommitted, current directory
  -o OUTPUT, --output OUTPUT
                        output folder; if same as input, will overwrite files; if ommitted, will use input folder
  -d DECIMATE, --decimate DECIMATE
                        decimate factor, from 0 to 1, 0 means no decimation
  -v, --verbose         display verbose logs
  -c, --clean           remove metadata
  -y, --overwrite       confirm inplace processing; if not set, will prompt for confirmation
  -r, --repair          repair (remove supports, experimental)

```

### Examples

# Convert .obj to .stl
Will convert to text stl; python-stl-cli with a -d factor of 0 can be used to convert to binary stl.
```bash
    # install assimp
    sudo apt update
    sudo apt install -y assimp-utils libassimp5

    # apply to all .stl files in subfolder
    find ./ -type f -name "*.obj" -exec assimp export "{}" "{}".stl \;
```

# TODO:
    [ ] [https://pymeshfix.pyvista.org/](https://pymeshfix.pyvista.org/)