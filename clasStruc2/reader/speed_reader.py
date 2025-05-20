## reader.py
import pandas as pd

class CsvDataReader:
    """
    Reads and standardizes CSV files for train parameters, stations, curves, gradients,
    and curve-based speed restriction mappings.
    """
    def __init__(self, train_params_path, stations_path,
                 curves_path=None, gradients_path=None,
                 curve_sr_path=None):
        self.train_params_path = train_params_path
        self.stations_path = stations_path
        self.curves_path = curves_path
        self.gradients_path = gradients_path
        self.curve_sr_path = curve_sr_path

    def read_train_parameters(self) -> dict:
        df = pd.read_csv(self.train_params_path)
        params = {}
        for _, row in df.iterrows():
            key = str(row['Parameter']).strip()
            value = row['Value']
            # Try to convert to float if possible
            try:
                params[key] = float(value)
            except (ValueError, TypeError):
                params[key] = str(value).strip()
        return params

    def read_stations(self) -> pd.DataFrame:
        df = pd.read_csv(self.stations_path)
        return df.rename(columns={'Chainage': 'chainage', 'Station_Name': 'name'})

    def read_curves(self) -> pd.DataFrame:
        if not self.curves_path:
            return None
        df = pd.read_csv(self.curves_path)
        return df.rename(columns={'Start': 'start', 'End': 'end', 'Radius': 'radius'})

    def read_gradients(self) -> pd.DataFrame:
        if not self.gradients_path:
            return None
        df = pd.read_csv(self.gradients_path)
        return df.rename(columns={'Start': 'start', 'End': 'end', 'Ratio': 'gradient'})

    def read_curve_speed_restrictions(self) -> pd.DataFrame:
        """
        Reads a mapping from curve radius to max speed.
        Expects CSV with columns 'Radius','Speed'.
        """
        if not self.curve_sr_path:
            return None
        df = pd.read_csv(self.curve_sr_path)
        return df.rename(columns={'Radius': 'radius', 'Speed': 'speed'})

    def read_curve_speed_restrictions(self) -> pd.DataFrame:
        """
        Reads a mapping from curve radius to max speed.
        Automatically finds the radius and speed columns even if named differently.
        """
        if not self.curve_sr_path:
            return None
        df = pd.read_csv(self.curve_sr_path)
        # normalize column names
        df.columns = [c.strip().lower() for c in df.columns]
        # detect radius column
        radius_col = next((c for c in df.columns if 'radius' in c), None)
        speed_col = next((c for c in df.columns if 'speed' in c or 'restrict' in c), None)
        if not radius_col or not speed_col:
            raise KeyError(f"Cannot find 'radius' or 'speed' columns in SR file: {df.columns.tolist()}")
        df = df[[radius_col, speed_col]].rename(columns={radius_col: 'radius', speed_col: 'speed'})
        return df
