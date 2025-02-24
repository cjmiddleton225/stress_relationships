# 
import plotly.express as px
import pandas as pd
import sys
import os
dir_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(dir_path, '..')))
from strain_gauge import strain_gauge_rosette_0_45_90 as sg

# variables
rotate_angle = 0/(180/3.14159)

# Load data
data = pd.read_csv('./sample data/GT6.csv')
print(data.head())

# Compute strains and stresses
strains = sg.strain_calcs(data['SO-GT6-Red'], data['SO-GT6-Yellow'], data['SO-GT6-White'])
stresses = sg.stress_calcs(data['SO-GT6-Red'], data['SO-GT6-Yellow'], data['SO-GT6-White'], 200e9, 0.3)

# Create a DataFrame for output
df = pd.DataFrame({
    'Time (s)': data['time (s)'],
    'Strain 0°': strains['ex'],
    'Strain 45°': strains['gamma_xy'],
    'Strain 90°': strains['ey'],
    'principal1': strains['principal1'],
    'principal2': strains['principal2'],
    'max_shear': strains['max_shear'],
    'principal_angle': strains['principal_angle']*180/3.14159,
    'Stress 0° (MPa)': stresses['sx']*1e-6,
    'Stress 45° (MPa)': stresses['txy']*1e-6,
    'Stress 90° (MPa)': stresses['sy']*1e-6,
    'Stress principal1 (MPa)': stresses['principal1']*1e-6,
    'Stress principal2 (MPa)': stresses['principal2']*1e-6,
    'Stress max_shear (MPa)': stresses['max_shear']*1e-6,
    'Stress principal_angle': stresses['principal_angle']*180/3.14159,
    'Mean stress (MPa)': (stresses['principal1'] + stresses['principal2'])*1e-6/2
})

# rotate strains and stresses
df['Strain 0°'], df['Strain 90°'], df['Strain 45°'], df['principal1'], df['principal2'], df['max_shear'], df['principal_angle'] = sg.rotate_strain_field(df['Strain 0°'], df['Strain 90°'], df['Strain 45°'], rotate_angle)
df['principal_angle'] = df['principal_angle']*180/3.14159
df['Stress 0° (MPa)'], df['Stress 90° (MPa)'], df['Stress 45° (MPa)'], df['Stress principal1 (MPa)'], df['Stress principal2 (MPa)'], df['Stress max_shear (MPa)'], df['Stress principal_angle'] = sg.rotate_stress_field(df['Stress 0° (MPa)'], df['Stress 90° (MPa)'], df['Stress 45° (MPa)'], rotate_angle)
df['Stress principal_angle'] = df['Stress principal_angle']*180/3.14159
df.to_csv(f'./sample data/GT6_processed_{int(rotate_angle*180/3.14519)}deg.csv', index=False)

# copy of df with top 20% abs principal1 and principal2 stresses
df_top20 = df[(df['Stress principal1 (MPa)'].abs() > df['Stress principal1 (MPa)'].abs().quantile(0.8)) | (df['Stress principal2 (MPa)'].abs() > df['Stress principal2 (MPa)'].abs().quantile(0.8))]

# histogram of princiapl angle
fig = px.histogram(df_top20, x='principal_angle', nbins=20)
fig.write_image(f"./examples/outputs/GT6_principal_angle.png")
fig = px.histogram(df_top20, x='Stress principal_angle', nbins=20)
fig.write_image(f"./examples/outputs/GT6_Stress_principal_angle_{int(rotate_angle*180/3.14159)}deg.png")

# scatter plot of principal stresses1 vs principal angle
fig = px.scatter(df_top20, x='Stress principal_angle', y='Stress principal1 (MPa)', color='Stress principal2 (MPa)')
fig.write_image(f"./examples/outputs/GT6_principal1_vs_principal2_{int(rotate_angle*180/3.14159)}deg.png")

# scatter plot of principal stresses2 vs principal angle
fig = px.scatter(df_top20, x='Stress principal_angle', y='Stress principal2 (MPa)', color='Stress principal1 (MPa)')
fig.write_image(f"./examples/outputs/GT6_principal2_vs_principal1_{int(rotate_angle*180/3.14519)}deg.png")

# scatter plot of max shear stress vs principal angle
fig = px.scatter(df_top20, x='Stress principal_angle', y='Stress max_shear (MPa)')
fig.write_image(f"./examples/outputs/GT6_max_shear_vs_principal_angle_{int(rotate_angle*180/3.14159)}deg.png")

# plot mean stress vs principal angle
fig = px.scatter(df_top20, x='Stress principal_angle', y='Mean stress (MPa)')
fig.write_image(f"./examples/outputs/GT6_mean_stress_vs_principal_angle_{int(rotate_angle*180/3.14519)}deg.png")
