import numpy as np
from numpy.typing import ArrayLike
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.transforms import Affine2D

# reference: https://engineerexcel.com/stress-and-strain-transformations/

def strain_calcs(e0: ArrayLike, e45: ArrayLike, e90: ArrayLike) -> dict:
    """
    Compute strain components, principal strains, maximum shear strain, and principal angle from a 0-45-90 strain gauge rosette.
    
    Parameters:
        e0 (ArrayLike): Strain at 0° (assumed to be ε_x); scalar or array-like.
        e45 (ArrayLike): Strain at 45°.
        e90 (ArrayLike): Strain at 90° (assumed to be ε_y).
    
    Returns:
        dict: {
            'ex': strain in x,
            'ey': strain in y,
            'gamma_xy': shear strain,
            'principal1': first principal strain,
            'principal2': second principal strain,
            'max_shear': maximum shear strain,
            'principal_angle': principal angle in radians
        }
    """
    # Accept scalar or array-like inputs.
    e0 = np.asarray(e0)
    e45 = np.asarray(e45)
    e90 = np.asarray(e90)
    
    # Compute normal and shear strains.
    ex = e0
    ey = e90
    gamma_xy = 2 * (e45 - (e0 + e90) / 2)
    
    # Compute principal strains
    prin_data = principal_strains(ex, ey, gamma_xy)
    
    return {
        'ex': ex,
        'ey': ey,
        'gamma_xy': gamma_xy,
        'principal1': prin_data['principal1'],
        'principal2': prin_data['principal2'],
        'max_shear': prin_data['max_shear'],
        'principal_angle': prin_data['principal_angle']
    }

def stress_calcs(e0: ArrayLike, e45: ArrayLike, e90: ArrayLike, E: float, nu: float) -> dict:
    """
    Compute stress components, principal stresses, maximum shear stress, and principal angle from a 0-45-90 strain gauge rosette.
    
    Parameters:
        e0 (ArrayLike): Strain at 0° (assumed to be ε_x); scalar or array-like.
        e45 (ArrayLike): Strain at 45°.
        e90 (ArrayLike): Strain at 90° (assumed to be ε_y).
        E (float): Young's modulus.
        nu (float): Poisson's ratio.
    
    Returns:
        dict: {
            'sx': stress in x,
            'sy': stress in y,
            'txy': shear stress,
            'principal1': first principal stress,
            'principal2': second principal stress,
            'max_shear': maximum shear stress,
            'principal_angle': principal angle in radians
        }
    """
    # Calculate strains
    strains = strain_calcs(e0, e45, e90)
    ex = strains['ex']
    ey = strains['ey']
    gamma_xy = strains['gamma_xy']
    
    # Compute stresses using Hooke's law for plane stress
    sx = (E / (1 - nu**2)) * (ex + nu * ey)
    sy = (E / (1 - nu**2)) * (ey + nu * ex)
    txy = (E / (2 * (1 + nu))) * gamma_xy
    
    # Compute average stress and radius for principal stresses
    prin_data = principal_stresses(sx, sy, txy)
    
    return {
        'sx': sx,
        'sy': sy,
        'txy': txy,
        'principal1': prin_data['principal1'],
        'principal2': prin_data['principal2'],
        'max_shear': prin_data['max_shear'],
        'principal_angle': prin_data['principal_angle']
    }

def principal_stresses(sx, sy, txy):
    """
    Compute the principal stresses and maximum shear stress from the stress components.
    
    Parameters:
        sx (ArrayLike): Stress in x.
        sy (ArrayLike): Stress in y.
        txy (ArrayLike): Shear stress.
    
    Returns:
        dict: {
            'principal1': first principal stress,
            'principal2': second principal stress,
            'max_shear': maximum shear stress,
            'principal_angle': principal angle in radians
        }
    """
    # Accept scalar or array-like inputs.
    sx = np.asarray(sx)
    sy = np.asarray(sy)
    txy = np.asarray(txy)

    avg = (sx + sy) / 2
    radius = np.sqrt(((sx - sy) / 2) ** 2 + txy**2)
    principal1 = avg + radius
    principal2 = avg - radius
    max_shear = radius
    principal_angle = 0.5 * np.arctan2(txy, sx - sy)

    return {
        'principal1': principal1,
        'principal2': principal2,
        'max_shear': max_shear,
        'principal_angle': principal_angle
    }

