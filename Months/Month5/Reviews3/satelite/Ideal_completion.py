# ideal_completion.py

import numpy as np
import matplotlib.pyplot as plt
from sgp4.api import Satrec, jday
import geomag
from datetime import datetime, timedelta

# Constants and initial conditions
moment_inertia_x = 0.03673257292
moment_inertia_y = 0.03673257292
moment_inertia_z = 0.005833333333
initial_omega_x = 0.12
initial_omega_y = 0.1
initial_omega_z = 0.05
max_moment_x = 0.8
max_moment_y = 0.8
max_moment_z = 0.2
time_step_omega = 0.010
time_step_magnetic = 0.001
simulation_duration = 20000
prop_gain = 0.0002695
deriv_gain = 0.0022
integ_gain = 0

# Thresholds and intervals for each axis
omega_change_threshold_x = 0.0001
omega_change_threshold_y = 0.0002
omega_change_threshold_z = 0.00015
activation_interval_x = 10 * time_step_omega
activation_interval_y = 15 * time_step_omega
activation_interval_z = 12 * time_step_omega

# Define the range for the zero-response region for mx, my, and mz (in seconds)
zero_response_x = (0, 0)
zero_response_y = (0, 0)
zero_response_z = (0, 0)

# Operational limits for magnetic moments
NEGATIVE_MAX_X = -max_moment_x
NEGATIVE_MIN_X = -max_moment_x / 2
POSITIVE_MIN_X = max_moment_x / 2
POSITIVE_MAX_X = max_moment_x
NEGATIVE_MAX_Z = -max_moment_z
NEGATIVE_MIN_Z = -max_moment_z / 2
POSITIVE_MIN_Z = max_moment_z / 2
POSITIVE_MAX_Z = max_moment_z

# Geomagnetic model initialization
magnetic_model = geomag.geomag.GeoMag()

# Satellite parameters from TLE
sat_object = Satrec.twoline2rv(
    "1 25544U 98067A   20334.68915930  .00001264  00000-0  32282-4 0  9993",
    "2 25544  51.6457  84.5687 0002347  88.8982  34.8296 15.48815347254155"
)

def compute_magnetic_field(time, sat_obj, year_dec):
    jd, fr = jday(int(year_dec), 1, 0, 0, 0, 0)
    jd += time / (24 * 3600)  # Convert seconds to days
    error, radius, velocity = sat_obj.sgp4(jd, fr)
    if error != 0:
        raise RuntimeError("SGP4 error: " + str(error))

    latitude = np.degrees(np.arctan2(radius[2], np.sqrt(radius[0] ** 2 + radius[1] ** 2)))
    longitude = np.degrees(np.arctan2(radius[1], radius[0]))
    altitude_km = np.sqrt(radius[0] ** 2 + radius[1] ** 2 + radius[2] ** 2) - 6371.0

    # Correctly convert the time to a date object
    current_date = (datetime(year_dec, 1, 1) + timedelta(seconds=time)).date()
    
    # Pass the correct type to the GeoMag function (a date object, not datetime)
    magnetic_data = magnetic_model.GeoMag(latitude, longitude, altitude_km, current_date)

    field_x = magnetic_data.bx * 1e-9
    field_y = magnetic_data.by * 1e-9
    field_z = magnetic_data.bz * 1e-9

    return np.array([field_x, field_y, field_z])


def limit_magnetic_moment(mgn_moment, is_m_z=False):
    if is_m_z:
        if NEGATIVE_MAX_Z <= mgn_moment <= NEGATIVE_MIN_Z:
            return mgn_moment
        elif POSITIVE_MIN_Z <= mgn_moment <= POSITIVE_MAX_Z:
            return mgn_moment
        elif mgn_moment < NEGATIVE_MIN_Z:
            return NEGATIVE_MIN_Z
        elif mgn_moment > POSITIVE_MAX_Z:
            return POSITIVE_MAX_Z
        else:
            return NEGATIVE_MIN_Z if mgn_moment < 0 else POSITIVE_MIN_Z
    else:
        if NEGATIVE_MAX_X <= mgn_moment <= NEGATIVE_MIN_X:
            return mgn_moment
        elif POSITIVE_MIN_X <= mgn_moment <= POSITIVE_MAX_X:
            return mgn_moment
        elif mgn_moment < NEGATIVE_MIN_X:
            return NEGATIVE_MIN_X
        elif mgn_moment > POSITIVE_MAX_X:
            return POSITIVE_MAX_X
        else:
            return NEGATIVE_MIN_X if mgn_moment < 0 else POSITIVE_MIN_X

