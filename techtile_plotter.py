import plotly.graph_objects as go
import numpy as np
import dicts
import local_functions as lf
from pyroomacoustics.directivities import (
    DirectivityPattern
)

path_fig = 'figs\\'


def plot_room_errors(vertices, height, positions, error, anchor_positions, anchor_name, filename, title, cmax):
    """
    Plots the room in 3d, based on given vertices in config file or here in this example on top of the file,
    with corresponding error values at the position as 4th dimension. The anchor positions are also plotted.
    :param vertices: vertices of the ground plane of the room
    :param height: height of the room
    :param positions: positions of interest in the room
    :param error: error (or other parameter) on specific positions
    :param anchor_positions: positions of the anchors (e.g. microphones)
    :param anchor_name: list of names of the anchors (e.g. A01, D11, etc.)
    :param filename: name of the file to save as html file
    :param title: title of the plot
    :param cmax: max value of colorscale
    """
    x_pos = positions[:, 0]
    y_pos = positions[:, 1]
    z_pos = positions[:, 2]

    x_anchor = []
    y_anchor = []
    z_anchor = []
    for coord in anchor_positions:
        x_anchor.append(coord[0])
        y_anchor.append(coord[1])
        z_anchor.append(coord[2])

    traces_vert = []
    for corner in vertices:
        trace = go.Scatter3d(
            x=[corner[0], corner[0]], y=[corner[1], corner[1]], z=[0, height],
            mode='lines',
            line=dict(color='black', width=2),
            hoverinfo='none',
            text=None,
            connectgaps=False,
            showlegend=False
        )
        traces_vert.append(trace)

    # Create ground and top plane of room
    edges_top_ground = lf.edges_from_vertices_2D(vertices)

    traces_top_bottom = []
    for edge in edges_top_ground:
        x_tr, y_tr = zip(*edge)
        trace1 = go.Scatter3d(
            x=x_tr, y=y_tr, z=[height, height],
            mode='lines',
            line=dict(color='black', width=2),
            hoverinfo='none',
            text=None,
            connectgaps=False,
            showlegend=False
        )
        traces_top_bottom.append(trace1)
        trace2 = go.Scatter3d(
            x=x_tr, y=y_tr, z=[0, 0],
            mode='lines',
            line=dict(color='black', width=2),
            hoverinfo='none',
            text=None,
            connectgaps=False,
            showlegend=False
        )
        traces_top_bottom.append(trace2)

    positions = [(go.Scatter3d(x=x_pos, y=y_pos, z=z_pos, mode='markers', name='Error in m', marker_size=10,  text=[f'Point {i}<br>Error: {error[i]:.2f} m' for i in range(len(error))],
                               marker=dict(color=error, colorscale='Viridis', opacity=0.8, showscale=True, cmin=0, cmax=cmax)))]
    anchors = [(go.Scatter3d(x=x_anchor, y=y_anchor, z=z_anchor, mode='markers', name='Anchors', marker_size=5,
                             marker=dict(color="#386055", symbol='square'), text=['Anchor ' + str(anchor_name[i]) for i in range(len(x_anchor))]))]

    # Create a Scatter trace for the points
    fig = go.Figure(data = positions + anchors + traces_vert + traces_top_bottom)

    camera_params = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=-1, y=-1.75, z=1.1)
    )

    fig.update_scenes(xaxis=dict(title_text='x [m]'),
                      yaxis=dict(title_text='y [m]'),
                      zaxis=dict(title_text='z [m]'))

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                      scene_camera=camera_params, legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1),
                      height=800)

    fig.write_html(path_fig + filename + ".html")
    #fig.show()


