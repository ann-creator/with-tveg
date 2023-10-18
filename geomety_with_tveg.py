from math import sqrt

import openmc
import numpy as np
from params import GeometryParams
from mat import UO2_mat, zirconi_mat, mixed_with_Gd2O3_mat,  water_mat

# Surfaces
p = GeometryParams()

# Surfaces
fuel_surf = openmc.ZCylinder(r=p.tvel_fuel_radius)
cladding_surf = openmc.ZCylinder(r=p.tvel_global_radius)
water_surf = openmc.hexagonal_prism(edge_length=p.tvel_step / sqrt(3), orientation='y', boundary_type='transmission')

tube_inner_surf = openmc.ZCylinder(r=p.tube_inner_radius)
tube_outer_surf = openmc.ZCylinder(r=p.tube_outer_radius)

abs_rod_inner_surf = openmc.ZCylinder(r=p.absorber_rod_inner_radius)
abs_rod_outer_surf = openmc.ZCylinder(r=p.absorber_rod_outer_radius)

top_surf = openmc.ZPlane(z0=p.tvel_heigh / 2)
bottom_surf = openmc.ZPlane(z0=-p.tvel_heigh / 2)

TVS_hex_lat_surf = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,)

top_surf.boundary_type = 'vacuum'
bottom_surf.boundary_type = 'vacuum'
TVS_hex_lat_surf.boundary_type='periodic'
# Geometry

# 1 TVS container
TVS_container_cell = openmc.Cell(fill=water_mat, region=TVS_hex_lat_surf & -top_surf & +bottom_surf)
TVS_container_universe = openmc.Universe(cells=[TVS_container_cell])
# 1.1 tvel in water
fuel_cell = openmc.Cell(fill=UO2_mat, region=-fuel_surf & +bottom_surf & -top_surf)
cladding_cell = openmc.Cell(fill=zirconi_mat, region=+fuel_surf & -cladding_surf & +bottom_surf & -top_surf)
water_cell = openmc.Cell(fill=water_mat, region=+cladding_surf & water_surf & +bottom_surf & -top_surf)

tvel_universe = openmc.Universe(cells=[fuel_cell, cladding_cell, water_cell])

# 1.2 tveg in water
fuel_with_Gd_cell = openmc.Cell(fill=mixed_with_Gd2O3_mat, region=-fuel_surf & +bottom_surf & -top_surf)
cladding_with_Gd_cell = openmc.Cell(fill=zirconi_mat, region=+fuel_surf & -cladding_surf & +bottom_surf & -top_surf)
water_with_Gd_cell = openmc.Cell(fill=water_mat, region=+cladding_surf & water_surf & +bottom_surf & -top_surf)

tvel_with_Gd_universe = openmc.Universe(cells=[fuel_with_Gd_cell, cladding_with_Gd_cell, water_with_Gd_cell])

# 1.3 tube in water
tube_cladding_cell = openmc.Cell(fill=zirconi_mat,
                                 region=+tube_inner_surf & -tube_outer_surf & +bottom_surf & -top_surf)
tube_water_region = -tube_inner_surf | +tube_outer_surf & water_surf
tube_water_cell = openmc.Cell(fill=water_mat, region=tube_water_region & +bottom_surf & -top_surf)

empty_tube_universe = openmc.Universe(cells=[tube_water_cell, tube_cladding_cell])

# 1.4 absorber in tube
absorber_cell = openmc.Cell(fill=water_mat, region=-abs_rod_inner_surf & +bottom_surf & -top_surf)
absorber_cladding_cell = openmc.Cell(fill=zirconi_mat,
                                     region=-abs_rod_outer_surf & +abs_rod_inner_surf & +bottom_surf & -top_surf)

abs_tube_water_inner_cell= openmc.Cell(fill=water_mat, region=+abs_rod_outer_surf & -tube_inner_surf & +bottom_surf & -top_surf)

abs_tube_cladding_cell = openmc.Cell(fill=zirconi_mat,
                                     region=+tube_inner_surf & -tube_outer_surf & +bottom_surf & -top_surf)

abs_tube_water_outer_cell = openmc.Cell(fill=water_mat, region=+tube_outer_surf & water_surf & +bottom_surf & -top_surf)
absorber_tube_universe = openmc.Universe(
    cells=[absorber_cell, absorber_cladding_cell, abs_tube_water_inner_cell, abs_tube_cladding_cell,abs_tube_water_outer_cell])
#1.4.2 tube choosing

if p.rod_inserted:
    tube_universe = absorber_tube_universe
else:
    tube_universe = empty_tube_universe

# 2. 1 TVS lattice
TVS_hex_lat = openmc.HexLattice()
TVS_hex_lat.orientation = p.orientation
TVS_hex_lat.center = (0, 0)
TVS_hex_lat.pitch = [p.tvel_step]

TVS_lat_center = [empty_tube_universe]
TVS_lat_rings = []
for i in range(1, p.n_tvel_rows):
    TVS_lat_rings.append([tvel_universe] * 6 * i)
TVS_lat_rings[2] = [tvel_universe, tvel_universe, tube_universe] * 6
TVS_lat_rings[3] = [tvel_universe, tvel_universe, tvel_universe, tvel_with_Gd_universe] * 6
TVS_lat_rings[4] = [tube_universe, tvel_universe, tvel_universe, tvel_universe, tvel_universe] * 6
TVS_lat_rings[5] = [tvel_universe, tvel_universe, tvel_universe, tube_universe, tvel_universe,
                    tvel_universe] * 6
TVS_lat_rings[7] = [tvel_with_Gd_universe, tvel_universe, tvel_universe, tvel_universe, tvel_universe, tvel_universe,
                    tvel_universe, tvel_universe] * 6
TVS_lat_rings.reverse()
TVS_hex_lat.universes = [*TVS_lat_rings, TVS_lat_center]
TVS_hex_lat.outer = TVS_container_universe

TVS_lat_cell = openmc.Cell(region=TVS_hex_lat_surf, fill=TVS_hex_lat)
universe = openmc.Universe(cells=[TVS_lat_cell])



