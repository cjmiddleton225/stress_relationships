import numpy as np
from numpy.typing import ArrayLike
from dataclasses import dataclass

@dataclass
class StressTensor:
    """
    A class to represent a 3D stress tensor and perform common operations.
    """
    components: np.ndarray

    def __init__(self, components: ArrayLike):
        """
        Initialize stress tensor with components.
        Expected format: 3x3 matrix or [xx, yy, zz, xy, yz, xz]
        """
        if isinstance(components, (list, np.ndarray)):
            if len(components) == 6:
                # Convert from vector [xx, yy, zz, xy, yz, xz] to 3x3 matrix
                xx, yy, zz, xy, yz, xz = components
                self.components = np.array([
                    [xx, xy, xz],
                    [xy, yy, yz],
                    [xz, yz, zz]
                ])
            elif np.array(components).shape == (3, 3):
                self.components = np.array(components)
            else:
                raise ValueError("Components must be either a 6-element vector or 3x3 matrix")
        else:
            raise TypeError("Components must be list or numpy array")

    @property
    def principal_stresses(self) -> np.ndarray:
        """Calculate principal stresses."""
        eigenvalues, eigenvectors = np.linalg.eigh(self.components)

        return eigenvalues, eigenvectors

    @property
    def von_mises(self) -> float:
        """Calculate von Mises stress."""
        s = self.components
        return np.sqrt(0.5 * ((s[0,0] - s[1,1])**2 + 
                             (s[1,1] - s[2,2])**2 + 
                             (s[2,2] - s[0,0])**2 + 
                             6*(s[0,1]**2 + s[1,2]**2 + s[0,2]**2)))
    @property
    def tresca(self) -> float:
        """Calculate Tresca stress."""
        principal_stresses = self.principal_stresses[0]
        return max(abs(principal_stresses[0] - principal_stresses[1]),
                   abs(principal_stresses[1] - principal_stresses[2]),
                   abs(principal_stresses[2] - principal_stresses[0]))

    @property
    def signed_von_mises(self) -> float:
        """Calculate signed von Mises stress."""
        s = self.components
        von_mises_stress = self.von_mises
        hydrostatic_stress = (s[0, 0] + s[1, 1] + s[2, 2]) / 3
        return np.sign(hydrostatic_stress) * von_mises_stress

    @property
    def signed_tresca(self) -> float:
        """Calculate signed Tresca stress."""
        tresca_stress = self.tresca
        hydrostatic_stress = (self.components[0, 0] + self.components[1, 1] + self.components[2, 2]) / 3
        return np.sign(hydrostatic_stress) * tresca_stress

    def rotate_by_euler_angles(self, angles: ArrayLike, inplace: bool = True) -> 'StressTensor':
        """
        Rotate stress tensor by Euler angles (in radians).
        angles: [theta_x, theta_y, theta_z]
        inplace: If True, modify the tensor in place, otherwise return a new rotated tensor.
        """
        theta_x, theta_y, theta_z = angles

        # Rotation matrices around x, y, and z axes
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(theta_x), -np.sin(theta_x)],
            [0, np.sin(theta_x), np.cos(theta_x)]
        ])
        Ry = np.array([
            [np.cos(theta_y), 0, np.sin(theta_y)],
            [0, 1, 0],
            [-np.sin(theta_y), 0, np.cos(theta_y)]
        ])
        Rz = np.array([
            [np.cos(theta_z), -np.sin(theta_z), 0],
            [np.sin(theta_z), np.cos(theta_z), 0],
            [0, 0, 1]
        ])

        # Combined rotation matrix
        R = Rz @ Ry @ Rx

        # Rotate the stress tensor
        rotated_components = R @ self.components @ R.T

        if inplace:
            self.components = rotated_components
            return self
        else:
            return StressTensor(rotated_components)
        
    def rotate_by_matrix(self, rotation_matrix: ArrayLike, inplace: bool = True) -> 'StressTensor':
        """
        Rotate stress tensor by a given rotation matrix.
        rotation_matrix: 3x3 matrix
        inplace: If True, modify the tensor in place, otherwise return a new rotated tensor.
        """
        rotated_components = rotation_matrix @ self.components @ rotation_matrix.T

        if inplace:
            self.components = rotated_components
            return self
        else:
            return StressTensor(rotated_components)

    def __str__(self) -> str:
        """
        Return a string representation of the stress tensor.
        Shows components in matrix form rounded to 2 decimal places.
        """
        matrix = np.round(self.components, decimals=2)
        rows = []
        rows.append("⎡{:8.2f} {:8.2f} {:8.2f}⎤".format(*matrix[0]))
        rows.append("⎢{:8.2f} {:8.2f} {:8.2f}⎥".format(*matrix[1]))
        rows.append("⎣{:8.2f} {:8.2f} {:8.2f}⎦".format(*matrix[2]))
        return "\n".join(rows)
    
if __name__ == "__main__":
    # Example usage
    tensor = StressTensor([-100, -50, -30, -20, -10, -5])
    
    rotx, roty, rotz = 10, 20, 30 # degrees
    print("Stress Tensor:")
    print(tensor)
    principal_stresses, principal_vector = tensor.principal_stresses
    print("\nPrincipal Stresses:", np.round(principal_stresses, 2))
    print("Principal Vectors:", principal_vector)
    print("Von Mises Stress:", round(tensor.von_mises, 2))
    print("Tresca Stress:", round(tensor.tresca, 2))
    print("Signed Von Mises Stress:", round(tensor.signed_von_mises, 2))
    print("Signed Tresca Stress:", round(tensor.signed_tresca, 2))
    
    rotated_tensor = tensor.rotate_by_euler_angles([np.radians(rotx), np.radians(roty), np.radians(rotz)], inplace=False)
    print("\nRotated Tensor:")
    print(rotated_tensor)
    principal_stresses, principal_vector = rotated_tensor.principal_stresses
    print("\nPrincipal Stresses (rotated):", np.round(principal_stresses, 2))
    print("Principal Vectors (rotated):", principal_vector)
    print("Von Mises Stress (rotated):", round(rotated_tensor.von_mises, 2))
    print("Tresca Stress (rotated):", round(rotated_tensor.tresca, 2))
    print("Signed Von Mises Stress (rotated):", round(rotated_tensor.signed_von_mises, 2))
    print("Signed Tresca Stress (rotated):", round(rotated_tensor.signed_tresca, 2))
    print("\nOriginal Tensor:")
    print(tensor)

    # Rotation matrix
    rotation_matrix = principal_vector.T
    rotated_tensor.rotate_by_matrix(rotation_matrix, inplace=True)
    print("\nRotated Tensor:")
    print(rotated_tensor)
    principal_stresses, principal_vector = tensor.principal_stresses
    print("\nPrincipal Stresses (rotated):", np.round(principal_stresses, 2))
    print("Principal Vectors (rotated):", principal_vector)
    print("Von Mises Stress (rotated):", round(rotated_tensor.von_mises, 2))
    print("Tresca Stress (rotated):", round(rotated_tensor.tresca, 2))
    print("Signed Von Mises Stress (rotated):", round(rotated_tensor.signed_von_mises, 2))
    print("Signed Tresca Stress (rotated):", round(rotated_tensor.signed_tresca, 2))
    print("\nOriginal Tensor:")
    print(tensor)

