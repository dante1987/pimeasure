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

RANGEFINDER_0 = {'address': ADDRESS_1, 'channel': 3}
RANGEFINDER_1 = {'address': ADDRESS_1, 'channel': 2}
RANGEFINDER_2 = {'address': ADDRESS_1, 'channel': 1}
RANGEFINDER_3 = {'address': ADDRESS_1, 'channel': 0}
RANGEFINDER_4 = {'address': ADDRESS_2, 'channel': 3}
RANGEFINDER_5 = {'address': ADDRESS_2, 'channel': 2}

ALL_RANGEFINDERS = [
    RANGEFINDER_0,
    RANGEFINDER_1,
    RANGEFINDER_2,
    RANGEFINDER_3,
    RANGEFINDER_4,
    RANGEFINDER_5
]


def get_one_value(address=ADDRESS_1, channel=3):
    adc = ADS1x15(address=address, ic=ADS1015)
    volts = adc.readADCSingleEnded(channel, GAIN, SPS) / 1000
    return volts


def get_all_values():
    all_values = [get_one_value(**parameters) for parameters in ALL_RANGEFINDERS]
    return all_values


if __name__ == '__main__':
    all_values = get_all_values()
    print(all_values)
    for value in all_values:
        print("%.6f" % value)
