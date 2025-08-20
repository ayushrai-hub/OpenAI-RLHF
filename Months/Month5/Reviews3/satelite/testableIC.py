import numpy as np
import geomag
from sgp4.api import Satrec, jday
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

# Unique thresholds and activation intervals for each axis
omega_change_threshold_x = 0.0001
omega_change_threshold_y = 0.0001
omega_change_threshold_z = 0.0001

activation_interval_x = 10 * time_step_omega
activation_interval_y = 10 * time_step_omega
activation_interval_z = 10 * time_step_omega

# Operational limits for magnetic moments in mx and my
NEGATIVE_MAX_X = -max_moment_x
NEGATIVE_MIN_X = -max_moment_x / 2
POSITIVE_MIN_X = max_moment_x / 2
POSITIVE_MAX_X = max_moment_x

# Operational constraints for magnetic moments in mz
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

# Function for calculating magnetic field based on satellite's position
def compute_magnetic_field(time, sat_obj, year_dec):
    jd, fr = jday(int(year_dec), 1, 0, 0, 0, 0)
    jd += time / (24 * 3600)

    error, radius, velocity = sat_obj.sgp4(jd, fr)
    if error != 0:
        raise RuntimeError("SGP4 error: " + str(error))

    latitude = np.degrees(np.arctan2(radius[2], np.sqrt(radius[0] ** 2 + radius[1] ** 2)))
    longitude = np.degrees(np.arctan2(radius[1], radius[0]))
    altitude_km = np.sqrt(radius[0] ** 2 + radius[1] ** 2 + radius[2] ** 2) - 6371.0

    current_date = datetime(2024, 1, 1) + timedelta(seconds=time)
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

# PD controller
def pd_controller(error_x, error_y, error_z, last_error_x, last_error_y, last_error_z,
                  integral_err_x, integral_err_y, integral_err_z, time_intvl):
    control_moment_x = prop_gain * error_x + integ_gain * integral_err_x + deriv_gain * (error_x - last_error_x) / time_intvl
    control_moment_y = prop_gain * error_y + integ_gain * integral_err_y + deriv_gain * (error_y - last_error_y) / time_intvl
    control_moment_z = prop_gain * error_z + integ_gain * integral_err_z + deriv_gain * (error_z - last_error_z) / time_intvl

    control_moment_x = limit_magnetic_moment(control_moment_x)
    control_moment_y = limit_magnetic_moment(control_moment_y)
    control_moment_z = limit_magnetic_moment(control_moment_z, is_m_z=True)

    return control_moment_x, control_moment_y, control_moment_z, integral_err_x, integral_err_y, integral_err_z

# Checks for constant behavior on individual axes
def detect_flat_behavior(curr_time, delta_omega, prev_time, threshold_time, axis_label, omega_change_threshold, activation_interval):
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
