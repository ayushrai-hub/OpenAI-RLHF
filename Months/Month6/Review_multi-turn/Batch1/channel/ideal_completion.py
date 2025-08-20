import time
import numpy as np

channelConversion = 0.62477120195241

def configure_channels(channels: 'CRSFChannels', state: str, time_to_run: int) -> str:
    start_time = time.time()
    ch5_updated = False

    while time.time() - start_time < time_to_run:
        current_time = time.time()
        elapsed_time = current_time - start_time

        if not ch5_updated and elapsed_time >= 5:
            channels.ch5 = 2011
            ch5_updated = True

        if state == 'activate':
            channels_values = [
                channels.ch0, channels.ch1, channels.ch2, channels.ch3,
                channels.ch4, channels.ch5, channels.ch6, channels.ch7,
                channels.ch8, channels.ch9, channels.ch10, channels.ch11,
                channels.ch12, channels.ch13, channels.ch14, channels.ch15
            ]

            converted_channels = [
                np.uint16((np.float32(ch - 881) / channelConversion) + 1)
                for ch in channels_values
            ]

        time.sleep(0.004)
    
    return state
