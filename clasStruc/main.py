import logging

from dpr_train import TrainsRequirement
from dpr_power import EnergyRequirement

from data_reader import ConfigReader
from report_generator import MetroReportGenerator
from plot_generator import TransitPlotGenerator


# Configure logging
logging.basicConfig(level=logging.INFO, filename="train_simulation.log", filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    # Set image filename
    image_file = "./report/normalised.png"

    try:
        # Read and store Traffic, Section and Train Data
        reader = ConfigReader("./inputs/input_data.csv")
        reader.read()

        corridor_name = reader.corridor
        ridership = reader.daily_ridership
        capacity_info = reader.train_info
        power = reader.power
        working = reader.working
        diversity_factor = reader.power["DF"]
        years = reader.years
        phpdt = reader.phpdt
        train_comp = reader.train_comp
        tare = reader.tare
        params = reader.params

        # Compute the Traffic and Train Parameters
        train_require = TrainsRequirement(capacity_info, phpdt, params, tare, train_comp)
        energy_require = EnergyRequirement(power, working)

        capacity = train_require.compute_capacity("AW3")
        capacity_aw4 = train_require.compute_capacity("AW4")
        headways = train_require.compute_headways(capacity)
        trains = train_require.compute_train_requirements(headways)
        train_weight, axle_loads = train_require.compute_aw4_weights(capacity_aw4)
        energy_raw, energy_eff = energy_require.compute_traction_energy(headways,
                                        params["section_length"], train_weight)
        aux_raw, aux_eff = energy_require.compute_auxiliary_energy(years)
        total_units, max_demand = energy_require.compute_total_energy(energy_eff,
                                                        aux_eff, years)

        # Output
        #print(f'Corridor Name: {corridor}')
        print(f"Total Capacity:{capacity}")
        #print(f'Train Composition:{train_comp}')
        #print(f'PHPDT:{phpdt}')
        print("Yearly Headways:", headways)
        print("Trains Required:", trains)
        print("Train Weight (AW4) and Axle Loads:", train_weight, axle_loads)
        print("Traction Energy with Regeneration:", energy_eff)
        print("Aux Energy Efficiency:", aux_eff)
        print("Total Units and Max Demand:", total_units, max_demand)

        # Logging summary
        logging.info(f"Train Capacity (AW3): {capacity} passengers")
        logging.info(f"Yearly Headways in minutes: {headways} " )
        logging.info(f"Train Requirements: {trains} Trainset required" )
        logging.info(f"Total Train Weight: {train_weight} tons")
        logging.info(f"Axle Loads: {axle_loads} tons per axle")
        logging.info(f"Traction Energy in MW: {energy_eff} ")
        logging.info(f"Auxiliary Energy in MW: {aux_eff} ")
        logging.info(f"Total Energy in Million Units: {total_units} ")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

    # Generate the normalized plot and save to disk
    plotter = TransitPlotGenerator(
        years=years,
        ridership=ridership,
        phpdt=phpdt,
        headway=headways,
        train_number=trains,
        image_filename=image_file
    )
    plotter.generate_plot()

    report = MetroReportGenerator(
        corridor=corridor_name,
        parameters=params,
        train_composition=train_comp,
        capacity=capacity,
        years=years,
        tfc_labels=["Daily Ridership", "PHPDT", "Headway (min)", "Number of Trains"],
        data={"DailyRidership": ridership, "PHPDT": phpdt},
        yearly_headways=headways,
        yearly_trains=trains,
        section=["Traffic Forecast", "Power Requirements"],
        tpower=power,
        apower=power,
        pw_labels=[
            "Traction Energy (MWh/day)",
            "Traction Energy (MWh/year)",
            "Auxiliary Energy (MWh/day)",
            "Auxiliary Energy (MWh/year)",
            "Total Energy (MWh/day)",
            "Total Energy (MWh/year)"
        ],
        trc_energy=(energy_raw, energy_eff),
        aux_energy=(aux_raw, aux_eff),
        total_energy=(total_units, max_demand),
        image_filename=image_file  # make sure your plot was saved with this name
    )

    doc_path = report.generate()
    print(f"\n Report saved at: {doc_path}")

if __name__ == '__main__':
    main()
