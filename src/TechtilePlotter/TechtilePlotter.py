import plotly.graph_objects as go
import numpy as np
import os
import yaml


class TechtilePlotter:

    def __init__(self, title=None):
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
        self.fig.update_layout(scene_camera_eye=dict(x=7, y=7, z=4))

        if title:
            self.fig.update_layout(
                title=dict(text=title, automargin=True)
            )

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
            skew_symmetric_matrix = np.array([[0, -cross_product[2], cross_product[1]],
                                            [cross_product[2], 0, -cross_product[0]],
                                            [-cross_product[1], cross_product[0], 0]])
            
            # Calculate the rotation matrix
            rotation_matrix = np.eye(3) + skew_symmetric_matrix + np.dot(skew_symmetric_matrix, skew_symmetric_matrix) * (1 / (1 + dot_product))

        return rotation_matrix


    def transform_points(self, matrix, transformation_matrix):
        """Apply the transformation matrix to each point in the original matrix."""
        transformed_matrix = []
        for point in matrix:
            transformed_point = np.dot(transformation_matrix, point)
            transformed_matrix.append(transformed_point)
        return np.asarray(transformed_matrix)

    def antennas(self, active_tiles: list = None, pattern=False, directivity=False, color="#000000"):
        """ Plots the antenna locations

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
        x_vals = np.array([0, 0, 1*scale, 1*scale, 0])
        y_vals = np.array([0, 0, 0, 0, 0])
        z_vals = np.array([0, 1*scale, 1*scale, 0, 0])

        antenna_matrix = np.transpose(np.asarray([x_vals, y_vals, z_vals]))

        # Default unit vector
        default_vector = [0, 1, 0]

        # Show only active tiles
        for tile_nr in active_tiles:
            usrp = next((antenna for antenna in self.sdr_descr if antenna['tile'] == tile_nr), None)
            # print(usrp)
            for ch in usrp["channels"]:

                # print(f"Plotting {tile_nr} CH{ch}")

                # Target unit vector
                target_vector = [ch["vx"], ch["vy"], ch["vz"]]

                if not np.allclose(default_vector, target_vector):
                    # Calculate the rotation matrix
                    rotation_matrix = self.calculate_rotation_matrix(default_vector, target_vector)

                    # Transform the points
                    transformed_matrix = self.transform_points(antenna_matrix, rotation_matrix)
                
                else:
                    transformed_matrix = antenna_matrix

                x_vals_ = transformed_matrix[:,0]
                y_vals_ = transformed_matrix[:,1]
                z_vals_ = transformed_matrix[:,2]

                self.fig.add_trace(go.Scatter3d(x=x_vals_+ch["x"], y=y_vals_+ch["y"], z=z_vals_+ch["z"], mode='lines', surfaceaxis=1,  # add a surface axis ('1' refers to axes[1] i.e. the y-axis)
                                                line=dict(color=color), showlegend=False)) #surfacecolor='#000000',
                # self.antennas_plotted = True

    def measurements(self, x, y, z, values, color=None, label=None, size=10):
        if color is None:
            color = values
        self.fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            text=label,
            mode='markers',
            marker=dict(color=color, colorscale='Viridis',
                        size=size, colorbar=dict(thickness=20))
        ))

    def show(self):
        self.fig.show()

    def html(self, path):
        self.fig.write_html(path)
