import plotly.graph_objects as go
import numpy as np
import os
import yaml
import threading
import dash


class TechtilePlotter:

    def __init__(self, title=None, realtime=False):
        # load positions from YAML
        # Create a layout with a specified aspect ratio

        if realtime:

            from dash import dcc, html
            from dash.dependencies import Input, Output, State

            # Initialize the Dash app
            self.app = dash.Dash(__name__)

            self.data_store = {"x": [], "y": [], "z": [], "values": []}

            self.is_recording = False

            self.camera_view = {  # Default camera view
                "eye": {"x": 7, "y": 7, "z": 4},
                "up": {"x": 0, "y": 0, "z": 1},
                "center": {"x": 0, "y": 0, "z": 0},
            }

            # Layout of the app with full-width styles
            # Layout with full-width style and two plots side by side (no buttons)
            self.app.layout = html.Div(style={'width': '100%', 'height': '100vh', 'display': 'flex'}, children=[
                html.Div(style={'width': '50%'}, children=[
                    dcc.Graph(id='live-3d-scatter-plot', style={'height': '80vh'}),
                    dcc.Store(id='camera-store', data=self.camera_view),  # Store camera view
                ]),
                html.Div(style={'width': '50%'}, children=[
                    dcc.Graph(id='live-2d-plot', style={'height': '80vh'}),
                ]),
                dcc.Interval(id='interval-component', interval=1000, n_intervals=0),  # Update every second
            ])

            # Register callbacks for updating both figures
            self.app.callback(
                [Output('live-3d-scatter-plot', 'figure'), Output('live-2d-plot', 'figure')],
                [Input('interval-component', 'n_intervals'),
                State('camera-store', 'data')]
            )(self.update_graph)

            # # Register callbacks
            # self.app.callback(
            #     Output("live-3d-scatter-plot", "figure"),
            #     # (
            #         Input("interval-component", "n_intervals"),
            #         # State("camera-store", "data"),
            #     # ),
            # )(self.update_graph)

            self.app.callback(
                Output("camera-store", "data"),
                Input("live-3d-scatter-plot", "relayoutData"),
            )(self.store_camera_view)

            # self.app.callback(
            #     Output("interval-component", "disabled"),
            #     [Input("start-button", "n_clicks"), Input("stop-button", "n_clicks")],
            # )(self.toggle_recording)

            self.layout = go.Layout(
                scene=dict(
                    aspectmode="manual",
                    # Adjust x and y ratio to make it rectangular
                    aspectratio=dict(x=8.4, y=4, z=2.4),
                    xaxis=dict(range=[8.4, 0.0]),  # Set the range for the x-axis
                    yaxis=dict(range=[4.0, 0]),  # Set the range for the y-axis
                    zaxis=dict(range=[0, 2.4]),  # Set the range for the z-axis,
                    camera=self.camera_view,
                )
            )
        self.fig = go.Figure(layout=self.layout)
        self.fig.update_layout(scene_camera_eye=dict(x=7, y=7, z=4))

        if title:
            self.fig.update_layout(title=dict(text=title, automargin=True))

        self.antennas_plotted = False
        self.sdr_descr = []

        import importlib.resources

        # with importlib.resources.open_text(__name__, 'positions.yml') as file:
        with open(
            os.path.join(os.path.dirname(__file__), "positions.yml"), "r"
        ) as file:
            positions = yaml.safe_load(file)
            self.sdr_descr = positions["antennes"]  # placeholder to test
            # self.fig.add_trace(go.Scatter3d(x=(-1,),
            #                                 y=(-1,),
            #                                 z=(1,), showlegend=False))

        if realtime:
            self.run()

    # def toggle_recording(self, start_clicks, stop_clicks):
    #     """Toggle recording based on button clicks."""
    #     if start_clicks > stop_clicks:  # If Start has been clicked more than Stop
    #         self.is_recording = True
    #         self.data_store = {
    #             "x": [],
    #             "y": [],
    #             "z": [],
    #             "values": [],
    #         }  # Reset the data store when starting
    #     else:
    #         self.is_recording = False  # Stop recording
    #     return False  # Return False to keep the interval running (no disabling)

    def store_camera_view(self, relayoutData):
        """Store the current camera view from the graph."""
        if relayoutData and "scene.camera" in relayoutData:
            return relayoutData["scene.camera"]
        return dash.no_update  # Do not update if no camera change

    def measurements_rt(self, x, y, z, values, color=None, label=None):
        # Update the store with new data
        # if self.is_recording:
        self.data_store["x"].append(x)
        self.data_store["y"].append(y)
        self.data_store["z"].append(z)
        self.data_store["values"].append(values)

    def update_graph(self, n, camera_view):
        # Extract x, y, z data from the store

        x = self.data_store["x"]
        y = self.data_store["y"]
        z = self.data_store["z"]
        values = self.data_store["values"]

        scatter_3d = go.Scatter3d(
            x=x,
            y=y,
            z=z,
            text=values,
            mode="markers",
            marker=dict(
                color=values, colorscale="Viridis", size=10, colorbar=dict(thickness=20)
            ),
        )
        # Return the figure
        layout_3d = go.Layout(
            scene=dict(
                aspectmode="manual",
                # Adjust x and y ratio to make it rectangular
                aspectratio=dict(x=8.4, y=4, z=2.4),
                xaxis=dict(range=[8.4, 0.0]),  # Set the range for the x-axis
                yaxis=dict(range=[4.0, 0]),  # Set the range for the y-axis
                zaxis=dict(range=[0, 2.4]),  # Set the range for the z-axis,
                camera=camera_view,
                uirevision=True,
            )
        )

        layout_2d = go.Layout(
            scene=dict(
                aspectmode="manual",
                # Adjust x and y ratio to make it rectangular
                aspectratio=dict(x=8.4, y=4),
                xaxis=dict(range=[8.4, 0.0]),  # Set the range for the x-axis
                yaxis=dict(range=[4.0, 0]),  # Set the range for the y-axis
                uirevision=True,
            )
        )

        scatter_2d = go.Scatter(
            x=x,
            y=y,
            text=values,
            mode="markers",
            marker=dict(
                color=values, colorscale="Viridis", size=10, colorbar=dict(thickness=20)
            ),
        )

        # Return both the 3D and 2D figures
        return {"data": [scatter_3d], "layout": layout_3d}, {
            "data": [scatter_2d],
            "layout": layout_2d,
        }

    def run(self):
        # Run the Dash app in a separate thread
        self.thr = threading.Thread(target=self.app.run_server, daemon=True)
        self.thr.start()

    def microphones(self, pattern=False, directivity=False):
        """Plots the microphones locations

        Args:
            pattern (bool, optional): Plot the pattern of the microphones (uses the normal of the tiles). Defaults to False.
            directivity (bool, optional): Plot the directivity of the microphones (uses the normal of the tiles). Defaults to False.
        """
        pass

    def normalize(self, vector):
        """Normalize a vector to make it a unit vector."""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def calculate_rotation_matrix(self, default_vector, target_vector):
        """Calculate the rotation matrix to align the default vector with the target vector."""
        default_vector = self.normalize(default_vector)
        target_vector = self.normalize(target_vector)

        # Calculate the dot product
        dot_product = np.dot(default_vector, target_vector)

        if dot_product == -1.0:
            rotation_matrix = np.eye(3)
        else:
            # Calculate the cross product
            cross_product = np.cross(default_vector, target_vector)

            # Calculate the skew-symmetric matrix
            skew_symmetric_matrix = np.array(
                [
                    [0, -cross_product[2], cross_product[1]],
                    [cross_product[2], 0, -cross_product[0]],
                    [-cross_product[1], cross_product[0], 0],
                ]
            )

            # Calculate the rotation matrix
            rotation_matrix = (
                np.eye(3)
                + skew_symmetric_matrix
                + np.dot(skew_symmetric_matrix, skew_symmetric_matrix)
                * (1 / (1 + dot_product))
            )

        return rotation_matrix

    def transform_points(self, matrix, transformation_matrix):
        """Apply the transformation matrix to each point in the original matrix."""
        transformed_matrix = []
        for point in matrix:
            transformed_point = np.dot(transformation_matrix, point)
            transformed_matrix.append(transformed_point)
        return np.asarray(transformed_matrix)

    def antennas(
        self,
        active_tiles: list = None,
        pattern=False,
        directivity=False,
        color="#000000",
    ):
        """Plots the antenna locations

        Args:
            active_tiles (list, optional): List of active tiles (only those will be plotted)
            pattern (bool, optional): Plot the pattern of the antennas (uses the normal of the tiles). Defaults to False.
            directivity (bool, optional): Plot the directivity of the antennas (uses the normal of the tiles). Defaults to False.
        """
        # TODO plot based on normal (include real dimensions)
        # if not self.antennas_plotted:
        #     scale = 0.1
        #     x_vals = np.array([0, 0, 1*scale, 1*scale, 0])
        #     y_vals = np.array([0, 0, 0, 0, 0])
        #     z_vals = np.array([0, 1*scale, 1*scale, 0, 0])
        #     for usrp in self.sdr_descr:
        #         for ch in usrp["channels"]:
        #             self.fig.add_trace(go.Scatter3d(x=x_vals+ch["x"], y=y_vals+ch["y"], z=z_vals+ch["z"], mode='lines', surfaceaxis=1,  # add a surface axis ('1' refers to axes[1] i.e. the y-axis)
        #                                             surfacecolor='#66c2a5', showlegend=False))
        #         self.antennas_plotted = True
        # ONLY active tiles
        # if not self.antennas_plotted:
        scale = 0.1
        x_vals = np.array([0, 0, 1 * scale, 1 * scale, 0])
        y_vals = np.array([0, 0, 0, 0, 0])
        z_vals = np.array([0, 1 * scale, 1 * scale, 0, 0])

        antenna_matrix = np.transpose(np.asarray([x_vals, y_vals, z_vals]))

        # Default unit vector
        default_vector = [0, 1, 0]

        # Show only active tiles
        for tile_nr in active_tiles:
            usrp = next(
                (antenna for antenna in self.sdr_descr if antenna["tile"] == tile_nr),
                None,
            )
            # print(usrp)
            for ch in usrp["channels"]:

                # print(f"Plotting {tile_nr} CH{ch}")

                # Target unit vector
                target_vector = [ch["vx"], ch["vy"], ch["vz"]]

                if not np.allclose(default_vector, target_vector):
                    # Calculate the rotation matrix
                    rotation_matrix = self.calculate_rotation_matrix(
                        default_vector, target_vector
                    )

                    # Transform the points
                    transformed_matrix = self.transform_points(
                        antenna_matrix, rotation_matrix
                    )

                else:
                    transformed_matrix = antenna_matrix

                x_vals_ = transformed_matrix[:, 0]
                y_vals_ = transformed_matrix[:, 1]
                z_vals_ = transformed_matrix[:, 2]

                self.fig.add_trace(
                    go.Scatter3d(
                        x=x_vals_ + ch["x"],
                        y=y_vals_ + ch["y"],
                        z=z_vals_ + ch["z"],
                        mode="lines",
                        surfaceaxis=1,  # add a surface axis ('1' refers to axes[1] i.e. the y-axis)
                        line=dict(color=color),
                        showlegend=False,
                    )
                )  # surfacecolor='#000000',
                # self.antennas_plotted = True

    def measurements(self, positions, values, colors=None, labels=None, size=10):
        if colors is None:
            colors = values
        if labels is None:
            labels = values
        x = [p.x for p in positions]
        y = [p.y for p in positions]
        z = [p.z for p in positions]

        self.fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                text=labels,
                mode="markers",
                marker=dict(
                    color=colors,
                    colorscale="Viridis",
                    size=size,
                    colorbar=dict(thickness=20),
                ),
            )
        )

    def measurements_xyz(self, x, y, z, values, color=None, label=None, size=10):
        if color is None:
            color = values
        self.fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                text=label,
                mode="markers",
                marker=dict(
                    color=color,
                    colorscale="Viridis",
                    size=size,
                    colorbar=dict(thickness=20),
                ),
            )
        )

    def show(self):
        self.fig.show()

    def html(self, path):
        self.fig.write_html(path)
