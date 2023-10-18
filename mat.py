import openmc
from openmc.data import NATURAL_ABUNDANCE
import math
from math import pi
import neutronics_material_maker as nmm
r=0.235
R=0.757
h=353
V=pi*(R**2-r**2)*h

water_mat=openmc.Material(name='water')
water_mat.add_nuclide('H1', 2.*0.999885, percent_type='ao')
water_mat.add_nuclide('H2', 2.*0.000115, percent_type='ao')
water_mat.add_nuclide('O16', 0.99757, percent_type='ao')
water_mat.add_nuclide('O17', 0.00038, percent_type='ao')
water_mat.add_nuclide('O18', 0.00205, percent_type='ao')
water_mat.set_density('g/cm3', 0.99821)
UO2_mat=openmc.Material(name='UO2')
UO2_mat.add_element('U', 1.0,  enrichment=1.6)
UO2_mat.add_element('O', 2.0)
UO2_mat.set_density('g/cm3', 10.4)
UO2_mat.volume=V
#zirconi_mat=openmc.Material()
#zirconi_mat.add_element('Zr', 0.99)
#zirconi_mat.add_element('Nb', 0.01)
#zirconi_mat.set_density('g/cm3', 6.55)
Gd2O3_mat=openmc.Material()
Gd2O3_mat.add_element('Gd', 2.0, percent_type='ao')
Gd2O3_mat.add_element('O', 3.0, percent_type='ao')
Gd2O3_mat.set_density( 'g/cm3', 7.41)
mixed_with_Gd2O3_mat=openmc.Material.mix_materials(
    materials=[
        UO2_mat,
        Gd2O3_mat,
    ],
    fracs=[0.95, 0.05],
    percent_type='vo')
mixed_with_Gd2O3_mat.volume=R**2*pi*350*18*7
helium_mat=openmc.Material(name='Helium')
helium_mat.add_element('He', 1.0)
helium_mat.set_density('g/cm3', 0.178e-3)
water_mat = nmm.Material.from_library(name='Water, Liquid').openmc_material
cladding_mat = nmm.Material.from_library(name='Zircaloy-2').openmc_material
absorber_mat = nmm.Material.from_library(name='Boron Carbide (B4C)').openmc_material
tube_mat=nmm.Material.from_library(name='SS_316L_N_IG').openmc_material