import fastf1 as ff1
from fastf1 import plotting

import pandas as pd

from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import cm

import numpy as np

import os

if not os.path.exists('cache'):
    os.makedirs('cache')

ff1.Cache.enable_cache('cache/')


ff1.Cache.enable_cache('cache/') 
pd.options.mode.chained_assignment = None

race = ff1.get_session(2023, 'Singapore', 'R')
race.load() 
laps = race.laps

laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

laps = laps.loc[(laps['PitOutTime'].isnull() & laps['PitInTime'].isnull())]

q75, q25 = laps['LapTimeSeconds'].quantile(0.75), laps['LapTimeSeconds'].quantile(0.25)

intr_qr = q75 - q25

laptime_max = q75 + (1.5 * intr_qr) 
laptime_min = q25 - (1.5 * intr_qr) 

laps.loc[laps['LapTimeSeconds'] < laptime_min, 'LapTimeSeconds'] = np.nan
laps.loc[laps['LapTimeSeconds'] > laptime_max, 'LapTimeSeconds'] = np.nan

drivers_to_visualize = ['VER', 'SAI', 'HAM', 'NOR']

visualized_teams = []

plt.rcParams['figure.figsize'] = [10, 10]

fig, ax = plt.subplots(2)

laptimes = [laps.pick_driver(x)['LapTimeSeconds'].dropna() for x in drivers_to_visualize] 

ax[0].boxplot(laptimes, labels=drivers_to_visualize)

ax[0].set_title('Average racepace comparison')
ax[0].set(ylabel = 'Laptime (s)')

for driver in drivers_to_visualize:
    driver_laps = laps.pick_driver(driver)[['LapNumber', 'LapTimeSeconds', 'Team']]
    
    driver_laps = driver_laps.dropna()
    
    team = pd.unique(driver_laps['Team'])[0]
    
    x = driver_laps['LapNumber']
    
    poly = np.polyfit(driver_laps['LapNumber'], driver_laps['LapTimeSeconds'], 5)
    y_poly = np.poly1d(poly)(driver_laps['LapNumber'])
    
    linestyle = '-' if team not in visualized_teams else ':'
    
    ax[1].plot(x, y_poly, label=driver, color=ff1.plotting.team_color(team), linestyle=linestyle)
  
    ax[1].set(ylabel = 'Laptime (s)')
    ax[1].set(xlabel = 'Lap')
    
    ax[1].set_title('Smoothed lap-by-lap racepace')

    ax[1].legend()
    visualized_teams.append(team)
    
    plt.savefig('racepace_comparison.png', dpi=300)