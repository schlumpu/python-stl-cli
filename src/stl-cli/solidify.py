
import structlog
import open3d as o3d
import numpy as np

import os
import multiprocessing
import math

def make_solid(
    infilename: str,
    outfilename: str,
    verbose: bool = False,
):
    
    cpu_count = math.ceil(multiprocessing.cpu_count()/2)
    os.environ['OMP_NUM_THREADS'] = str(cpu_count)
    
    number_of_sample_points = 2**19     # solid accuracy
    density_depth = 16                  # solid accuracy
    keep_quantile = 0.0

    structlog.contextvars.bind_contextvars(infilename=infilename, outfilename=outfilename)

    # Read mesh
    mesh = o3d.io.read_triangle_mesh(infilename)
    mesh.compute_vertex_normals()

    # Sample points
    pcd = mesh.sample_points_uniformly(number_of_points=number_of_sample_points)

    # Poisson reconstruction
    mesh_solid, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd,
        depth=density_depth
    )

    # Optional cleanup
    densities = np.asarray(densities)
    keep = densities > np.quantile(densities, keep_quantile)
    mesh_solid = mesh_solid.select_by_index(np.where(keep)[0])

    # FIX: compute normals for STL export
    mesh_solid.compute_triangle_normals()
    mesh_solid.compute_vertex_normals()

    # Write STL
    o3d.io.write_triangle_mesh(outfilename, mesh_solid)