# Initial angular velocity variables
omega_x = initial_omega_x
omega_y = initial_omega_y
omega_z = initial_omega_z

# PID error term initialization
integral_err_x = 0
integral_err_y = 0
integral_err_z = 0
last_error_x = -initial_omega_x
last_error_y = -initial_omega_y
last_error_z = -initial_omega_z

# Record results for plotting
omega_x_record = []
omega_y_record = []
omega_z_record = []
x_axis_stopped = None
y_axis_stopped = None
z_axis_stopped = None

# Conversion constant from rad/s to deg/s
radians_to_degrees = 180 / np.pi

# Enhanced PID controller with zero-response feature
def pd_controller(error_x, error_y, error_z, last_error_x, last_error_y, last_error_z,
                  integral_err_x, integral_err_y, integral_err_z, time_intvl, curr_time):
    control_moment_x = prop_gain * error_x + integ_gain * integral_err_x + deriv_gain * (error_x - last_error_x) / time_intvl
    control_moment_y = prop_gain * error_y + integ_gain * integral_err_y + deriv_gain * (error_y - last_error_y) / time_intvl
    control_moment_z = prop_gain * error_z + integ_gain * integral_err_z + deriv_gain * (error_z - last_error_z) / time_intvl

    control_moment_x = limit_magnetic_moment(control_moment_x)
    control_moment_y = limit_magnetic_moment(control_moment_y)
    control_moment_z = limit_magnetic_moment(control_moment_z, is_m_z=True)

    if zero_response_x[0] <= curr_time <= zero_response_x[1]:
        control_moment_x = 0
    if zero_response_y[0] <= curr_time <= zero_response_y[1]:
        control_moment_y = 0
    if zero_response_z[0] <= curr_time <= zero_response_z[1]:
        control_moment_z = 0

    return control_moment_x, control_moment_y, control_moment_z, integral_err_x, integral_err_y, integral_err_z

# Arrays for storing time data
simulation_time = np.arange(0, simulation_duration, time_step_omega)
magnetic_update_time = np.arange(0, simulation_duration, time_step_magnetic)

# Variables for magnetic field updates
magnetic_time = 0

# Variables to monitor rates of change
last_omega_x = omega_x
last_omega_y = omega_y
last_omega_z = omega_z

# Threshold and time interval parameters
omega_change_threshold = 0.0001
activation_interval = 10 * time_step_omega

# Axis-specific counters
x_threshold_time = 0
y_threshold_time = 0
z_threshold_time = 0

prev_time_x_axis = simulation_time[0]
prev_time_y_axis = simulation_time[0]
prev_time_z_axis = simulation_time[0]

# Checks for constant behavior on individual axes
def detect_flat_behavior(curr_time, delta_omega, prev_time, threshold_time, axis_label):
    if delta_omega <= omega_change_threshold:
        threshold_time += (curr_time - prev_time)

        if threshold_time >= activation_interval:
            global NEGATIVE_MAX_X, NEGATIVE_MIN_X, POSITIVE_MIN_X, POSITIVE_MAX_X
            global NEGATIVE_MAX_Z, NEGATIVE_MIN_Z, POSITIVE_MIN_Z, POSITIVE_MAX_Z

            if axis_label == 'x':
                NEGATIVE_MAX_X = -0.6
                NEGATIVE_MIN_X = -0.4
                POSITIVE_MIN_X = 0.4
                POSITIVE_MAX_X = 0.6
                print(f"New operating range for X axis at time: {curr_time:.2f} s")

            elif axis_label == 'y':
                NEGATIVE_MAX_X = -0.6
                NEGATIVE_MIN_X = -0.4
                POSITIVE_MIN_X = 0.4
                POSITIVE_MAX_X = 0.6
                print(f"New operating range for Y axis at time: {curr_time:.2f} s")

            elif axis_label == 'z':
                NEGATIVE_MAX_Z = -0.2
                NEGATIVE_MIN_Z = -0.1
                POSITIVE_MIN_Z = 0.1
                POSITIVE_MAX_Z = 0.2
                print(f"New operating range for Z axis at time: {curr_time:.2f} s")
    else:
        threshold_time = 0

    return threshold_time