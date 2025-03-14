from helpers import *

from scipy.special import gamma

class Wind():
    '''
    class to represent wind resource object
    '''


    def __init__(self, average, height, rho, step=1):
        '''
        initialize wind object with average with speed at a given height and air density
        '''
        self.average = average
        self.height = height
        self.rho = rho
        self.step = step

        # create wind speed array
        self.speed_vector = np.arange(0, 30, self.step)


    def wind_profile(self, h, z0):
        '''
        calculate average wind speed given a height and surface roughness
        '''
        self.hub_speed = self.average * (np.log(h / z0) / np.log(self.height / z0))
    

    def weibull(self, k):
        ''' 
        create weibull probability distribution of wind speed \n
        input: weibull k factor
        '''
        # store value in object
        self.k = k

        # compute weibull 'c' parameter with gamma function
        self.c_weibull = self.hub_speed / gamma(1 + 1/k)

        # create speed probability distribution function
        self.speed_probability_vector = weibull_pdf(self.speed_vector, k, self.c_weibull)

    
    def hourly_distribution(self, hours):
        '''
        create vector with duration of each wind speed for the weibull pdf \n
        input: number of hours in the period of interest
        '''
        self.hour_distribution_vector = self.speed_probability_vector * hours

    
    def energy_density_distribution(self):
        '''
        create vector with energy for each wind speed and cumulative distribution function\n
        '''
        # wind energy probability distribution function (PDF) Wh/m2, normalized by area
        self.energy_distribution_vector = [0.5 * self.rho * (u**3) * t
                                    for (u, t) in zip(self.speed_vector, self.hour_distribution_vector)]
        
        # energy cumulative distribution function (CDF)
        self.energy_cdf_vector = cdf(self.energy_distribution_vector)
        
        # self.energy_cdf_vector = 1 - np.exp(-(self.speed_vector/self.c_weibull)**self.k)


    def rated_speed(self, rated_limit):
        '''
        compute rated speed based on the energy CDF \n
        input: rated_limit design parameters
        '''
        self.speed_rated = self.speed_vector[np.where(self.energy_cdf_vector > rated_limit)[0][1]] # interception bin + 1


    def cutout_speed(self, cutout_limit):
        '''
        compute rated and cutout speed based on the energy CDF \n
        input: cutout_limit design parameters
        '''
        self.speed_cutout = self.speed_vector[np.where(self.energy_cdf_vector > cutout_limit)[0][1]] # interception bin + 1


    def wind_power_distribution(self, swept_area):
        '''
        create vector of WIND power for each velocity given its probability
        '''
        self.power_distribution_vector = 0.5 * self.rho * swept_area * (self.speed_vector ** 3) * self.speed_probability_vector


class Turbine():
    ''' 
    class to represent the turbine object
    '''

    def __init__(self, speed_vector, diameter, height, cp, global_efficiency, down_time, rho):
        ''' 
        initiate object with diameter and hight of the turbine
        '''
        self.speed_vector = speed_vector
        self.diameter = diameter
        self.height = height
        self.cp = cp
        self.global_efficiency = global_efficiency
        self.down_time = down_time
        self.rho = rho

        self.area = np.pi * (self.diameter / 2) ** 2

    
    def turbine_power_distribution(self, wind_power):
        '''
        create vector of WIND power for each velocity given its probability and turbine characteristics
        '''
        self.power_distribution_vector = wind_power * self.cp * self.global_efficiency


    def calculate_rated_power(self, rated_speed):
        # calculate rated power
        self.rated_power = 0.5 * self.rho * self.area * (rated_speed ** 3) * self.cp * self.global_efficiency


    def cutin_speed(self, cutin_limit):
        '''
        compute cutin speed based on the turbine power distribution \n
        input: cutin_limit design parameters
        '''
        self.speed_cutin = (2 * cutin_limit * self.rated_power / (self.rho * self.area * self.cp * self.global_efficiency)) ** (1/3)


    def power_curve(self, speed_cutout, speed_rated):
        '''
        calculate WEC power curve with cut_in, rated_power and cut_out
        input: cut_out and rated_power 
        '''
        self.power_curve_vector = 0.5 * self.rho * self.area * (self.speed_vector ** 3) * self.cp * self.global_efficiency

        # store wind speed cutout at turbine object
        self.speed_cutout = speed_cutout
        self.speed_rated = speed_rated

        # get indexes
        cut_in_index = np.where(self.speed_vector < self.speed_cutin)
        # rated_index = np.where(self.speed_vector >= self.speed_rated)
        rated_index = np.where(self.power_curve_vector >= self.rated_power)
        cut_out_index = np.where(self.speed_vector >= self.speed_cutout)

        # set values for turbine power curve
        self.power_curve_vector[cut_in_index] = 0
        self.power_curve_vector[rated_index] = self.rated_power
        self.power_curve_vector[cut_out_index] = 0


    def hourly_distribution_downtime(self, hourly_distribution):
        '''
        include turbine downtime at wind speed hourly distribution
        '''
        self.hourly_distribution_vector = hourly_distribution
        self.hourly_distribution_downtime_vector = hourly_distribution * (1 - self.down_time)


    def energy(self):
        '''
        calculate turbine energy production at each wind speed
        '''
        self.energy_vector = [p * t for p, t in zip(self.power_curve_vector, self.hourly_distribution_downtime_vector)]
        self.energy_production = sum(self.energy_vector)


    def average_power(self):
        '''
        calculate average power for each wind speed
        '''
        self.average_power_vector = [e / t if t != 0 else 0 for (e, t) in zip(self.energy_vector, self.hourly_distribution_vector)]
        self.average_power_value = self.energy_production / sum(self.hourly_distribution_vector)


    def full_load_hours(self):
        '''
        calculate full load hours for each wind speed
        '''
        self.full_load_hours_vector = [e / self.rated_power for e in self.energy_vector]
