import plotly.graph_objects as go
import numpy as np

class TechtilePlotter:

    def __init__(self):
        # load positions from YAML
        # Create a layout with a specified aspect ratio
           
        layout = go.Layout(
                scene=dict(
                    aspectmode='manual',
                    aspectratio=dict(x=8.4, y=4, z=2.4),  # Adjust x and y ratio to make it rectangular
                    xaxis=dict(range=[0, 8.4]),  # Set the range for the x-axis
                    yaxis=dict(range=[0, 4]),  # Set the range for the y-axis
                    zaxis=dict(range=[0, 2.4])   # Set the range for the z-axis
                )
            )
        self.fig = go.Figure(layout=layout)
        antennas_plotted = False
        self.antennas_pos = [0] # placeholder to test
        self.fig.add_trace(go.Scatter3d(x=(-1,),
            y=(-1,),
            z=(1,),showlegend=False))

    def microphones(self, pattern=False, directivity=False):
        """ Plots the microphones locations

        Args:
            pattern (bool, optional): Plot the pattern of the microphones (uses the normal of the tiles). Defaults to False.
            directivity (bool, optional): Plot the directivity of the microphones (uses the normal of the tiles). Defaults to False.
        """
        pass

    def antennas(self, pattern=False, directivity=False):
        """ Plots the antenna locations

        Args:
            pattern (bool, optional): Plot the pattern of the antennas (uses the normal of the tiles). Defaults to False.
            directivity (bool, optional): Plot the directivity of the antennas (uses the normal of the tiles). Defaults to False.
        """
        #TODO plot based on normal (include real dimensions)
        scale = 0.1
        x_vals = np.array([0,0,1*scale,1*scale,0])
        y_vals = np.array([0,0,0,0,0])
        z_vals = np.array([0,1*scale,1*scale,0,0])
        for ant in self.antennas_pos:
            self.fig.add_trace(go.Scatter3d(x=x_vals+4, y=y_vals, z=z_vals+1, mode='lines', surfaceaxis=1, # add a surface axis ('1' refers to axes[1] i.e. the y-axis)
        surfacecolor='#66c2a5',showlegend=False))

    def measurements(self, x,y,z, values, color=None, label=None):
        if color is None:
            color = values
        self.fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            text=label,
            mode='markers',
            marker=dict(color=color,colorscale='Viridis', size=10, colorbar=dict(thickness=20))
        ))
        pass

    def show(self):
        self.fig.show()

    def html(self, path):
        self.fig.html(path)