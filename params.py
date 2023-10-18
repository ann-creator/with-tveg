from math import sqrt


class GeometryParams:
    tvel_fuel_radius = 0.757 / 2
    tvel_global_radius = 0.91 / 2
    tvel_heigh = 350.0

    orientation = 'x'

    n_tvel_rows = 11
    tvel_step = 1.275

    tube_outer_radius = 1.26 / 2
    tube_inner_radius = 1.26 / 2 - 0.085

    absorber_rod_inner_radius = tvel_fuel_radius
    absorber_rod_outer_radius = tvel_global_radius

    rod_inserted = True
    TVS_edge_length=14.025
