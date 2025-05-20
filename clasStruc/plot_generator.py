import matplotlib.pyplot as plt

class TransitPlotGenerator:
    """
    Generates a normalized line plot comparing ridership, PHPDT, headway,
    and number of trains across forecast years, and saves the image to disk.
    """

    def __init__(self, years, ridership, phpdt, headway, train_number, image_filename):
        self.years = years
        self.ridership = ridership
        self.phpdt = phpdt
        self.headway = headway
        self.train_number = train_number
        self.image_filename = image_filename

    def _get_series(self, data):
        values = []
        for year in self.years:
            val = data.get(year, 0)
            if not isinstance(val, (int, float)):
                try:
                    val = int(val)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid value '{val}' for year {year}.") from e
            values.append(val)
        return values

    def _normalize(self, series):
        factor = max(abs(x) for x in series) or 1
        return [x / factor for x in series], factor

    def generate_plot(self):
        ridership_vals = self._get_series(self.ridership)
        phpdt_vals = self._get_series(self.phpdt)
        headway_vals = self._get_series(self.headway)
        train_vals = self._get_series(self.train_number)

        ridership_norm, r_factor = self._normalize(ridership_vals)
        phpdt_norm, p_factor = self._normalize(phpdt_vals)
        headway_norm, h_factor = self._normalize(headway_vals)
        train_norm, t_factor = self._normalize(train_vals)

        plt.figure(figsize=(10, 6))
        plt.plot(self.years, ridership_norm, marker='o', label=f"Ridership (×{r_factor:.2f})")
        plt.plot(self.years, phpdt_norm, marker='s', label=f"PHPDT (×{p_factor:.2f})")
        plt.plot(self.years, headway_norm, marker='^', label=f"Headway (×{h_factor:.2f})")
        plt.plot(self.years, train_norm, marker='d', label=f"Train Number (×{t_factor:.2f})")

        plt.xlabel("Year")
        plt.ylabel("Normalized Value")
        plt.title("Normalized Transit Data Over Years")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.image_filename)
        plt.close()
