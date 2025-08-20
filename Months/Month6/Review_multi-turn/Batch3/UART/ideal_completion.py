import time

def configure_channels(channels: 'CRSFChannels', state: str, time_to_run: int) -> str:
    start_time = time.time()
    while (time.time() - start_time) < time_to_run:
        elapsed_time = time.time() - start_time

        if elapsed_time > 5:
            channels.ch5 = 2011

    return state
