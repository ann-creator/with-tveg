from math import sqrt

import openmc
from mat import helium, zirconi_mat, water_mat, UO2_mat, mixed_with_Gd2O3_mat

STEP=12.75/10
n_rows=11

cyl_H=openmc.ZCylinder(r=7.72/20, surface_id=765)
plane_v=openmc.ZPlane(z0=352, surface_id=345)
plane_n=openmc.ZPlane(z0=0, surface_id=232)
plane_v.boundary_type='vacuum'
plane_n.boundary_type='vacuum'
cyl_ob=openmc.ZCylinder(r=9.1/20, surface_id=123)
water_surf = openmc.hexagonal_prism(edge_length=12.75/sqrt(3), orientation='x', boundary_type='transmission')
cyl_mal=openmc.ZCylinder(r=2.35/20, surface_id=678)
cyl_bol=openmc.ZCylinder(r=7.57/20, surface_id=895)
hel_vol=(-cyl_mal | (-cyl_H & +cyl_bol)) & -plane_v & +plane_n
#ТВЭЛ
cell1=openmc.Cell(fill=helium, region=hel_vol, cell_id=5)
cell2=openmc.Cell(fill=zirconi_mat, region=-cyl_ob & +cyl_H & -plane_v & +plane_n, cell_id=6)
cell3=openmc.Cell(fill=water_mat, region=water_surf & +cyl_ob & -plane_v & +plane_n, cell_id=3)
cell_fuel=openmc.Cell(fill=UO2_mat, region=-cyl_bol & +cyl_mal & -plane_v & +plane_n, cell_id=7)
#fuel=openmc.DAGMCUniverse(filename='/home/ann/PycharmProjects/python3.9/dagmc.h5m',auto_geom_ids=True)
# print(fuel.n_surfaces)
#cell4=openmc.Cell(fill=fuel, region=-cyl_bol & +cyl_mal & -plane_v & +plane_n, cell_id=4)
#ТВЭГ
Gd_cell=openmc.Cell(fill=mixed_with_Gd2O3_mat, region=-cyl_bol & +cyl_mal & -plane_v & +plane_n, cell_id=9)
cladding_Gd_cell=openmc.Cell(fill=zirconi_mat, region=-cyl_ob & +cyl_H & -plane_v & +plane_n, cell_id=11)
univers_one_tvel=openmc.Universe(cells=[cell1, cell2, cell3, cell_fuel])

TVS_hex_lat_surf = openmc.hexagonal_prism(edge_length=n_rows*STEP, orientation='y', boundary_type='reflective')

hex_lat = openmc.HexLattice(lattice_id=228)
hex_lat.orientation = 'y'
hex_lat.center = (0, 0)
hex_lat.pitch = [STEP]

lat_center=[univers_one_tvel]
lat_rings=[]
for i in range(1,n_rows):
    lat_rings.append([univers_one_tvel]*(6*i))

lat_rings.reverse()

hex_lat.universes=[*lat_rings, lat_center]

cell5=openmc.Cell(fill=water_mat,region=TVS_hex_lat_surf & -plane_v & +plane_n)
univers_con=openmc.Universe(cells=[cell5, ])

hex_lat.outer=univers_con

cell6=openmc.Cell(fill=hex_lat, region=TVS_hex_lat_surf & -plane_v & +plane_n)
universe=openmc.Universe(cells=[cell6, ])





