import openmc
import openmc.deplete
import openmc.model
from openmc import stats
import neutronics_material_maker as nmm
from mat import water_mat, UO2_mat, zirconi_mat, mixed_with_Gd2O3_mat
openmc.config['cross_sections']='/media/ann/600E180D69017994/jeff-3.3-hdf5/cross_sections.xml'
import matplotlib.pyplot as plt
from geometry_with_tveg import universe
from openmc import interp1d
from params import GeometryParams
import numpy as np
if __name__ == "__main__":
    materials = openmc.Materials([UO2_mat, water_mat, zirconi_mat, mixed_with_Gd2O3_mat])
    materials.export_to_xml()
    params = GeometryParams()
    # print(universe.get_all_materials())
    geometry=openmc.Geometry(universe)
    settings=openmc.Settings()
    uniform_dist = stats.Box([-10, -10, -350 / 2], [10, 10, 350 / 2], only_fissionable=True)
    source = openmc.source.Source(space=uniform_dist)
    source.time = stats.Uniform(0, 1)
    settings.source = source
    flux_tally = openmc.Tally(name='flux')
    flux_tally.scores = ['flux']
    U_tally = openmc.Tally(name='fuel')
    U_tally.scores = ['fission', 'total', 'absorption', 'elastic', 'scatter', 'decay-rate']
    U_tally.nuclides = ['U235', 'U238', 'O16', 'H1']
    settings.batches = 20
    settings.particles = 300
    settings.inactive = 10
    power = (3000.0e6)/163  # watts
    timesteps = [1, 3, 6, 11, 21, 36, 36, 56, 86, 126, 176, 246, 336]  # days
    model = openmc.Model(geometry, materials, settings)
    chain_file='/media/ann/600E180D69017994/chain_endfb71_pwr.xml'
    op = openmc.deplete.CoupledOperator(model, chain_file)
    openmc.deplete.CECMIntegrator(op, timesteps, power, timestep_units='d').integrate()
    results = openmc.deplete.Results("depletion_results.h5")
    time, keff = results.get_keff()

    settings.run_mode = 'fixed source'
    cecm = openmc.deplete.CECMIntegrator(operator, dt, power)
    cecm.integrate()
    source.strength = 18e0

    #colors = {
        #water_mat: (50,50,125),
        #UO2_mat: (0,125,0),
        #zirconi_mat: (20, 30, 40),
        #mixed_with_Gd2O3_mat:(100,100,250)
    #}
    #width=(4, 4)
    #plots = [openmc.Plot(), openmc.Plot(), openmc.Plot(), openmc.Plot(), ]
    #for i in range(4):
        #plots[i].width = width
        #plots[i].pixels = (1000, 1000)
        #plots[i].basis = 'xz'
        #plots[i].color_by = 'material'
        #plots[i].colors = colors
    #plots[0].origin = (0, 0, 350 / 2)
    #plots[2].origin = (0, 0, 350 /2)
    #plots[-1].basis = 'xy'
    #plots[-1].origin = (0, 0, 350/2)

    #plots = openmc.Plots(plots)
    colors = {water_mat: (120, 120, 255), zirconi_mat: 'black', UO2_mat: (0, 200, 0), mixed_with_Gd2O3_mat: (0, 100, 0)}
    color_data = dict(color_by='material', colors=colors)
    width = np.array([params.TVS_edge_length * 5.1, params.TVS_edge_length * 5.1, ])
    scale = 5.1 / 2
    fig, ax = plt.subplots(2, 2)

    universe.plot(width=width / scale, pixels=(250, 250), basis='xz', **color_data,
                  origin=(0, 0, GeometryParams.tvel_heigh / 2 - 1), axes=ax[0][0])
    universe.plot(width=width / scale, pixels=(250, 250), basis='xz', **color_data, origin=(0, 0, 0), axes=ax[1][1])
    universe.plot(width=width / scale, pixels=(250, 250), basis='xz', **color_data,
                  origin=(0, 0, -GeometryParams.tvel_heigh / 2 + 1),
                  axes=ax[0][1])
    universe.plot(width=width / scale, pixels=(250, 250), basis='xy', **color_data, origin=(0, 0, 0), axes=ax[1][0])
    plt.savefig('geometry.jpg')

    # ...and by openmc.Plots
    plots = [openmc.Plot(), openmc.Plot(), openmc.Plot(), openmc.Plot(), ]
    for i in range(4):
        plots[i].width = width
        plots[i].pixels = (500, 500)
        plots[i].basis = 'xz'
        plots[i].color_by = 'material'
        plots[i].colors = colors
    plots[0].origin = (0, 0, GeometryParams.tvel_heigh / 2 - 1)
    plots[2].origin = (0, 0, -GeometryParams.tvel_heigh / 2 - 1)
    plots[-1].basis = 'xy'

    plots = openmc.Plots(plots)
    tallies_file=openmc.Tallies([flux_tally, U_tally])
    tallies_file.export_to_xml()


    plots.export_to_xml('plots.xml')
    settings.export_to_xml('settings.xml')
    geometry.export_to_xml('geometry.xml')
    model.export_to_xml('model.xml')
    openmc.plot_geometry()
    openmc.run()