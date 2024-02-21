import plotly.graph_objects as go
import numpy as np
import dicts

path_fig = 'figs\\'

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
    edges_top_ground = edges_from_vertices_2D(vertices)

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
    fig = go.Figure(data= positions + anchors + traces_vert + traces_top_bottom)

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

if __name__ == '__main__':

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
    anchor_positions = create_anchor_position_matrix(anchor_name)

    # Get mobile node positions, normally I got this from csv file or something else, this is just an example
    # [[x1, y1, z1], [x2, y2, z2], ... [xn, yn, zn]]
    positions = np.array([[1, 1.2, 2], [2, 1.2, 2], [3, 1.2, 1.5], [4, 2.0, 1.5]])

    # Get measured values for each position (e.g. positioning errors)
    errors = [0.05, 1.02, 0.7, 0.01]

    # The plotting itself
    plot_room_errors(vertices, height, positions, errors, anchor_positions, anchor_name, '3Dfig', 'Title', 1.5)
