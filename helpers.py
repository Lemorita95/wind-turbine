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


