# File: simulation/reporting.py
import os
import pandas as pd

from dpr.dpr_report import MetroReportGenerator
from plotter.dpr_plotter import TransitPlotGenerator
from plotter.speed_plotter import Plotter

def generate_report_and_outputs(paths, inputs, traffic_data, energy_data, log_df, output_dirs):
    # Plot chart
    plotter = TransitPlotGenerator(
        years=inputs['years'],
        ridership=inputs['daily_ridership'],
        phpdt=inputs['phpdt'],
        headway=traffic_data['headways'],
        train_number=traffic_data['trains'],
        image_filename=paths['image_file_dpr']
    )
    plotter.generate_plot()

    # Generate report
    report = MetroReportGenerator(
        corridor=inputs['corridor'],
        parameters=inputs['params'],
        train_composition=inputs['train_comp'],
        capacity=traffic_data['capacity'],
        years=inputs['years'],
        tfc_labels=["Daily Ridership", "PHPDT", "Headway (min)", "Number of Trains"],
        data={"DailyRidership": inputs['daily_ridership'], "PHPDT": inputs['phpdt']},
        yearly_headways=traffic_data['headways'],
        yearly_trains=traffic_data['trains'],
        section=["Traffic Forecast", "Power Requirements"],
        tpower=inputs['power'],
        apower=inputs['power'],
        pw_labels=[
            "Traction Energy (MWh/day)",
            "Traction Energy (MWh/year)",
            "Auxiliary Energy (MWh/day)",
            "Auxiliary Energy (MWh/year)",
            "Total Energy (MWh/day)",
            "Total Energy (MWh/year)"
        ],
        trc_energy=(energy_data['energy_raw'], energy_data['energy_eff']),
        aux_energy=(energy_data['aux_raw'], energy_data['aux_eff']),
        total_energy=(energy_data['total_units'], energy_data['max_demand']),
        image_filename=paths['image_file_dpr'],
        output_dir_dpr=output_dirs['dpr']
    )

    doc_path = report.generate()
    print(f"\nReport saved at: {doc_path}")

    # Excel output with plots
    excel_path = os.path.join(output_dirs['speed'], 'run_output.xlsx')
    speed_png = os.path.join(output_dirs['speed'], 'speed_profile.png')
    energy_png = os.path.join(output_dirs['speed'], 'energy_profile.png')

    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        log_df.to_excel(writer, index=False, sheet_name='Log')
        ws = writer.sheets['Log']
        plotter = Plotter()
        plotter.plot(log_df, speed_png, energy_png)
        ws.insert_image('F2', speed_png)
        ws.insert_image('F30', energy_png)

    print(f"Run complete. Output at {excel_path}")
