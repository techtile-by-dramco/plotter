import plotly.graph_objects as go
import numpy as np
import dicts
import itertools
from pyroomacoustics.directivities import (
    DirectivityPattern,
    DirectionVector,
    CardioidFamily
)

def create_anchor_position_matrix(anchor_name):
    """
    From the mic_dict get the corresponding positions given the name of the anchor
    :param anchor_name: list of selected anchor names
    :return: matrix with positions of anchors from list
    """
    dict = dicts.mic_dict

    positions = [dict[anchor][1] for anchor in anchor_name]
    anchor_xyz_np = np.array(positions)

    return anchor_xyz_np

def edges_from_vertices_2D(vertices):
    """
    Creates xy plane edges (2D projection or ground plan of the room)
    :param vertices: the coordinates of the room
    :return: the edges of the room
    """
    edges = []
    for i in range(len(vertices)):
        edges.append((vertices[i], vertices[(i+1) % len(vertices)]))
    return edges

def create_plot_dir_vector_object(coaltitudes, azimuths, locations, name):
    # Directivity vectors
    length = 0.25
    # Convert coaltitude to zenith angle in radians
    zenith_angle = np.radians(coaltitudes)
    # Convert azimuth to radians
    azimuth_rad = np.radians(azimuths)

    dx = np.sin(zenith_angle) * np.cos(azimuth_rad)
    dy = np.sin(zenith_angle) * np.sin(azimuth_rad)
    dz = np.cos(zenith_angle)
    direction_vector = (np.array([dx, dy, dz])).T
    end_point = locations[:, 0:3] + length * direction_vector

    x = locations[:,0]
    y = locations[:,1]
    z = locations[:,2]

    dir_vects_anchors = []
    for i, point in enumerate(end_point):
        line_dir = go.Scatter3d(
            x=[x[i], point[0]], y=[y[i], point[1]], z=[z[i], point[2]],
            mode='lines',
            line=dict(color='black', width=4),
            hoverinfo='none',
            text=name,
            connectgaps=False,
            showlegend=False,
            legendgroup=name
        )
        dir_vects_anchors.append(line_dir)

    dir_vects_legend_anchors = go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='lines',
        name=name,
        line=dict(color='black', width=2),
        hoverinfo='none',
        showlegend=True,
        legendgroup=name  # use the same custom legend group
    )

    return dir_vects_anchors, dir_vects_legend_anchors

def create_dir_speaker_plot_objects(positions, dir_pattern, scale, color, name):
    azimuth_plot = np.linspace(start=0, stop=360, num=35, endpoint=True) #361
    colatitude_plot = np.linspace(start=0, stop=180, num=35, endpoint=True) #180

    dir_obj = []
    legend = go.Scatter3d()
    for p in positions:
        x_offset = p[0]
        y_offset = p[1]
        z_offset = p[2]
        azi = p[3]
        coalt = p[4]

        spher_coord = np.array(list(itertools.product(azimuth_plot, colatitude_plot)))  #All combinations pyroom

        azi_flat = spher_coord[:, 0]
        col_flat = spher_coord[:, 1]

        dir_pattern_obj = CardioidFamily(
            orientation=DirectionVector(azimuth=azi, colatitude=coalt, degrees=True),
            pattern_enum=dir_pattern
        )

        # compute response
        resp = dir_pattern_obj.get_response(azimuth=azi_flat, colatitude=col_flat ,magnitude=True, degrees=False)
        RESP = resp.reshape(len(azimuth_plot), len(colatitude_plot))

        # create surface plot, need cartesian coordinates
        AZI, COL = np.meshgrid(azimuth_plot, colatitude_plot)
        X = scale * RESP.T * np.sin(COL) * np.cos(AZI) + x_offset
        Y = scale * RESP.T * np.sin(COL) * np.sin(AZI) + y_offset
        Z = scale * RESP.T * np.cos(COL) + z_offset

        points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])

        fig_obj = go.Mesh3d(x=points[:, 0], y=points[:, 1], z=points[:, 2], alphahull=0.4, opacity=0.3, color=color,
                            legendgroup=name)
        dir_obj.append(fig_obj)

        legend = go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode='markers',
            name=name,
            line=dict(color=color, width=2),
            opacity=0.3,
            hoverinfo='none',
            showlegend=True,
            legendgroup=name  # use the same custom legend group
        )

    return dir_obj, legend