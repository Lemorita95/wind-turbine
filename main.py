from turbine import *
from plot_func import *

import json
json_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'project.json')

# Load JSON file
with open(json_file, "r") as file:
    data = json.load(file)

# Convert values to float where possible
for key, value in data.items():
    try:
        data[key] = float(value)  # Convert to float if possible
    except (ValueError, TypeError):
        pass  # Ignore if conversion is not possible

# project parameters
K_FACTOR = data["k_factor"]
AVG_U_SPEED = data["avg_u_speed"] # m/s @ 10m
AVG_U_HEIGHT = data["avg_u_height"] # meters
Z0 = data["z0"]/1000 # meters
DOWN_TIME_PERCENTAGE = data["down_time"]/100
TURBINE_DIAMETER = data["turbine_diameter"] # meters
HUB_HEIGHT = data["hub_height"] # meters
CP = data["cp"]
DT_EFFICIENCY = data["dt_efficiency"]

# project considerations
WIND_STEP = 1
CUTIN_LIMIT = 1/100
RATED_LIMIT = 1/3
CUTOUT_LIMIT = 8/10

# project boundary conditions
SIGMA_ALLOWED = 160*(10**6) # Pascal (160 MPa)
TOWER_DIAMETER = HUB_HEIGHT/20 # meters
NACELLE_WEIGHT_POWER = 40 # kg/kW
SOLIDITY = 0.03
CD = 1.5 # drag coefficient
CT = 8/9 # thrust coefficient

# general parameters
YEAR_HOURS = 365.25 * 24 # hours
RHO = 1.225 # kg/m3
GRAVITY = 9.81 # m/s2
STEEL_DENSITY = 7850 # kg/m3


''' 1) Wind Resources '''
# create wind object
wind = Wind(AVG_U_SPEED, AVG_U_HEIGHT, RHO, WIND_STEP)
# compute wind speed at hub height
wind.wind_profile(HUB_HEIGHT, Z0)
# compute weibull probability distribution function
wind.weibull(K_FACTOR)
# create annual distribution of hours at each wind speed
wind.hourly_distribution(YEAR_HOURS)
# create energy density distribution and its cdf
wind.energy_density_distribution()
# compute rated and cutout speed
wind.rated_speed(RATED_LIMIT)
wind.cutout_speed(CUTOUT_LIMIT)

# plot speed time and energy distribution
plot_wind_resource(wind.speed_vector, wind.hour_distribution_vector, wind.energy_distribution_vector)
plot_wind_cdf(wind.speed_vector, wind.energy_cdf_vector, [RATED_LIMIT, CUTOUT_LIMIT])


''' 2) Wind Energy Converter '''
# create turbine object
turbine = Turbine(wind.speed_vector, TURBINE_DIAMETER, HUB_HEIGHT, CP, DT_EFFICIENCY, DOWN_TIME_PERCENTAGE, RHO)
# compute wind power
wind.wind_power_distribution(turbine.area)
# compute turbine rated power
turbine.calculate_rated_power(wind.speed_rated)
# compute turbine power
turbine.turbine_power_distribution(wind.power_distribution_vector)
# calculate turbine cut in speed
turbine.cutin_speed(CUTIN_LIMIT)
# calculate turbine power curve
turbine.power_curve(wind.speed_cutout, wind.speed_rated)

power_curve_limits = [turbine.speed_cutin, turbine.speed_rated, turbine.speed_cutout]

print(f'\nTurbine rated power: {turbine.rated_power/1000:.2f} kW')
print(f'Cut-in speed: {turbine.speed_cutin:.1f} m/s, Rated speed: {turbine.speed_rated} m/s, Cut-out speed: {turbine.speed_cutout} m/s\n')
plot_turbine_curve(turbine.speed_vector, turbine.power_curve_vector, power_curve_limits)


'''  3) Energy production for one year  '''
# create downtime array
turbine.hourly_distribution_downtime(wind.hour_distribution_vector)

# compute values
turbine.energy()
turbine.average_power()
turbine.full_load_hours()

# 1 - total energy
print(f'One year energy production: {turbine.energy_production/1000000:.2f} MWh')
# plt.bar(turbine.speed_vector, turbine.energy_vector)
# plt.show()

# # 2 - average power
# plt.bar(turbine.speed_vector, turbine.average_power_vector)
# plt.show()

# # 3 - full load hours
# plt.bar(turbine.speed_vector, turbine.full_load_hours_vector)
# plt.show()

# available wind energy at turbine area
available_wind_energy_vector = np.array(wind.energy_distribution_vector) * turbine.area
# available_wind_energy_value = available_wind_energy_vector[turbine.speed_rated] / wind.hour_distribution_vector[turbine.speed_rated]

plot_turbine_energy_production(turbine.speed_vector, turbine.energy_vector, available_wind_energy_vector)

'''  4) Mechanics  '''
# check IEC 61400-1 for 4.c)

# a) gravity load on base of tower from nacelle and tower weight
nacelle_weight = (NACELLE_WEIGHT_POWER * turbine.rated_power/1000)*1
thickness_gravity_load = (1/(2*np.pi*TOWER_DIAMETER/2))*(nacelle_weight*GRAVITY/(SIGMA_ALLOWED-turbine.height*STEEL_DENSITY*GRAVITY))

# b) wind load on turbine at rated power
force_aerodynamic = 0.5 * CT * wind.rho * turbine.area * (turbine.speed_rated ** 2)
bending_moment_aerodynamic = force_aerodynamic * turbine.height
thickness_aerodynamic = bending_moment_aerodynamic / (SIGMA_ALLOWED * np.pi * (TOWER_DIAMETER/2)**2)
thickness_aerodynamic *= 2

# c) extreme wind load on tower from turbine and tower for an IEC class II turbine (60 m/s)
force_extreme_wind = 0.5 * CD * wind.rho * SOLIDITY * turbine.area * (60 ** 2)
bending_moment_extreme_wind = force_extreme_wind * turbine.height
thickness_extreme_wind = bending_moment_extreme_wind / (SIGMA_ALLOWED * np.pi * (TOWER_DIAMETER/2)**2)
thickness_extreme_wind *= 2

with open('report.txt', mode='w') as file:

    # prepare for printing
    file.write('\n')
    file.write("> Turbine Design:\n")
    file.write('\n')
    file.write(f'\nAverage speed at hub height: {wind.hub_speed:.2f} m/s')
    file.write('\n')
    file.write(f'\nTurbine rated power: {turbine.rated_power/1000:.2f} kW')
    file.write(f'\nCut-in speed: {turbine.speed_cutin:.1f} m/s, Rated speed: {turbine.speed_rated} m/s, Cut-out speed: {turbine.speed_cutout} m/s')
    file.write('\n')
    file.write(f'\nOne year energy production: {turbine.energy_production/1000000:.2f} MWh')
    file.write('\n')
    file.write(f'\nFull-load hours: {sum(turbine.full_load_hours_vector):.2f} Hours')
    file.write('\n')
    file.write(f'\nTurbine average power: {turbine.average_power_value/1000:.2f} kW')
    # file.write('\n')
    # file.write(f'\nWind average power: {available_wind_energy_value/1000:.2f} kW')
    file.write('\n')
    file.write(f'\nTower thickness due to gravity load: {thickness_gravity_load*1000:.2f} mm')
    file.write(f'\nTower thickness due to aerodinamic load: {thickness_aerodynamic*1000:.2f} mm')
    file.write(f'\nTower thickness due to extreme wind load: {thickness_extreme_wind*1000:.2f} mm')


