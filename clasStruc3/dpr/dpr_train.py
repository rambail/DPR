import math

class TrainsRequirement:
    def __init__(self, capacity_info, phpdt_dict, params, tare_dict, train_composition):
        """
        Initialize the simulator with all necessary data.

        Parameters:
            train_info (dict): Coach capacities for "Dmc" and "Tc", each with "seat", "AW3", and "AW4".
            phpdt_dict (dict): Year-wise PHPDT values.
            avg_speed (float): Average speed in km/h.
            section_length (float): Section length in km.
            reversal_time (float): Reversal time in minutes.
            tare_dict (dict): Tare weights for car types and average passenger weight in kg.
        """
        self.dmc_info = capacity_info.get("Dmc", {})
        self.tc_info = capacity_info.get("Tc", {})
        self.phpdt_dict = phpdt_dict
        self.avg_speed = params.get("average_speed", {})
        self.section_length = params.get("section_length", {})
        self.reversal_time = params.get("reversal_time", {})
        self.tare_dict = tare_dict
        self.train_composition = train_composition

    def compute_capacity(self,  load_type):
        if isinstance(self.train_composition, str):
            comp_list = [item.strip().upper() for item in self.train_composition.split(',') if item.strip()]
        else:
            comp_list = [item.strip().upper() for item in self.train_composition]

        dmc_capacity = self.dmc_info.get("seat", 0) + self.dmc_info.get(load_type, 0)
        tc_capacity = self.tc_info.get("seat", 0) + self.tc_info.get(load_type, 0)

        total_capacity = 0
        for coach in comp_list:
            if coach == "DMC":
                total_capacity += dmc_capacity
            elif coach in {"TC", "MC"}:
                total_capacity += tc_capacity
            else:
                print(f"Warning: Unknown coach type '{coach}' in composition.")

        return total_capacity

    def compute_headways(self, train_capacity):
        headways = {}
        for year, phpdt in self.phpdt_dict.items():
            try:
                phpdt_val = float(phpdt)
                headway = round(60 * train_capacity / phpdt_val, 2) if phpdt_val > 0 else None
            except (ValueError, TypeError):
                headway = None
            headways[year] = headway
        return headways

    def compute_train_requirements(self, headways_dict):
        trains = {}

        travel_time = (self.section_length / self.avg_speed) * 60 if self.avg_speed > 0 else float('inf')
        cycle_time = 2 * (travel_time + self.reversal_time)

        for year, headway in headways_dict.items():
            if headway and headway > 0:
                trains[year] = math.ceil(cycle_time / headway)
            else:
                trains[year] = None

        return trains

    def compute_aw4_weights(self, aw4_capacity):
        num_cars = len(self.train_composition)
        avg_passenger_weight_ton = (aw4_capacity / num_cars * self.tare_dict["PassWt"]) / 1000 if num_cars > 0 else 0

        total_train_weight = 0
        axle_loads = {}

        for car in self.train_composition:
            tare_weight = self.tare_dict.get(car, 0)
            total_weight = tare_weight + avg_passenger_weight_ton
            total_train_weight += total_weight
            axle_loads[car] = round(total_weight / 4.0, 2)

        return [round(total_train_weight, 2), axle_loads]

    def compute_dpr_data(self):
        self.capacity_aw3 = self.compute_capacity('AW3')
        self.capacity_aw4 = self.compute_capacity('AW4')
        self.headway = self.compute_headways(self.capacity_aw3)
        self.train_requirement = self.compute_train_requirements(self.headway)
        self.train_weight, self.axle_loads = self.compute_aw4_weights(self.capacity_aw4)

        return self.capacity_aw3, self.capacity_aw4, self.headway, self.train_requirement, self.train_weight, self.axle_loads
