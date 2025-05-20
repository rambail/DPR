import numpy as np
import pandas as pd


class MetroSimulator:
    """
    Simulates a train run: acceleration, coasting, braking (including
    deceleration for curves based on radius), and station dwell.
    Logs time, position, speed, and energy.
    """
    def __init__(self, params: dict, stations: pd.DataFrame,
                 curves: pd.DataFrame = None, gradients: pd.DataFrame = None,
                 curve_sr: pd.DataFrame = None):
        # Store input parameters and data tables
        self.params = params
        self.stations = stations.sort_values('chainage').reset_index(drop=True)
        self.curves = curves
        self.gradients = gradients
        self.curve_sr = curve_sr

        # Log the train running parameters
        self.time_log = []
        self.speed_log = []
        self.distance_log = []
        self.energy_log = []

        # Initialize simulation state
        self.distance = 0
        self.time = 0
        self.speed = 0

        # Read acceleration/braking parameters
        self.acc_rate_start = params.get('Acceleration_rate_1', 0.0)
        self.acc_rate_mid = params.get('Acceleration_rate_2', 0.0)
        self.braking_deceleration = params.get('Braking_rate', 0.0)

        # The speeds are defined in Km/hr2. Convert to m/s2
        self.max_speed_ms = params.get('Maximum_speed', 0.0) * 1000 / 3600
        self.switch_speed = params.get('Switch_speed', 0.0) * 1000 / 3600

        # Precompute distances needed to accelerate/brake
        self.accelerating_distance = self.max_speed_ms**2/2/self.acc_rate_mid
        self.braking_distance = self.max_speed_ms**2/2/self.braking_deceleration
        self.acc_rate = 0

        # Station dwell and coasting parameters
        self.stop_duration = params.get('Stop_duration',30)
        self.coasting_limit = params.get('Coasting_limit',0.5)

        # Resistance coefficients for Davis formula (A + B v + C v^2)
        self.static_friction    = params.get('Static_friction',    0.0)  # A (N/ton)
        self.rolling_resistance = params.get('Rolling_resistance', 0.0)  # B (N·s/m per ton)
        self.air_resistance     = params.get('Air_resistance',     0.0)  # C (N·s²/m² per ton)

        # Regeneration Efficiency
        self.regeneration_efficiency = params.get('Regeneration_efficiency',0.3)

        # Compute total train mass (tons)
        self.total_mass = self.calculate_train_mass()

    def calculate_train_mass(self):
        """
        Compute total train mass from composition string and per-coach masses,
        plus passenger weight if provided.
        Expects parameters:
          - Train_comp: e.g. "DTD"
          - MC_mass, TC_mass: floats in tons
          - Pass_AW4: number of passengers
          - Pass_wt: average weight per passenger (kg)
        Letter mapping:
          D → DMC (use MC_mass)
          M → MC  (use MC_mass)
          T → TC  (use TC_mass)
        """

        # Extract values
        train_comp = self.params.get('Train_comp', 0.0)
        mc_mass = float(self.params.get('MC_mass', 0.0))
        tc_mass = float(self.params.get('TC_mass', 0.0))
        pass_nos = float(self.params.get('Pass_AW4', 0.0))
        pass_wt = float(self.params.get('Pass_wt', 0.0))

        if mc_mass is None or tc_mass is None:
            raise KeyError("MC_mass and TC_mass must be present in train_parameters.csv")

        # Tare weight of Train
        total_mass = 0.0
        for letter in train_comp:
            if letter.upper() in ("D", "M"):
                total_mass += mc_mass
            elif letter.upper() == "T":
                total_mass += tc_mass
            else:
                raise ValueError(f"Unknown coach type: {letter}")

        # Include Passenger weight
        #print(f'Pass: {pass_nos}\t Weight:{pass_wt}')
        total_mass += pass_nos * pass_wt /1000
        return total_mass

    def get_speed_restriction(self):
        """
        If the train's current distance lies within any curve segment,
        return the speed restriction (m/s) for that curve's radius.
        """
        for _, row in self.curves.iterrows():
            if row['start'] <= self.distance <= row['end']:
                radius = row['radius']
                matched = self.curve_sr[self.curve_sr['radius'] == radius]
                if not matched.empty:
                    speed = matched.iloc[0]['speed']  # or 'restrict_speed'
                    #print(f"SR for radius {radius}: {speed}")
                    return speed * 1000 / 3600  # convert km/h to m/s
        return None

    def coasting_deacelerate(self, speed):
        """
        Compute deceleration due to resistive forces using Davis formula:
        R = (A + B*v + C*v^2) * mass (tons) → total N
        """
        R_per_ton = (self.static_friction +
                     self.rolling_resistance * speed +
                     self.air_resistance   * speed**2)
        return R_per_ton * self.total_mass  # N

    def accelerate(self, time_step):
        """
        Increase speed by acceleration; switch rate if above switch_speed.
        """
        self.acc_rate = self.acc_rate_start if self.speed < self.switch_speed else self.acc_rate_mid
        self.speed += self.acc_rate * time_step
        return min(self.speed, self.max_speed_ms)

    def coast(self, time_step):
        """
        Reduce speed by resistive forces while coasting.
        """
        #print(f'Speed:{speed}, Time Step:{time_step}')
        self.speed -= self.coasting_deacelerate(self.speed) / self.total_mass / 1000 * time_step
        return

    def brake(self, time_step):
        """
        Apply braking deceleration until speed reaches zero.
        """
        self.speed -= self.braking_deceleration * time_step
        return max(self.speed, 0)

    def accelerate_phase(self, segment_time, time_step):
        """
        Acceleration phase, after the train exits the station.
        """
        #print(f'')
        power = 0
        self.speed = self.accelerate(time_step)
        self.distance += self.speed * time_step
        power = self.power_consumed()
        self.log_data(power)
        segment_time += time_step
        self.time += time_step
        return  segment_time

    def coast_phase(self, local_distance, segment_time, time_step):
        """
        Once the train attains the maximum speed, Acceleration is turned coefficients.

        If the train enters a speed restricted (SR) zone, the speed reduces to SR.
        """
        # Flag to indicate when we should continue accelerating to reach max speed
        should_accelerate = False
        power = 0
        # Check if the speed has fallen below coasting limit
        if self.speed > self.coasting_limit * self.max_speed_ms and not should_accelerate:
            self.coast(time_step)
        else:
            should_accelerate = True
            self.speed = self.accelerate(time_step)
            # Stop acceleration if speed goes above maxm speed
            if self.speed >= self.max_speed_ms:
                should_accelerate = False
        # Power consumed only during acceleration
        if not should_accelerate:
            power = self.power_consumed()

        speed_limit = self.get_speed_restriction()
        if speed_limit:
            self.speed = speed_limit
        self.distance += self.speed * time_step
        self.log_data(power)
        segment_time += time_step
        self.time += time_step
        return segment_time

    def brake_phase(self, segment_time, time_step):
        """
        The train nearing a station, brakes to stop.
        """
        power = 0
        self.speed = self.brake(time_step)
        self.distance += self.speed * time_step
        power = self.power_consumed() * self.regeneration_efficiency * -1
        self.log_data(power)
        segment_time += time_step
        self.time += time_step
        return  segment_time

    def power_consumed(self):
        """
        Instantaneous power: P = F * v  where F = m * acc_rate
        Returns Watts.
        """
        force = self.total_mass * 1000 * self.acc_rate  # Force in Newtons
        power = force * self.speed  # Power in Watts
        return power

    def log_data(self, power):
        """
        Record current time, speed, distance, and energy (from power input regens).
        Speed logged in km/h.
        """
        self.time_log.append(self.time)
        self.speed_log.append(self.speed*18/5)
        self.distance_log.append(self.distance)
        self.energy_log.append(power)

    def energy_consumed_in_run(self, time_step):
        """
        Integrate power log to find total energy (kWh).
        """
        # Numerical integration of power to get energy in Joules
        energy_consumed = np.trapezoid(self.energy_log, dx=time_step)
        # Convert energy from Joules to kWh
        energy_consumed_kwh = energy_consumed / 3.6/10e5

        print(f"Total energy consumed during the run: {energy_consumed_kwh:.3f} kWh")

    def average_corridor_speed(self):
        '''
        Computes the average speed for the average_corridor_speed
        '''
        total_distance = self.stations.iloc[-1]['chainage'] - self.stations.iloc[0]['chainage']
        average_speed = total_distance / self.time
        #print(f"A total distance of {total_distance/1000:.2f} Km was covered in {self.time/60:.2f} minutes.")
        #print(f"Average speed for the trip was: {average_speed*18/5:.2f} km/hr")

        return average_speed, total_distance, self.time

    def simulate(self):
        """
        Full run simulation over all station segments.
        """
        dt = 1  # time step in seconds
        next_station_idx = 1

        # Calculate segment length
        while next_station_idx < len(self.stations):
            next_station_dist = self.stations.iloc[next_station_idx]['chainage']
            segment_distance = next_station_dist - self.distance
            local_distance = 0
            segment_time = 0

            #print(f'Start Acceleration at Time:{self.time} and Speed:{self.speed*18/5}')
            # 1) Accelerate up to max speed
            while self.speed < self.max_speed_ms:
                segment_time = self.accelerate_phase(segment_time, dt)
                local_distance += self.speed * dt
            #print(f'Start Coasting at Time:{self.time} and Speed:{self.speed*18/5}')
            # 2) Coast until braking point, enforce speed restrictions
            while local_distance < (segment_distance - self.braking_distance):
                segment_time = self.coast_phase(local_distance, segment_time, dt)
                local_distance += self.speed * dt
            #print(f'Start Braking atTime:{self.time} and Speed:{self.speed*18/5}')
            # 3) Brake to stop at station
            while self.speed > 0:
                segment_time = self.brake_phase(segment_time, dt)
                local_distance += self.speed * dt
            # 4) Dwell at station
            for _ in range(int(self.stop_duration)):
                self.time += 1
                self.log_data(0)
            # Advance to next station
            next_station_idx += 1

        # After run, compute and display total energy
        self.energy_consumed_in_run(dt)

        avg_speed, total_distance, total_time = self.average_corridor_speed()

        # Return detailed log as DataFrame
        return pd.DataFrame({
            'Time (s)':self.time_log,
            'Speed (m/s)':self.speed_log,
            'Distance':self.distance_log,
            'Energy (kJ)':self.energy_log,
            'Average Speed (km/h)': avg_speed * 18 / 5,
            'Total Distance (km)': total_distance / 1000,
            'Total Time (min)': total_time / 60
        })
