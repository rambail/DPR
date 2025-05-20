import csv

class ConfigReader:
    """
    Reads corridor configuration and forecasting data from a structured CSV.

    The CSV must include rows for:
      Corridor, Year, DailyRidership, PHPDT,
      Dmc, Tc,
      TrainComp, Parameters, TareWeight,
      TrPower, AuxPower, Working.

    After `reader.read()`, exposes:
      - reader.corridor (str)
      - reader.years (list of years)
      - reader.daily_ridership, reader.phpdt (dicts)
      - reader.train_info (dict of coach capacities)
      - reader.train_comp (list of coach codes)
      - reader.params (avg_speed, section_length, reversal_time)
      - reader.tare (tare weights and passenger weight)
      - reader.power (traction & auxiliary power params + DF)
      - reader.working (operational hours & days)
    """
    def __init__(self, filename):
        self.filename = filename
        self.corridor = {}
        self.years = []
        self.daily_ridership = {}
        self.phpdt = {}
        self.train_info = {}
        self.train_comp = []
        self.params = {}
        self.tare = {}
        self.power = {}
        self.working = {}

    def read(self):
        with open(self.filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            #print(len(rows))

            for row in rows:
                label = row[0].strip()
                # Look for rows with label "Corridor"
                if label.lower() == "corridor":
                    try:
                        self.corridor = row[1].strip()
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.corridor = None
                elif label.lower() == "year":
                    try:
                        # Read years
                        self.years = row[1:]
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.years = None
                elif label.lower() == "dailyridership":
                    try:
                        # Daily Ridership
                        ridership_vals = row[1:]
                        self.daily_ridership = {year: float(val) for year, val
                                                in zip(self.years, ridership_vals)}
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.daily_ridership = {0}
                elif label.lower() == "phpdt":
                    try:
                        # PHPDT
                        phpdt_vals = row[1:]
                        #print(self.years)
                        self.phpdt = {year: float(val) for year, val
                                        in zip(self.years, phpdt_vals)}
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.phpdt = {0}
                elif label.lower() in {"dmc", "tc"}:
                    # For Dmc and Tc, expect three numbers:
                    # seating capacity, AW3 standing, AW4 standing.
                    try:
                        self.train_info[label] = {
                            "seat": int(row[1]) if len(row) > 1 else 0,
                            "AW3": int(row[2]) if len(row) > 2 else 0,
                            "AW4": int(row[3]) if len(row) > 3 else 0,
                        }
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.train_info[label] = {"seat": 0, "AW3": 0, "AW4": 0}
                elif label.lower() == "traincomp":
                    # For TrainComp, assume the composition is given
                    # as a comma-separated string in one cell. Alternatively,
                    # if provided in multiple cells, this will also capture them.
                    try:
                        if len(row) == 2:
                            comp_list = [item.strip() for item in row[1].split(',') if item.strip()]
                        else:
                            comp_list = [item.strip() for item in row[1:] if item.strip()]
                        self.train_comp = comp_list
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.train_comp = ['']
                elif label.lower() == 'parameters':
                    # Parameters
                    try:
                        average_speed, section_length, reversal_time = map(float, row[1:4])
                        self.params = {
                            "average_speed": average_speed,
                            "section_length": section_length,
                            "reversal_time": reversal_time
                        }
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.train_comp = {0}
                elif label.lower() == 'tareweight':
                    # Parameters
                    try:
                        dmc, tc, pass_wt = map(float, row[1:4])
                        self.tare = {
                            "DMC": dmc,
                            "TC": tc,
                            "MC": dmc,  # assuming DMC and MC are same weight
                            "PassWt": pass_wt
                        }
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.tare = {0}
                elif label.lower() == 'trpower':
                    # Traction power
                    try:
                        sec, regen, tr_loss, tr_pf, depot_tp = map(float, row[1:6])
                        self.power = {
                            "SEC": sec,
                            "Regen": regen,
                            "TrLoss": tr_loss,
                            "TrPF": tr_pf,
                            "DepotTP": depot_tp
                        }
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.power = {0}
                elif label.lower() == 'auxpower':
                    # Traction power
                    try:
                        el_stn_pwr, el_stn_nos, ug_stn_pwr, ug_stn_nos, dp_pwr, dp_nos, aux_loss, aux_pf, df = map(float, row[1:10])
                        self.power.update({
                            "ElStnPwr": el_stn_pwr,
                            "ElStnNos": el_stn_nos,
                            "UGStnPwr": ug_stn_pwr,
                            "UGStnNos": ug_stn_nos,
                            "DpPwr": dp_pwr,
                            "DpNos": dp_nos,
                            "AuxLoss": aux_loss,
                            "AuxPF": aux_pf,
                            "DF": df
                        })
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.power = {0}
                elif label.lower() == 'working':
                    try:
                        hours, days = map(int, row[1:3])
                        self.working = {"Hours": hours, "Days": days}
                    except ValueError:
                        print(f"Error converting values for {label}.")
                        self.working = {0}
