
import vtk
import structlog

from logger import logger

def process(infilename:str, outfilename:str, decimate_factor=0.5, verbose=False):

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