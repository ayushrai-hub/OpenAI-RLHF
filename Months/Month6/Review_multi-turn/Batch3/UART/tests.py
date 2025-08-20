import unittest
import time
from ideal_completion import configure_channels


def calculate_crc8(crc, val, poly):
    crc ^= val
    for _ in range(8):
        if crc & 0x80:
            crc = (crc << 1) ^ poly
        else:
            crc <<= 1
    return crc & 0xFF

def compute_crc8_dvb_s2(crc, val):
    return calculate_crc8(crc, val, 0xD5)

def compute_crc8_poly_0xba(crc, val):
    return calculate_crc8(crc, val, 0xBA)

def get_cmd_crc_for_crsf_frame(buf):
    crc = compute_crc8_poly_0xba(0, buf[2])  # packet type
    for b in buf[3:]:
        crc = compute_crc8_poly_0xba(crc, b)  # payload
    return crc

def get_crc_for_crsf_frame(buf):
    crc = compute_crc8_dvb_s2(0, buf[2])  # packet type
    for b in buf[3:]:
        crc = compute_crc8_dvb_s2(crc, b)  # payload
    return crc


class CRSFChannels:
    def __init__(self):
        self.ch0 = 1500
        self.ch1 = 1500
        self.ch3 = 1500
        self.ch2 = 989
        self.ch4 = 989
        self.ch5 = 989
        self.ch6 = 1000
        self.ch7 = 1000
        self.ch8 = 1000
        self.ch9 = 1000
        self.ch10 = 1000
        self.ch11 = 1000
        self.ch12 = 1000
        self.ch13 = 1000
        self.ch14 = 1000
        self.ch15 = 1000

    def pack(self):
        collection = bytearray()
        collection.extend(self.pack_channel(self.ch0))
        collection.extend(self.pack_channel(self.ch1))
        collection.extend(self.pack_channel(self.ch2))
        collection.extend(self.pack_channel(self.ch3))
        collection.extend(self.pack_channel(self.ch4))
        collection.extend(self.pack_channel(self.ch5))
        collection.extend(self.pack_channel(self.ch6))
        collection.extend(self.pack_channel(self.ch7))
        collection.extend(self.pack_channel(self.ch8))
        collection.extend(self.pack_channel(self.ch9))
        collection.extend(self.pack_channel(self.ch10))
        collection.extend(self.pack_channel(self.ch11))
        collection.extend(self.pack_channel(self.ch12))
        collection.extend(self.pack_channel(self.ch13))
        collection.extend(self.pack_channel(self.ch14))
        collection.extend(self.pack_channel(self.ch15))
        return collection

    @staticmethod
    def pack_channel(value):
        return value.to_bytes(2, 'little')[0:2]  # Extract only the first 11 bits


class TestPythonCode(unittest.TestCase):
    def test_change_with_activate_longer(self):
        # This test checks if channel 5 was updated after more than 5 seconds.
        # the function ran in "activate" state
        channels = CRSFChannels()
        channels.ch5 = 989
        state = 'activate'
        time_to_run = 6
        expected_result = 2011

        new_state = configure_channels(channels, state, time_to_run)
        self.assertEqual(channels.ch5, expected_result)
        self.assertEqual(state, new_state)

    def test_change_with_activate_shorter(self):
        # This test checks if channel 5 was updated after less than 5 seconds.
        # the function ran in "activate" state
        channels = CRSFChannels()
        channels.ch5 = 989
        state = 'activate'
        time_to_run = 3
        expected_result = 989

        new_state = configure_channels(channels, state, time_to_run)
        self.assertEqual(channels.ch5, expected_result)
        self.assertEqual(state, new_state)

    def test_change_with_deactivate_longer(self):
        # This test checks if channel 5 was updated after more than 5 seconds.
        # the function ran in "deactivate" state

        channels = CRSFChannels()
        channels.ch5 = 989
        state = 'deactivate'
        time_to_run = 6
        expected_result = 2011

        new_state = configure_channels(channels, state, time_to_run)
        self.assertEqual(channels.ch5, expected_result)
        self.assertEqual(state, new_state)

    def test_change_with_deactivate_shorter(self):
        # This test checks if channel 5 was updated after less than 5 seconds.
        # the function ran in "deactivate" state
        channels = CRSFChannels()
        channels.ch5 = 989
        state = 'deactivate'
        time_to_run = 3
        expected_result = 989

        new_state = configure_channels(channels, state, time_to_run)
        self.assertEqual(channels.ch5, expected_result)
        self.assertEqual(state, new_state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
