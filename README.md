
# TODO:
    [ ] [https://pymeshfix.pyvista.org/](https://pymeshfix.pyvista.org/)

# Convert .obj to .stl
```bash
    # install assimp
    sudo apt update
    sudo apt install -y assimp-utils libassimp5

    # apply to all .stl files in subfolder
    find ./ -type f -name "*.obj" -exec assimp export "{}" "{}".stl \;
```
