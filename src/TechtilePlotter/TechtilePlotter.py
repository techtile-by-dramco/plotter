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
            from dash.dependencies import Input, Output

            # Initialize the Dash app
            self.app = dash.Dash(__name__)

            self.data_store = {"x": [], "y": [], "z": [], "values": []}

            self.camera_view = {  # Default camera view
                "eye": {"x": 7, "y": 7, "z": 4},
                "up": {"x": 0, "y": 0, "z": 1},
                "center": {"x": 0, "y": 0, "z": 0},
            }

            # Layout of the app with full-width styles
            self.app.layout = html.Div(
                style={
                    "width": "100%",
                    "height": "100vh",
                    "margin": "0",
                    "padding": "0",
                },
                children=[
                    dcc.Graph(id="live-3d-scatter-plot", style={"height": "100vh"}),
                    dcc.Store(
                        id="camera-store", data=self.camera_view
                    ),  # Store camera view
                    dcc.Interval(
                        id="interval-component", interval=1000, n_intervals=0
                    ),  # Update every second
                ],
            )

            # Register the callbacks
            self.app.callback(
                Output("live-3d-scatter-plot", "figure"),
                Input("interval-component", "n_intervals"),  # Trigger every interval
            )(self.update_graph)

            self.app.callback(
                Output("camera-store", "data"),
                Input(
                    "live-3d-scatter-plot", "relayoutData"
                ),  # Trigger when the graph is relayed
            )(self.store_camera_view)

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

        with open(
            os.path.join(os.path.dirname(__file__), "..", "..", "positions.yml"), "r"
        ) as file:
            positions = yaml.safe_load(file)
            self.sdr_descr = positions["antennes"]  # placeholder to test
            # self.fig.add_trace(go.Scatter3d(x=(-1,),
            #                                 y=(-1,),
            #                                 z=(1,), showlegend=False))

        if realtime:
            self.run()

    def store_camera_view(self, relayoutData):
        """Store the current camera view from the graph."""
        if relayoutData and 'scene.camera' in relayoutData:
            return relayoutData['scene.camera']
        return dash.no_update  # Do not update if no camera change

    def measurements_rt(self, x, y, z, values, color=None, label=None):
        # Update the store with new data
        self.data_store["x"].append(x)
        self.data_store["y"].append(y)
        self.data_store["z"].append(z)
        self.data_store["values"].append(values)

    def update_graph(self, n):
        # Extract x, y, z data from the store
        print("updating graph")

        x = self.data_store["x"]
        y = self.data_store["y"]
        z = self.data_store["z"]
        values = self.data_store["values"]

        scatter = go.Scatter3d(
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
        self.layout.scene.camera = self.camera_view
        _fig = go.Figure({"data": [scatter], "layout": self.layout})

        return _fig

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

    def antennas(self, active_tiles: list = None, pattern=False, directivity=False):
        """Plots the antenna locations

        Args:
            active_tiles (list, optional): List of active tiles (only those will be plotted)
            pattern (bool, optional): Plot the pattern of the antennas (uses the normal of the tiles). Defaults to False.
            directivity (bool, optional): Plot the directivity of the antennas (uses the normal of the tiles). Defaults to False.
        """
        # TODO plot based on normal (include real dimensions)
        if not self.antennas_plotted:
            scale = 0.1
            x_vals = np.array([0, 0, 1 * scale, 1 * scale, 0])
            y_vals = np.array([0, 0, 0, 0, 0])
            z_vals = np.array([0, 1 * scale, 1 * scale, 0, 0])
            for usrp in self.sdr_descr:
                for ch in usrp["channels"]:
                    self.fig.add_trace(
                        go.Scatter3d(
                            x=x_vals + ch["x"],
                            y=y_vals + ch["y"],
                            z=z_vals + ch["z"],
                            mode="lines",
                            surfaceaxis=1,  # add a surface axis ('1' refers to axes[1] i.e. the y-axis)
                            surfacecolor="#66c2a5",
                            showlegend=False,
                        )
                    )
                self.antennas_plotted = True

    def measurements(self, x, y, z, values, color=None, label=None):
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
                    size=10,
                    colorbar=dict(thickness=20),
                ),
            )
        )

    def show(self):
        self.fig.show()

    def html(self, path):
        self.fig.write_html(path)
