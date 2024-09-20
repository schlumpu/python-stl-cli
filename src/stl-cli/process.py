
import vtk
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