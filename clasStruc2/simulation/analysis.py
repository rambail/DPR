# File: simulation/analysis.py
from dpr.dpr_train import TrainsRequirement
from dpr.dpr_power import EnergyRequirement
from speed.simulator import MetroSimulator


def compute_traffic_and_energy(inputs):
    """
    Compute train capacity, headway, weight and energy demands.
    """
    # Unpack inputs
    capacity_info = inputs['train_info']
    phpdt = inputs['phpdt']
    params = inputs['params']
    tare = inputs['tare']
    train_comp = inputs['train_comp']
    power = inputs['power']
    working = inputs['working']
    years = inputs['years']
    section_length = params['section_length']

    # Train requirement computation
    train_require = TrainsRequirement(capacity_info, phpdt, params, tare, train_comp)
    result = train_require.compute_dpr_data()
    capacity, capacity_aw4, headways, trains, train_weight, axle_loads = result

    # Energy requirement computation
    energy_require = EnergyRequirement(power, working, headways, section_length, train_weight, years)
    result = energy_require.compute_dpr_data()
    energy_raw, energy_eff, aux_raw, aux_eff, total_units, max_demand = result

    return (
        {
            'capacity': capacity,
            'capacity_aw4': capacity_aw4,
            'headways': headways,
            'trains': trains,
            'train_weight': train_weight,
            'axle_loads': axle_loads
        },
        {
            'energy_raw': energy_raw,
            'energy_eff': energy_eff,
            'aux_raw': aux_raw,
            'aux_eff': aux_eff,
            'total_units': total_units,
            'max_demand': max_demand
        }
    )


def run_simulation(inputs):
    """
    Initialize MetroSimulator with track and curve data and run the simulation.
    """
    sim = MetroSimulator(
        inputs['params_speed'],
        inputs['stations'],
        inputs['curves'],
        inputs['gradients'],
        inputs['curve_sr']
    )

    log_df = sim.simulate()
    return log_df, sim.total_mass
