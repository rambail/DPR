## plotter.py
import matplotlib.pyplot as plt

class Plotter:
    """
    Plots and saves the speed-time profile (and optional energy) from simulation logs.
    """
    def __init__(self, figsize=(10, 6)):
        self.figsize = figsize

    def plot(self, df, speed_path, energy_path=None):
        plt.figure(figsize=self.figsize)
        plt.plot(df['Time (s)'], df['Speed (m/s)'], label='Speed (m/s)')
        plt.xlabel('Time (s)')
        plt.ylabel('Speed (m/s)')
        plt.title('Speed Profile')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(speed_path)
        plt.close()

        if energy_path:
            plt.figure(figsize=self.figsize)
            plt.plot(df['Time (s)'], df['Energy (kJ)'], label='Energy (J)')
            plt.xlabel('Time (s)')
            plt.ylabel('Energy (J)')
            plt.title('Energy Consumption')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.savefig(energy_path)
            plt.close()
