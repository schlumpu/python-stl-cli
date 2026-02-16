
from matplotlib.pyplot import contour
import vtk
import pymeshfix
import structlog

from logger import logger

def decimate(
        infilename:str, 
        outfilename:str, 
        decimate_factor:float=0.5, 
        verbose:bool=False
    ):

    structlog.contextvars.bind_contextvars(
        infilename=str(infilename),
        outfilename=str(outfilename),
        decimate_factor=decimate_factor
    )
    if verbose:
        logger.info('decimate')

    try:
        stlReader = vtk.vtkSTLReader()
        stlReader.SetFileName(infilename)
        stlReader.Update()
        inputPoly = stlReader.GetOutput()

        # decimate = vtk.vtkDecimatePro()
        # decimate.PreserveTopologyOn()
        decimate = vtk.vtkQuadricDecimation()
        decimate.SetInputData(inputPoly)
        decimate.SetTargetReduction(decimate_factor)

        stlWriter = vtk.vtkSTLWriter()
        stlWriter.SetFileName(outfilename)
        stlWriter.SetFileTypeToBinary()
        stlWriter.SetInputConnection(decimate.GetOutputPort())
        stlWriter.Write()
    except Exception as e:
        logger.exception('exception')


def clean(infilepath: str, verbose:bool=False):
    # https://en.wikipedia.org/wiki/STL_(file_format)
    try: 
        if verbose:
            with open(infilepath, 'rb') as f:
                meta = f.read(80)   # first 80 bytes are the STL header
                logger.info('clean', meta=meta)
        with open(infilepath, 'r+b') as f:
            # f.seek(0)
            f.write(bytearray([0]*80))
    except Exception as e:
        logger.exception('exception')

def repair(infilepath: str, outfilepath: str, verbose:bool=False):
    try:
        # pymeshfix.clean_from_file(str(outputpath), str(outputpath))
        tin = pymeshfix.PyTMesh()
        tin.load_file(str(infilepath))
        
        v, f = tin.return_arrays()
        meshfix = pymeshfix.MeshFix(v, f)
        meshfix.repair()
        meshfix.save(str(outfilepath))

        # tin.join_closest_components()
        # tin.fill_small_boundaries()
        # tin.clean()
        # tin.save_file(str(outputpath))
    except Exception as e:
        logger.exception('exception')


def vtk_progress(caller, event):
    progress = caller.GetProgress()  # 0.0 → 1.0
    print(f"Voxelization progress: {progress * 100:.1f}%", end="\r")

def make_solid(
    infilename: str,
    outfilename: str,
    voxel_size: float = 0.5,
    smoothing_iterations: int = 30,
    verbose: bool = False,
):
    structlog.contextvars.bind_contextvars(
        infilename=str(infilename),
        outfilename=str(outfilename),
        voxel_size=voxel_size,
    )

    if verbose:
        logger.info("make_solid")

    try:
        # Read STL
        print(f"Reading STL: {infilename}")
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(infilename))
        reader.Update()

        print(f"Decimating mesh to reduce complexity...")
        # Clean & triangulate
        clean = vtk.vtkCleanPolyData()
        clean.SetInputConnection(reader.GetOutputPort())

        print(f"Triangulating mesh...")
        triangles = vtk.vtkTriangleFilter()
        triangles.SetInputConnection(clean.GetOutputPort())
        triangles.Update()

        print(f"Computing bounds and voxelization parameters...")
        # Compute bounds
        bounds = triangles.GetOutput().GetBounds()
        xmin, xmax, ymin, ymax, zmin, zmax = bounds

        dx = xmax - xmin
        dy = ymax - ymin
        dz = zmax - zmin
        print(f"dx: {dx}, dy: {dy}, dz: {dz}")

        volume = dx * dy * dz
        print(f"Bounding box volume: {volume}")
        voxel_size = volume/2**20
        print(f"Calculated voxel size: {voxel_size}")

        # Convert voxel size → grid resolution
        nx = int(dx / voxel_size)
        ny = int(dy / voxel_size)
        nz = int(dz / voxel_size)
        print(f"Voxel grid dimensions: nx={nx}, ny={ny}, nz={nz}")

        # # Voxelization (implicit surface)
        # modeller = vtk.vtkImplicitModeller()
        # modeller.SetInputConnection(triangles.GetOutputPort())
        # modeller.SetModelBounds(bounds)
        # modeller.SetSampleDimensions(nx, ny, nz)
        # modeller.SetMaximumDistance(voxel_size * 2)
        # modeller.SetAdjustDistance(True)
        # print(f"Starting voxelization...")
        # modeller.AddObserver("ProgressEvent", vtk_progress)
        # modeller.Update()
        # print(f"Voxelization complete.")

        # # Extract surface (marching cubes)
        # contour = vtk.vtkContourFilter()
        # contour.SetInputConnection(modeller.GetOutputPort())
        # contour.SetValue(0, voxel_size * 0.5)
        # contour.Update()
        # print("Contour points:", contour.GetOutput().GetNumberOfPoints())
        # print(f"Extracting surface with marching cubes...")

        # # # Optional smoothing (MeshMixer-like polish)
        # # smooth = vtk.vtkSmoothPolyDataFilter()
        # # smooth.SetInputConnection(contour.GetOutputPort())
        # # smooth.SetNumberOfIterations(smoothing_iterations)
        # # smooth.SetRelaxationFactor(0.1)
        # # smooth.FeatureEdgeSmoothingOff()
        # # smooth.BoundarySmoothingOn()
        # # smooth.Update()
        # # print(f"Smoothing complete.")

        # Convert mesh to point cloud with normals
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(triangles.GetOutputPort())
        normals.SetConsistency(True)
        normals.SetAutoOrientNormals(True)
        normals.SetSplitting(False)
        normals.Update()

        # Signed distance field
        distance = vtk.vtkSignedDistance()
        distance.SetInputConnection(normals.GetOutputPort())
        distance.SetRadius(voxel_size * 2)
        distance.SetBounds(bounds)
        distance.SetDimensions(nx, ny, nz)
        distance.Update()

        # Extract surface
        surface = vtk.vtkExtractSurface()
        surface.SetInputConnection(distance.GetOutputPort())
        surface.SetRadius(voxel_size)
        surface.Update()

        smooth = vtk.vtkWindowedSincPolyDataFilter()
        smooth.SetInputConnection(surface.GetOutputPort())
        smooth.SetNumberOfIterations(smoothing_iterations)
        smooth.SetPassBand(0.1)
        smooth.NonManifoldSmoothingOn()
        smooth.NormalizeCoordinatesOn()
        smooth.Update()

        # Write STL
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(str(outfilename))
        writer.SetFileTypeToBinary()
        writer.SetInputConnection(smooth.GetOutputPort())
        writer.Write()
        print(f"Written solid STL: {outfilename}")

    except Exception:
        logger.exception("exception")