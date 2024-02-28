import plotly.graph_objects as go
import numpy as np
import os
import yaml


class TechtilePlotter:

    def __init__(self):
        # load positions from YAML
        # Create a layout with a specified aspect ratio

        layout = go.Layout(
            scene=dict(
                aspectmode='manual',
                # Adjust x and y ratio to make it rectangular
                aspectratio=dict(x=8.4, y=4, z=2.4),
                xaxis=dict(range=[8.4, 0.0]),  # Set the range for the x-axis
                yaxis=dict(range=[4.0, 0]),  # Set the range for the y-axis
                zaxis=dict(range=[0, 2.4])   # Set the range for the z-axis
            )
        )
        self.fig = go.Figure(layout=layout)

        self.antennas_plotted = False
        self.sdr_descr = []

        with open(os.path.join(os.path.dirname(__file__), "..", "..", "positions.yml"), 'r') as file:
            positions = yaml.safe_load(file)
            self.sdr_descr = positions["antennes"]  # placeholder to test
            # self.fig.add_trace(go.Scatter3d(x=(-1,),
            #                                 y=(-1,),
            #                                 z=(1,), showlegend=False))

    def microphones(self, pattern=False, directivity=False):
        """ Plots the microphones locations

        Args:
            pattern (bool, optional): Plot the pattern of the microphones (uses the normal of the tiles). Defaults to False.
            directivity (bool, optional): Plot the directivity of the microphones (uses the normal of the tiles). Defaults to False.
        """
        pass

    def antennas(self, active_tiles: list = None, pattern=False, directivity=False):
        """ Plots the antenna locations

        Args:
            active_tiles (list, optional): List of active tiles (only those will be plotted)
            pattern (bool, optional): Plot the pattern of the antennas (uses the normal of the tiles). Defaults to False.
            directivity (bool, optional): Plot the directivity of the antennas (uses the normal of the tiles). Defaults to False.
        """
        # TODO plot based on normal (include real dimensions)
        if not self.antennas_plotted:
            scale = 0.1
            x_vals = np.array([0, 0, 1*scale, 1*scale, 0])
            y_vals = np.array([0, 0, 0, 0, 0])
            z_vals = np.array([0, 1*scale, 1*scale, 0, 0])
            for usrp in self.sdr_descr:
                for ch in usrp["channels"]:
                    self.fig.add_trace(go.Scatter3d(x=x_vals+ch["x"], y=y_vals+ch["y"], z=z_vals+ch["z"], mode='lines', surfaceaxis=1,  # add a surface axis ('1' refers to axes[1] i.e. the y-axis)
                                                    surfacecolor='#66c2a5', showlegend=False))
                self.antennas_plotted = True

    def measurements(self, x, y, z, values, color=None, label=None):
        if color is None:
            color = values
        self.fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            text=label,
            mode='markers',
            marker=dict(color=color, colorscale='Viridis',
                        size=10, colorbar=dict(thickness=20))
        ))
        pass

    def show(self):
        self.fig.show()

    def html(self, path):
        self.fig.write_html(path)
