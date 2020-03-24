"""
Python script for logging Inkubio kiltis' climate data.

The kiltis is equipped with Vaisala GMW90 air quality meter, which can measure
temperature, co2 concentration and humidity. The device is accessed with serial
service connection.
"""

import time
import datetime
import serial

def setup():
    """
    Set GMW90 to a state where climate data can be read reliably.
    """
    ser = serial.Serial('/dev/ttyUSB0', timeout=5)
    ser.baudrate = 19200

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    time.sleep(1)

    ser.write(b'\r')
    time.sleep(1)

    while ser.in_waiting:
        ser.readline()

    time.sleep(1)
    ser.reset_output_buffer()

    ser.write(b'reset\r')
    # Waiting for gmw90 to reboot
    time.sleep(5)
    # Removing messages sent by gmw90 after reset command from buffer
    while ser.in_waiting:
        ser.readline()

    # A hack to fix data misaligned due to missing '>' in first measurement
    ser.write(b'send\r')
    ser.readline()
    time.sleep(1)
    return ser

def read_measurement(ser):
    """
    Get measurement from GMW90.

    Parameters:
        ser: serial connection object connected to GMW90
    Returns:
        String containing measurement data from GMW90. Example string:
        >T=22.34 'C  CO2=1343 ppm  RH=34.26 %RH
    """

    ser.write(b'send\r')
    line = ser.readline()
    return line

def temperature_str(meas):
    """ Pick temperature characters from measurement line."""
    ret = 'Temp: {}C'.format(meas[3:8].decode())
    return ret

def temperature_num(meas):
    """ Pick temperature as number from measurement line."""
    ret = '{}'.format(meas[3:8].decode())
    return float(ret)

def co2_str(meas):
    """ Pick CO2 concentration characters from measurement line."""
    ret = 'CO2: {}ppm'.format(meas[17:21].decode())
    return ret

def co2_num(meas):
    """ Pick temperature as number from measurement line."""
    ret = '{}'.format(meas[17:21].decode())
    return int(ret)

def humidity_str(meas):
    """ Pick relative humidity characters from measurement line."""
    ret = 'Humidity: {}%'.format(meas[30:35].decode())
    return ret

def humidity_num(meas):
    """ Pick relative humidity as number from measurement line."""
    ret = '{}'.format(meas[30:35].decode())
    return float(ret)

def save_data(data):
    """ Save aquired data on disk.

    Parameters:
        data: string containing data row to write in csv format"""
    now = datetime.datetime.now()
    with open('./data/{}-{}.csv'.format(now.year, now.month), 'a') as f:
        for item in data:
            f.write('{}\n'.format(item))

def log(ser):
    """ Infinite loop to log air quality data on disk.
    
    Takes a measurement every minute and writes them on disk after 10
    measurements.

    Parameters:
        ser: Serial connection object connected to GMW90.
    """
    data = []
    while True:
        line = read_measurement(ser)
        unixtime = int(time.time())
        try:
            temp = temperature_num(line)
            co2 = co2_num(line)
            hum = humidity_num(line)
            data.append('{}, {}, {}, {}'.format(unixtime, temp, co2, hum))

            with open('newest', 'w') as f_newest:
                f_newest.write('{}\n'.format(temp))
                f_newest.write('{}\n'.format(co2))
                f_newest.write('{}\n'.format(hum))
                f_newest.write('{}\n'.format(datetime.datetime.now()))

        except ValueError:
            now = datetime.datetime.now()
            time_str = now.strftime('%Y-%m-%d %H:%M:%S')
            with open('./data/log.txt', 'a') as logfile:
                logfile.write('{}: Unexpected response from gmw90: {}\n'.format(time_str, line))

        if len(data) > 9:
            save_data(data)
            data.clear()
        time.sleep(60)

def main():
    """
    Set up connection to the meter and log until eternity.
    """
    ser = setup()
    log(ser)

main()
