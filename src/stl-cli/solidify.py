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
    number_of_sample_points: int = 2**22,
    density_depth: int = 10,
    keep_quantile: float = 0.0,
    smoothing_iterations: int = 20
):
    # Limit OpenMP threads
    cpu_count = math.ceil(multiprocessing.cpu_count() * 0.75)
    os.environ['OMP_NUM_THREADS'] = str(cpu_count)

    structlog.contextvars.bind_contextvars(infilename=infilename, outfilename=outfilename)

    # Read mesh
    mesh = o3d.io.read_triangle_mesh(infilename)
    mesh.compute_vertex_normals()

    # Sample points using Poisson-disk sampling for better distribution
    pcd = mesh.sample_points_poisson_disk(number_of_points=number_of_sample_points)

    # Poisson reconstruction
    mesh_solid, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd,
        depth=density_depth
    )

    # # Keep only high-density vertices
    # densities = np.asarray(densities)
    # keep = densities > np.quantile(densities, keep_quantile)
    # mesh_solid = mesh_solid.select_by_index(np.where(keep)[0])

    # # Remove small disconnected components
    # triangle_clusters, cluster_n_triangles, _ = mesh_solid.cluster_connected_triangles()
    # largest_cluster = np.argmax(cluster_n_triangles)
    # triangles_to_keep = np.where(triangle_clusters == largest_cluster)[0]
    # mesh_solid = mesh_solid.select_by_index(triangles_to_keep, triangle=True)

    # Optional smoothing (Meshmixer-like)
    mesh_solid = mesh_solid.filter_smooth_taubin(number_of_iterations=smoothing_iterations)

    # Compute normals for STL
    mesh_solid.compute_triangle_normals()
    mesh_solid.compute_vertex_normals()

    # Write STL
    o3d.io.write_triangle_mesh(outfilename, mesh_solid)
