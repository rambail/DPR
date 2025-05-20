import math

class EnergyRequirement:
    def __init__(self, power_params, working_hours):
        """
        power_params: dict containing keys like 'SEC', 'Regen', 'DepotTP', 'TrLoss', 'TrPF',
                     'ElStnPwr', 'ElStnNos', 'UGStnPwr', 'UGStnNos', 'DpPwr', 'DpNos',
                     'AuxLoss', 'AuxPF'
        working_hours: dict with keys 'Hours' and 'Days'
        diversity_factor: float (e.g. 0.85 for 85%)
        """
        self.power = power_params
        self.working_hours = working_hours
        self.diversity_factor = power_params.get("DF", {})

    def compute_traction_energy(self, yearly_headways, section_length, train_weight_aw4):
        energy_raw = {}
        energy_regen_eff = {}

        # kWh per trip
        energy_per_trip = self.power['SEC'] * train_weight_aw4 * section_length / 1e6

        for year, headway in yearly_headways.items():
            train_nos = 60 * 2 / headway
            energy_raw[year] = round(energy_per_trip * train_nos, 2)

        for year, val in energy_raw.items():
            energy_wo_regen = val
            energy_with_depot = energy_wo_regen * (1 - self.power['Regen']/100) + self.power['DepotTP']
            final_energy = energy_with_depot / (1 - self.power['TrLoss']/100) / self.power['TrPF']
            energy_regen_eff[year] = round(final_energy, 2)

        return [energy_raw, energy_regen_eff]

    def compute_auxiliary_energy(self, years):
        energy_raw = {}
        energy_regen_eff = {}

        for year in years:
            aux_energy_kw = (
                self.power['ElStnPwr'] * self.power['ElStnNos'] +
                self.power['UGStnPwr'] * self.power['UGStnNos'] +
                self.power['DpPwr'] * self.power['DpNos']
            )
            aux_energy_mw = aux_energy_kw / 1000
            energy_raw[year] = round(aux_energy_mw, 2)
            eff_energy = aux_energy_kw / (1 - self.power['AuxLoss']/100) / self.power['AuxPF'] / 1000
            energy_regen_eff[year] = round(eff_energy, 2)

        return [energy_raw, energy_regen_eff]

    def compute_total_energy(self, traction_mw, auxiliary_mw, years):
        total_units = {}
        max_demand = {}

        for year in years:
            total_power = traction_mw[year] + auxiliary_mw[year]
            max_demand[year] = math.ceil(total_power)

            tr_units = traction_mw[year] * self.working_hours['Hours'] * self.working_hours['Days'] / 1000
            aux_units = auxiliary_mw[year] * self.working_hours['Hours'] * self.working_hours['Days'] * self.diversity_factor / 1000

            total_units[year] = round(tr_units + aux_units, 2)

        return [total_units, max_demand]
