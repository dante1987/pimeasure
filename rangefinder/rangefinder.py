from adafruit.Adafruit_ADS1x15 import ADS1x15


# converter parameters
# GAIN = 6144  # +/- 6.144V
GAIN = 4096  # +/- 4.096V
# GAIN = 2048  # +/- 2.048V
# GAIN = 1024  # +/- 1.024V
# GAIN = 512   # +/- 0.512V
# GAIN = 256   # +/- 0.256V

# SPS = 8    # 8 samples per second
# SPS = 16   # 16 samples per second
# SPS = 32   # 32 samples per second
# SPS = 64   # 64 samples per second
# SPS = 128  # 128 samples per second
SPS = 250  # 250 samples per second
# SPS = 475  # 475 samples per second
# SPS = 860  # 860 samples per second

# The converter type (12 bit version)
ADS1015 = 0x00

ADDRESS_1 = 0x48
ADDRESS_2 = 0x49

# sensor properties
RANGEFINDER_NO_DEVICE = 8.174

# sensor type 1
SENSOR1_NO_DETECT_VALUE = 0
SENSOR1_LOW_DISTANCE = 0
SENSOR1_HIGH_DISTANCE = 50
SENSOR1_RANGE = 50
SENSOR1_MINIMUM_DISTANCE = 35
SENSOR1_INVERT = True

# sensor type 2
SENSOR2_NO_DETECT_VALUE = 4.094
SENSOR2_LOW_DISTANCE = 0
SENSOR2_HIGH_DISTANCE = 6
SENSOR2_RANGE = 6
SENSOR2_MINIMUM_DISTANCE = 2
SENSOR2_INVERT = False

# sensor type 1
RANGEFINDER_0 = {'address': ADDRESS_1, 'channel': 3, 'no_detect_val': SENSOR1_NO_DETECT_VALUE, 'max_distance': SENSOR1_HIGH_DISTANCE, 'minimum_distance': 0, 'invert': SENSOR1_INVERT, 'minimum_value': 0.354, 'mv_per_mm': 0.0882}
RANGEFINDER_1 = {'address': ADDRESS_1, 'channel': 2, 'no_detect_val': SENSOR1_NO_DETECT_VALUE, 'max_distance': SENSOR1_HIGH_DISTANCE, 'minimum_distance': 0, 'invert': SENSOR1_INVERT, 'minimum_value': 0.348, 'mv_per_mm': 0.0895}
RANGEFINDER_2 = {'address': ADDRESS_1, 'channel': 1, 'no_detect_val': SENSOR1_NO_DETECT_VALUE, 'max_distance': SENSOR1_HIGH_DISTANCE, 'minimum_distance': 0, 'invert': SENSOR1_INVERT, 'minimum_value': 0.52, 'mv_per_mm': 0.0951}
RANGEFINDER_3 = {'address': ADDRESS_1, 'channel': 0, 'no_detect_val': SENSOR1_NO_DETECT_VALUE, 'max_distance': SENSOR1_HIGH_DISTANCE, 'minimum_distance': 0, 'invert': SENSOR1_INVERT, 'minimum_value': 0.286, 'mv_per_mm': 0.0908}

# sensor type 2
RANGEFINDER_4 = {'address': ADDRESS_2, 'channel': 3, 'no_detect_val': SENSOR2_NO_DETECT_VALUE, 'max_distance': SENSOR2_HIGH_DISTANCE, 'minimum_distance': 0, 'invert': SENSOR2_INVERT, 'minimum_value': SENSOR2_NO_DETECT_VALUE, 'mv_per_mm': 0.862}
RANGEFINDER_5 = {'address': ADDRESS_2, 'channel': 2, 'no_detect_val': SENSOR2_NO_DETECT_VALUE, 'max_distance': SENSOR2_HIGH_DISTANCE, 'minimum_distance': 0, 'invert': SENSOR2_INVERT, 'minimum_value': SENSOR2_NO_DETECT_VALUE, 'mv_per_mm': 0.904}

ALL_RANGEFINDERS = [
    RANGEFINDER_0,
    RANGEFINDER_1,
    RANGEFINDER_2,
    RANGEFINDER_3,
    RANGEFINDER_4,
    RANGEFINDER_5
]


def get_distance(value, minimum_value=0.354, mv_per_mm=0.91, invert=False):
    if invert:
        real_distance = (value - minimum_value) / (mv_per_mm * 10)
        real_distance = real_distance * -1
    else:
        real_distance = (minimum_value - value) / mv_per_mm
    return real_distance


def get_one_value(address=ADDRESS_1, channel=3):
    adc = ADS1x15(address=address, ic=ADS1015)
    volts = adc.readADCSingleEnded(channel, GAIN, SPS) / 1000
    return volts


def get_all_values():
    all_vals = [get_one_value(parameters['address'], parameters['channel']) for parameters in ALL_RANGEFINDERS]
    return all_vals


def get_all_distances():
    all_distances = [
        get_distance(
            value=get_one_value(sensor['address'], sensor['channel']),
            minimum_value=sensor['minimum_value'],
            mv_per_mm=sensor['mv_per_mm'],
            invert=sensor['invert'])
        for sensor in ALL_RANGEFINDERS
    ]
    return all_distances


if __name__ == '__main__':
    # all_values = get_all_distances()
    # print(all_values)
    # for value in all_values:
    #     print("%.6f" % value)
    print(get_all_values())
    print(get_all_distances())
