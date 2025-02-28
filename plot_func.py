# import needed libraries
import matplotlib.pyplot as plt

import matplotlib.ticker as plt_tick
from matplotlib.ticker import MaxNLocator
PX = 1/plt.rcParams['figure.dpi']  # pixel in inches
plt.rcParams["font.family"] = "Times New Roman"
FONT_SIZE = 16

import os

from helpers import np

figures_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')

def plot_wind_resource(u_vector, duration_vector, energy_vector):
    ''' 
    plot on the same chart the speed vector in the x axis and
    speed anual duration in the first y axis and the energy per area on the second y axis
    '''
    fig, ax1 = plt.subplots(figsize=(1280*PX, 720*PX))

    color = 'tab:gray'
    ax1.set_ylabel('Duration [h/year]', color=color, fontsize = FONT_SIZE)
    ax1.bar(u_vector, duration_vector, color=color, label='Duration')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel(r'Energy [kWh/$\text{m}^2$/year]', color=color, fontsize = FONT_SIZE)
    ax2.plot(u_vector, energy_vector, color=color, label='Energy')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.legend(loc='upper right', bbox_to_anchor=(0.85, 0.85))

    # chart formatting
    ax2.get_yaxis().set_major_formatter(
        plt_tick.FuncFormatter(lambda x, p: format(int(x)/1000, ',.0f')))
    
    fig.suptitle(f'Anual wind speed hours distribution and wind energy distribution', fontsize = FONT_SIZE + 2)
    ax1.set_xlabel('Wind speed [m/s]', fontsize = FONT_SIZE)

    plt.grid(alpha=0.25)
    fig.tight_layout()
    
    plt.savefig(os.path.join(figures_dir, 'wind_resource.png'))
    plt.show()


def plot_turbine_curve(u_vector, power_vector, limits):
    ''' 
    plot turbine characteristic power curve with cut-in, rated and cut-out
    '''
    cut_in, rated, cut_out = limits[0], limits[1], limits[2]
    rated_power = max(power_vector)

    fig, ax = plt.subplots(figsize=(1280*PX, 720*PX))

    # plot power curve
    color = (0, 0, 0)
    ax.plot(u_vector, power_vector, color=color, label='Turbine Power', lw='2')
    ax.tick_params(axis='y', labelcolor=color)

    # plot limits
    plt.axvline(x = cut_in, ls = ':', lw = '0.75', color = 'red', alpha = 0.5)
    plt.axvline(x = rated, ls = ':', lw = '0.75', color = 'red', alpha = 0.5)
    plt.axvline(x = cut_out, ls = ':', lw = '0.75', color = 'red', alpha = 0.5)
    plt.axhline(y = rated_power, ls = ':', lw = '0.75', color = 'red', alpha = 0.5)

    # add X values of interest
    ax = plt.gca()  # Get current axis
    xticks = ax.get_xticks()
    for limit in limits:  # Retrieve x-axis tick positions
        if limit not in xticks:
            xticks = np.append(xticks, limit)  # Append new value
            xticks = np.sort(xticks)  # Sort ticks to keep order
    
    # add Y value of interest
    ax = plt.gca()  # Get current axis
    yticks = ax.get_yticks()
    if rated_power not in yticks:
        yticks = np.append(yticks, rated_power)  # Append new value
        yticks = np.sort(yticks)  # Sort ticks to keep order

    # Set updated tick positions
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    # highlight X value
    for label in ax.get_xticklabels():
        try:
            tick_value = float(label.get_text())  # Convert label text to number
            if tick_value in limits:
                label.set_color('red')  # Change color
                label.set_fontweight('bold')  # Optional: Make it bold
        except ValueError:
            pass  # In case there are empty or non-numeric labels

    # highlight Y value
    for label in ax.get_yticklabels():
        try:
            tick_value = label._y  # Convert label text to number
            if tick_value == rated_power:
                label.set_color('red')  # Change color
                label.set_fontweight('bold')  # Optional: Make it bold
        except ValueError:
            pass  # In case there are empty or non-numeric labels

    y_width = max(power_vector) - min(power_vector)
    plt.xlim(min(u_vector), max(u_vector))
    plt.ylim(min(power_vector) - y_width/10, max(power_vector) + y_width/10)

    # add texts
    plt.text(cut_in, -y_width/20, "Cut-in Speed", fontsize=10, color="red",
         ha='left', va='center', bbox=dict(facecolor='grey', alpha=0.25))
    plt.text(rated, -y_width/20, "Rated Speed", fontsize=10, color="red",
         ha='left', va='center', bbox=dict(facecolor='grey', alpha=0.25))
    plt.text(cut_out, -y_width/20, "Cut-out Speed", fontsize=10, color="red",
         ha='left', va='center', bbox=dict(facecolor='grey', alpha=0.25))
    plt.text(0, rated_power + y_width/20, "Rated Power", fontsize=10, color="red",
         ha='left', va='center', bbox=dict(facecolor='grey', alpha=0.25), transform=plt.gca().transData)

    # chart formatting
    ax.get_yaxis().set_major_formatter(
        plt_tick.FuncFormatter(lambda x, p: format(int(x)/1000, ',.0f')))

    # axis labels
    fig.suptitle(f'Turbine power curve', fontsize = FONT_SIZE + 2)
    ax.set_xlabel('Wind speed [m/s]', fontsize = FONT_SIZE)
    ax.set_ylabel('Power [kW]', fontsize = FONT_SIZE)
    
    # layout
    plt.grid(alpha=0.25)
    fig.tight_layout()

    # export as png
    plt.savefig(os.path.join(figures_dir, 'turbine_power_curve.png'))
    plt.show()
    

def plot_turbine_energy_production(u_vector, turbine_energy_vector, wind_energy_vector):
    ''' 
    plot on the same chart the speed vector in the x axis and
    turbine anual energy production and the available wind energy
    '''
    fig, ax = plt.subplots(figsize=(1280*PX, 720*PX))

    color = (0, 0, 0)
    ax.set_ylabel('Energy [kWh/year]', color=color, fontsize = FONT_SIZE)
    ax.bar(u_vector, turbine_energy_vector, color=color, label='Turbine production')
    
    color = 'tab:brown'
    ax.plot(u_vector, wind_energy_vector, color=color, label='Available wind energy at turbine area', marker='.')

    fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.85))

    # chart formatting
    ax.get_yaxis().set_major_formatter(
        plt_tick.FuncFormatter(lambda x, p: format(int(x)/1000000, ',.0f')))
    
    fig.suptitle(f'Turbine energy production and available wind energy', fontsize = FONT_SIZE + 2)
    ax.set_xlabel('Wind speed [m/s]', fontsize = FONT_SIZE)

    plt.grid(alpha=0.25)
    fig.tight_layout()

    plt.savefig(os.path.join(figures_dir, 'energy_production.png'))
    plt.show()