def principal_strains(ex, ey, gamma_xy):
    """
    Compute the principal strains and maximum shear strain from the strain components.
    Returns principal1, principal2, max_shear, and principal_angle.
    """
    ex = np.asarray(ex)
    ey = np.asarray(ey)
    gamma_xy = np.asarray(gamma_xy)
    avg = (ex + ey) / 2
    radius = np.sqrt(((ex - ey) / 2)**2 + (gamma_xy / 2)**2)
    principal1 = avg + radius
    principal2 = avg - radius
    max_shear = radius * 2
    principal_angle = 0.5 * np.arctan2(gamma_xy, ex - ey)
    return {
        'principal1': principal1,
        'principal2': principal2,
        'max_shear': max_shear,
        'principal_angle': principal_angle
    }

def rotate_strain_field(ex, ey, gamma_xy, angle):
    """
    Rotate the strain field by angle. 
    Returns ex', ey', gamma_x'y' in the rotated coordinate system.
    """

    ey_prime = (ex + ey)/2 - (ex - ey)/2 * np.cos(2*angle) - gamma_xy/2 * np.sin(2*angle)
    ex_prime = (ex + ey)/2 + (ex - ey)/2 * np.cos(2*angle) + gamma_xy/2 * np.sin(2*angle)
    gamma_xy_prime = -(ex - ey) * np.sin(2*angle) + gamma_xy * np.cos(2*angle)    
    # principals
    prin_data = principal_strains(ex_prime, ey_prime, gamma_xy_prime)
    return ex_prime, ey_prime, gamma_xy_prime, prin_data['principal1'], prin_data['principal2'], prin_data['max_shear'], prin_data['principal_angle']

def rotate_stress_field(sx, sy, txy, angle):
    """
    Rotate the stress field by angle. 
    Returns sx', sy', tx'y' in the rotated coordinate system.
    """
    sx_prime = (sx + sy)/2 + (sx - sy)/2 * np.cos(2*angle) + txy * np.sin(2*angle)
    sy_prime = (sx + sy)/2 - (sx - sy)/2 * np.cos(2*angle) - txy * np.sin(2*angle)
    txy_prime = -(sx - sy)/2 * np.sin(2*angle) + txy * np.cos(2*angle)    
    # principals
    prin_data = principal_stresses(sx_prime, sy_prime, txy_prime)
    return sx_prime, sy_prime, txy_prime, prin_data['principal1'], prin_data['principal2'], prin_data['max_shear'], prin_data['principal_angle']

if __name__ == '__main__':
    # Example with scalar inputs:
    e0_scalar = 0.001
    e45_scalar = 0.0015
    e90_scalar = 0.002
    result_scalar = strain_calcs(e0_scalar, e45_scalar, e90_scalar)
    print("Scalar input results:")
    print(result_scalar)

    # Example with array-like inputs:
    e0_array = np.array([0.001, 0.002, 0.003])
    e45_array = np.array([0.0015, 0.0025, 0.0035])
    e90_array = np.array([0.002, 0.003, 0.004])
    result_array = strain_calcs(e0_array, e45_array, e90_array)
    print("\nArray input results:")
    print(result_array)

    # Example with stress calculations:
    E = 200e9  # Young's modulus in Pa
    nu = 0.3  # Poisson's ratio
    stress_result = stress_calcs(e0_scalar, e45_scalar, e90_scalar, E, nu)
    print("\nStress calculation results:")
    print(stress_result)

    # Example with rotation of stress field
    sx_prime, sy_prime, txy_prime, principal1, principal2, max_shear, principal_angle = rotate_stress_field(-80, 50, -25, -30/(180/np.pi))
    print(f"\nStress field rotated by {-30} degrees:")
    print(f"sx': {sx_prime}")
    print(f"sy': {sy_prime}")
    print(f"txy': {txy_prime}")
    print(f"Principal1: {principal1}")
    print(f"Principal2: {principal2}")
    print(f"Max shear: {max_shear}")

    # Example with rotation of strain field
    ex_prime, ey_prime, gamma_xy_prime, principal1, principal2, max_shear, principal_angle = rotate_strain_field(0.001, 0.0015, 0.002, 30/(180/np.pi))
    print(f"\nStrain field rotated by {30} degrees:")
    print(f"ex': {ex_prime}")
    print(f"ey': {ey_prime}")
    print(f"gamma_x'y': {gamma_xy_prime}")
    print(f"Principal1: {principal1}")
    print(f"Principal2: {principal2}")
    print(f"Max shear: {max_shear}")

