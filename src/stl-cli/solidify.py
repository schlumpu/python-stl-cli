import structlog
import vtk
import math
import multiprocessing
from logger import logger

def attach_progress(alg, name):
    last = {"val": -1}
    def callback(caller, event):
        p = int(caller.GetProgress() * 100)
        if p != last["val"]:
            last["val"] = p
            print(f"{name}: {p}%   ", end="\r")
    alg.AddObserver("ProgressEvent", callback)

def make_solid(
    infilename: str,
    outfilename: str,
    smoothing_iterations: int = 20,
    target_grid: int = 128,
    voxel_size: float = None,
    verbose: bool = False,
):
    structlog.contextvars.bind_contextvars(infilename=infilename, outfilename=outfilename)

    try:
        if verbose:
            print(f"Reading STL: {infilename}")

        reader = vtk.vtkSTLReader()
        reader.SetFileName(infilename)
        reader.Update()

        clean = vtk.vtkCleanPolyData()
        clean.SetInputConnection(reader.GetOutputPort())

        triangles = vtk.vtkTriangleFilter()
        triangles.SetInputConnection(clean.GetOutputPort())
        triangles.Update()

        bounds = triangles.GetOutput().GetBounds()
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        dx, dy, dz = xmax-xmin, ymax-ymin, zmax-zmin
        volume = dx*dy*dz

        voxel_size = volume / 2**20
        print(f"Auto voxel size: {voxel_size:.4f}")

        # # Automatic voxel size
        # if voxel_size is None:
        #     largest_dim = max(dx, dy, dz)
        #     voxel_size = largest_dim / target_grid
        #     print(f"Auto voxel size: {voxel_size:.4f}")

        nx, ny, nz = int(dx/voxel_size), int(dy/voxel_size), int(dz/voxel_size)
        if verbose:
            print(f"Voxel grid: {nx} x {ny} x {nz}")

        # Normals
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(triangles.GetOutputPort())
        normals.SetConsistency(True)
        normals.SetAutoOrientNormals(True)
        normals.SetSplitting(False)

        # Signed Distance
        distance = vtk.vtkSignedDistance()
        distance.SetInputConnection(normals.GetOutputPort())
        distance.SetRadius(voxel_size * 2)
        distance.SetBounds(bounds)
        distance.SetDimensions(nx, ny, nz)
        attach_progress(distance, "Signed Distance")
        distance.Update()
        print("SDF complete.")

        # Gaussian smooth
        gauss = vtk.vtkImageGaussianSmooth()
        gauss.SetInputConnection(distance.GetOutputPort())
        gauss.SetStandardDeviation(voxel_size)
        gauss.SetRadiusFactors(1.0,1.0,1.0)
        try:
            gauss.SetNumberOfThreads(multiprocessing.cpu_count())
        except AttributeError:
            pass
        attach_progress(gauss, "Gaussian Smooth")
        gauss.Update()
        print("Gaussian smoothing complete.")

        # Extract surface
        surface = vtk.vtkExtractSurface()
        surface.SetInputConnection(gauss.GetOutputPort())
        surface.SetRadius(voxel_size)

        # Windowed Sinc smoothing
        smooth = vtk.vtkWindowedSincPolyDataFilter()
        smooth.SetInputConnection(surface.GetOutputPort())
        smooth.SetNumberOfIterations(smoothing_iterations)
        smooth.SetPassBand(0.1)
        smooth.NonManifoldSmoothingOn()
        smooth.NormalizeCoordinatesOn()
        try:
            smooth.SetNumberOfThreads(multiprocessing.cpu_count())
        except AttributeError:
            pass
        attach_progress(smooth, "Sinc Smooth")
        smooth.Update()
        print("Sinc smoothing complete.")

        # Write STL
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(outfilename)
        writer.SetFileTypeToBinary()
        writer.SetInputConnection(smooth.GetOutputPort())
        writer.Write()
        print(f"Written solid STL: {outfilename}")

    except Exception:
        logger.exception("make_solid_failed")
        raise