def plot_room_situation(vertices, height, anchor_locs, positions_mn, plt_dir_vect_ancher, plot_dirs_ancher, plt_dir_vect_mn, plot_dirs_mn,
                               dir_pattern_ancher, dir_pattern_mn, filename, title):
    """
        Plots the room with anchors and mobile nodes (mn) given its vertices and height an all positions within the room
        Directivity vectors and directivities are also plotted if set to True
    :param vertices: coordinates of corners in 2D
    :param height: height of the room
    :param anchor_locs: location of the anchors np array: [[x1, y1, z1, azi1, coalt1 ], [x2, y2, ... ], ...]
    :param positions_mn: location of the mobile nodes np array: [[x1, y1, z1, azi1, coalt1 ], [x2, y2, ... ], ...]
    :param plt_dir_vect_ancher: True or False to plot a vector for anchor directivity
    :param plot_dirs_ancher: True or False to plot the directivities of the anchors
    :param plt_dir_vect_mn: True or False to plot a vector for mobile node directivity
    :param plot_dirs_mn: True or False to plot the mobile node directivities
    :param dir_pattern_ancher: Directivity pattern of anchor nodes: e.g. DirectivityPattern.CARDIOID (via PyroomAcoustics)
    :param dir_pattern_mn: Directivity pattern of mn's: e.g. DirectivityPattern.CARDIOID (via PyroomAcoustics)
    :param filename: name of the .html file to save it
    :param title: Title of the plotly plot
    """
    x_an = anchor_locs[:,0]
    y_an = anchor_locs[:,1]
    z_an = anchor_locs[:,2]
    azimuth_anch = anchor_locs[:,3]
    coaltitude_anch = anchor_locs[:,4]

    x_mn = positions_mn[:, 0]
    y_mn = positions_mn[:, 1]
    z_mn = positions_mn[:, 2]
    azimuth_mn = positions_mn[:,3]
    coaltitude_mn = positions_mn[:,4]

    traces_vert = []
    for corner in vertices:
        trace = go.Scatter3d(
            x=[corner[0], corner[0]], y=[corner[1], corner[1]], z=[0, height],
            mode='lines',
            line=dict(color='black', width=2),
            hoverinfo='none',
            text=None,
            connectgaps=False,
            showlegend=False
        )
        traces_vert.append(trace)

    # Create ground and top plane of room
    edges_top_ground = lf.edges_from_vertices_2D(vertices)

    traces_top_bottom = []
    for edge in edges_top_ground:
        x_tr, y_tr = zip(*edge)
        trace1 = go.Scatter3d(
            x=x_tr, y=y_tr, z=[height, height],
            mode='lines',
            line=dict(color='black', width=2),
            hoverinfo='none',
            text=None,
            connectgaps=False,
            showlegend=False
        )
        traces_top_bottom.append(trace1)
        trace2 = go.Scatter3d(
            x=x_tr, y=y_tr, z=[0, 0],
            mode='lines',
            line=dict(color='black', width=2),
            hoverinfo='none',
            text=None,
            connectgaps=False,
            showlegend=False
        )
        traces_top_bottom.append(trace2)


    anchers = [(go.Scatter3d(x=x_an, y=y_an, z=z_an, mode='markers', name='Anchors', marker_size=5,
                             marker=dict(color="#BB4406", symbol='square')))]
    datapoints_mn = [(go.Scatter3d(x=x_mn, y=y_mn, z=z_mn, mode='markers', name='Mobile nodes', marker_size=5,
                                     marker=dict(color="#a28be3")))]

    data = anchers + datapoints_mn + traces_vert + traces_top_bottom

    if plt_dir_vect_ancher:
        dir_vects_anchors, dir_vects_legend_anchors = lf.create_plot_dir_vector_object(coaltitude_anch, azimuth_anch, anchor_locs, 'Directivity vector anchors') #TODO
        data = data + dir_vects_anchors + [dir_vects_legend_anchors]

    if plot_dirs_ancher:
        dirs_anchers, dir_anchors_legend = lf.create_dir_speaker_plot_objects(anchor_locs, dir_pattern_ancher, scale=0.5, color='orange', name='Directivity anchors')
        data = data + dirs_anchers + [dir_anchors_legend]

    if plt_dir_vect_mn:
        dir_vect_mn, dir_vects_legend_mn = lf.create_plot_dir_vector_object(positions_mn[:, 3], positions_mn[:,4], positions_mn[:, 0:3], 'Directivity vector mobile nodes')
        data = data + dir_vect_mn + [dir_vects_legend_mn]

    if plot_dirs_mn:
        dirs_mn, dir_mn_legend = lf.create_dir_speaker_plot_objects(positions_mn, dir_pattern_mn, scale=0.3,
                                                                           color = 'purple', name='Directivity mobile nodes')
        data = data + dirs_mn + [dir_mn_legend]

    # Create a Scatter trace for the points
    fig = go.Figure(data=data)

    camera_params = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=-1, y=-1.75, z=1.1)
    )

    fig.update_scenes(xaxis=dict(title_text='x [m]'),
                      yaxis=dict(title_text='y [m]'),
                      zaxis=dict(title_text='z [m]'))

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                      scene_camera=camera_params, legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1),
                      height=800)

    fig.write_html(path_fig + filename + ".html")


if __name__ == '__main__':

    ################################################################
    #   Example 1: room plot with color scale for measured values
    ################################################################

    # 2 examples, one shoebox example = Techtile and one other random room given by it's vertices in 2D and a height
    shoebox = True,
    room_dim_shoebox = [8.56, 4.0, 2.4]
    room_corners_no_shoebox = [[0, 0], [0, 4], [8, 4], [8, 1.5], [6, 1.5], [5, 0]]
    room_height_no_shoebox = 2.4

    if shoebox:
        room_dim = room_dim_shoebox
        height = room_dim[2]
        vertices = np.array([[0, 0], [0, room_dim[1]], [room_dim[0], room_dim[1]], [room_dim[0], 0]])
    else:
        vertices = room_corners_no_shoebox
        height= room_height_no_shoebox

    # Select anchors you want to add to the plot based on the dicts.py dictionary
    anchor_name = ['C07', 'G03', 'E04', 'C12', 'E09', 'A02', 'A11']
    anchor_positions = lf.create_anchor_position_matrix(anchor_name)

    # Get mobile node positions, normally I got this from csv file or something else, this is just an example
    # [[x1, y1, z1], [x2, y2, z2], ... [xn, yn, zn]]
    positions = np.array([[1, 1.2, 2], [2, 1.2, 2], [3, 1.2, 1.5], [4, 2.0, 1.5]])

    # Get measured values for each position (e.g. positioning errors)
    errors = [0.05, 1.02, 0.7, 0.01]

    # The plotting itself
    plot_room_errors(vertices, height, positions, errors, anchor_positions, anchor_name, '3Dfig_example1', 'Example 1 Room', 1.5)
    print('Check folder figs to see the plots')

    #####################################################################
    #   Example 2: detailed room situation plot with directivities etc.
    #####################################################################
    anchor_locs = np.array([[1, 0.05, 1.8, 90, 90], [7, 0.05, 1, 90, 90], [4, 3.95, 1.5, 270, 90]]) # np array: [[x1, y1, z1, azi1, coalt1 ], [x2, y2, ... ], ...]
    positions_mn =  np.array([[1, 1.2, 2, 0, 0], [2, 1.2, 2, 0, 0]])

    pattern_enum_anchor = DirectivityPattern.CARDIOID
    pattern_enum_mn = DirectivityPattern.OMNI

    plot_room_situation(vertices, height, anchor_locs, positions_mn, True, True, True, True, pattern_enum_anchor,
                        pattern_enum_mn, '3Dfig_example2', 'Example 2 Room')
