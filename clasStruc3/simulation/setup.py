# File: simulation/setup.py
import os

from reader.dpr_reader import ConfigReader
from reader.speed_reader import CsvDataReader

def prepare_directories():
    """Create input and output directories if they don't exist."""
    cwd = os.getcwd()
    input_dirs = {
        'dpr': os.path.join(cwd, 'inputs', 'dpr'),
        'speed': os.path.join(cwd, 'inputs', 'speed')
    }
    output_dirs = {
        'dpr': os.path.join(cwd, 'output', 'dpr'),
        'speed': os.path.join(cwd, 'output', 'speed')
    }

    for path in input_dirs.values():
        os.makedirs(path, exist_ok=True)
    for path in output_dirs.values():
        os.makedirs(path, exist_ok=True)

    return input_dirs, output_dirs

def load_paths(input_dirs, output_dirs):
    """Build full file paths for I/O operations."""
    return {
        'image_file_dpr': os.path.join(output_dirs['dpr'], 'normalised.png'),
        'input_file_dpr': os.path.join(input_dirs['dpr'], 'input_data.csv'),
        'train_params': os.path.join(input_dirs['speed'], 'train_parameters.csv'),
        'stations': os.path.join(input_dirs['speed'], 'stations.csv'),
        'curves': os.path.join(input_dirs['speed'], 'curves.csv'),
        'gradients': os.path.join(input_dirs['speed'], 'gradients.csv'),
        'curve_sr': os.path.join(input_dirs['speed'], 'sr.csv'),
    }

def read_all_inputs(paths):
    """Read all input files and return a unified dictionary of usable data."""

    # Read DPR input file
    reader = ConfigReader(paths['input_file_dpr'])
    reader.read()

    # Read speed profile input files
    reader_speed = CsvDataReader(
        paths['train_params'],
        paths['stations'],
        paths['curves'],
        paths['gradients'],
        paths['curve_sr']
    )

    return {
        'corridor': reader.corridor,
        'daily_ridership': reader.daily_ridership,
        'train_info': reader.train_info,
        'power': reader.power,
        'working': reader.working,
        'years': reader.years,
        'phpdt': reader.phpdt,
        'train_comp': reader.train_comp,
        'tare': reader.tare,
        'params': reader.params,
        'params_speed': reader_speed.read_train_parameters(),
        'stations': reader_speed.read_stations(),
        'curves': reader_speed.read_curves(),
        'gradients': reader_speed.read_gradients(),
        'curve_sr': reader_speed.read_curve_speed_restrictions(),
    }
