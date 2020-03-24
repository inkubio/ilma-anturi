'''Simple script for plotting climate sensor data.'''

import glob
import os.path

import pandas as pd
import matplotlib.pyplot as plt

# Set here the desired time range
t_start = '2019-11-01 00:00:00'
t_end = '2019-12-01 00:00:00'

# Register datetime converter to ensure correct plotting by matplotlib
pd.plotting.register_matplotlib_converters()

# Find paths to all .csv-files in ./data -folder
csv_file_paths = glob.glob(os.path.join('data', '*.csv'))

# Combine all csv files to a single data frames
data_files = []
for month_file in csv_file_paths:
    df = pd.read_csv(
        month_file,
        names=(
            'unixtime',
            'temperature',
            'co2',
            'humidity'
        )
    )
    data_files.append(df)
data = pd.concat(data_files, ignore_index=True)

# Add human-readable timestamps
data['time'] = pd.to_datetime(data['unixtime'], unit='s')

# Filter data by selection
data = data[(data.time >= t_start) & (data.time <= t_end)]

# Plot data and show results
ax = plt.subplot(3, 1, 1,)
plt.scatter(x=data.time, y=data.co2, s=2)
plt.ylabel('CO2 (ppm)')

plt.subplot(3, 1, 2, sharex=ax)
plt.scatter(x=data.time, y=data.temperature, s=2)
plt.ylabel('Temperature (°C)')

plt.subplot(3, 1, 3, sharex=ax)
plt.scatter(x=data.time, y=data.humidity, s=2)
plt.ylabel('Relative Humidity (RH%)')

plt.show()
