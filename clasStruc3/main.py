# File: entrypoint.py
# Purpose: Entry script to initialize and run the train simulation and report pipeline.

import os
import logging
import pandas as pd

from simulation.setup import prepare_directories, load_paths, read_all_inputs
from simulation.analysis import compute_traffic_and_energy, run_simulation
from simulation.reporting import generate_report_and_outputs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="train_simulation.log",
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        # Step 1: Setup
        input_dirs, output_dirs = prepare_directories()
        paths = load_paths(input_dirs, output_dirs)

        # Step 2: Read input data
        inputs = read_all_inputs(paths)

        # Step 3: Perform calculations
        traffic_data, energy_data = compute_traffic_and_energy(inputs)

        # Step 4: Run physical simulation
        log_df, total_mass = run_simulation(inputs)

        run_dist = log_df['Total Distance (km)'].iloc[0]
        run_time = log_df['Total Time (min)'].iloc[0]
        run_speed = log_df['Average Speed (km/h)'].iloc[0]

        logging.info(f"Train_wt: {total_mass} tons")
        logging.info(f"Average speed for the trip was: {run_speed:.2f} km/hr")
        logging.info(f"A total distance of {run_dist:.2f} Km was covered in {run_time:.2f} minutes.")

        # Step 5: Generate report and outputs
        generate_report_and_outputs(paths, inputs, traffic_data, energy_data, log_df, output_dirs)

        print("\nSimulation complete. Output files generated.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == '__main__':
    main()
