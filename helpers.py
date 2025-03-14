# import needed libraries
import numpy as np

def weibull_pdf(u_vector, k, c):
    '''
    calculate weibull probability of wind speed VECTOR 'u_vector'
    with 'k' and 'c' parameters
    '''
    return (k/c) * ((u_vector/c) ** (k-1)) * np.exp(-(u_vector/c) ** k)


def weibull_cdf(u_vector, k, c):
    '''
    calculate weibull cumulative distribution function of wind speed VECTOR 'u_vector'
    with 'k' and 'c' parameters
    '''
    return 1 - np.exp(-(u_vector/c) ** k)


def cdf(u_vector):
    '''
    calculate cummulative distribution function of the u_vector and returns a vector
    '''
    return np.array([sum(u_vector[:x+1]) / sum(u_vector) 
            for x in range(0, len(u_vector))])