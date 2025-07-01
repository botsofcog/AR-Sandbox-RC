from sandbox import _test_data as test_data
from sandbox.modules import LandslideSimulation
import matplotlib.pyplot as plt
import pytest
import numpy as np
file = np.load(test_data['topo'] + "DEM1.npz")
frame = file['arr_0']
extent = [0, frame.shape[1], 0, frame.shape[0], frame.min(), frame.max()]


def load_marker():
    import pandas as pd
    from sandbox import _test_data
    arucos = _test_data['test'] + "arucos.pkl"
    try:
        df = pd.read_pickle(arucos)
        print("Arucos loaded")
    except:
        df = pd.DataFrame()
        print("No arucos found")
    return df

fig, ax = plt.subplots()
pytest.sb_params = {'frame': frame,
                    'ax': ax,
                    'fig': fig,
                    'extent': extent,
                    'marker': load_marker(),
                    'cmap': plt.cm.get_cmap('gist_earth_r'),
                    'norm': None,
                    'active_cmap': True,
                    'active_contours': True}

def update(module):
    pytest.sb_params['ax'].cla()
    sb_params = module.update(pytest.sb_params)
    ax = sb_params['ax']
    fig = sb_params['fig']
    ax.imshow(sb_params.get('frame'), vmin=sb_params.get('extent')[-2], vmax=sb_params.get('extent')[-1],
              cmap=sb_params.get('cmap'), norm=sb_params.get('norm'), origin='lower')
    fig.show()


def test_init():
    module = LandslideSimulation(extent=extent)
    print(module)

def test_update():
    module = LandslideSimulation(extent=extent)
    update(module)

def test_load_simulation():
    module = LandslideSimulation(extent=extent)
    module.load_simulation_data_npz(test_data['landslide_simulation']+'Sim_Topo1_Rel13_results4sandbox.npz')
    assert module.velocity_flow is not None and module.height_flow is not None

def test_load_release_area():
    module = LandslideSimulation(extent=extent)
    module.Load_Area.loadTopo(test_data['landslide_topo']+'Topography_3.npz')
    assert module.Load_Area.file_id == '3'

    module.load_release_area(test_data['landslide_release'])
    lst = ['ReleaseArea_3_1.npy', 'ReleaseArea_3_2.npy','ReleaseArea_3_2.npy']
    assert [i in lst for i in module.release_options]
    lst2 = ['1', '2', '3']
    assert [i in lst for i in module.release_id_all]

def test_show_box_release():
    module = LandslideSimulation(extent=extent)
    module.Load_Area.loadTopo(test_data['landslide_topo'] + 'Topography_3.npz')
    module.load_release_area(test_data['landslide_release'])
    module.modify_to_box_coordinates(id = '1')
    fig, ax = plt.subplots()
    ax.imshow(frame, vmin=extent[-2], vmax=extent[-1], cmap='gist_earth_r',origin='lower')
    module.show_box_release(ax, module.release_area)
    #TODO assert np.allclose(np.asarray([[74., 72.], [74., 84.],[86., 84.],[86., 72.]]), module.release_area)
    fig.show()

def test_plot_landslide():
    module = LandslideSimulation(extent=extent)
    module.load_simulation_data_npz(test_data['landslide_simulation'] + 'Sim_Topo1_Rel13_results4sandbox.npz')
    module.flow_selector = "Velocity"
    module.frame_selector = 10
    fig, ax = plt.subplots()
    ax.imshow(frame, vmin=extent[-2], vmax=extent[-1], cmap='gist_earth_r', origin='lower')
    module.plot_landslide_frame(ax)
    fig.show()

    module.flow_selector = "Height"
    ax.cla()
    ax.imshow(frame, vmin=extent[-2], vmax=extent[-1], cmap='gist_earth_r', origin='lower')
    module.plot_landslide_frame(ax)
    fig.show()

def test_panel_plot():
    module = LandslideSimulation(extent=extent)
    module.load_simulation_data_npz(test_data['landslide_simulation'] + 'Sim_Topo1_Rel13_results4sandbox.npz')
    module.frame_selector = 10
    module.plot_frame_panel()
    module.plot_flow_frame.show()

def test_show_widgets():
    module = LandslideSimulation(extent=extent)
    module.load_simulation_data_npz(test_data['landslide_simulation'] + 'Sim_Topo1_Rel13_results4sandbox.npz')
    module.flow_selector = "Velocity"
    module.frame_selector = 10
    landslide = module.show_widgets()
    landslide.show()



