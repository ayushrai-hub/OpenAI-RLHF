# ideal_completion.py

import subprocess
import shlex
import os
import time
import logging
import threading
from typing import Tuple, Union, List

def execute_command_with_popen(
        command: Union[str, List[str]],
        limit: int = 300,
        shell_execution: bool = False,
        environment: dict = None,
        attempts: int = 0,
        username: str = None
    ) -> Tuple[str, str, int]:

    if isinstance(command, str):
        command = command.strip()
        log_command = command
        if not shell_execution:  # Split command only when not using shell execution
            command = shlex.split(command)
    else:
        log_command = ' '.join(command)  # Record the command in log as a string

    if username and username != "root":
        command = ['sudo', '-u', username] + command
        log_command = f"sudo -u {username} " + log_command

    start = time.time()
    process = None  # Initialize process variable

    try:
        if environment is not None:
            environment = {**os.environ, **environment}

        # Execute the command
        process = subprocess.Popen(command, shell=shell_execution,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   close_fds=True, env=environment, universal_newlines=True)

        timeout_timer = threading.Timer(limit, _terminate_process, [process, log_command, limit])
        timeout_timer.start()

        stdout, stderr = process.communicate(timeout=limit)
        timeout_timer.cancel()

        return_code = process.returncode
    except subprocess.TimeoutExpired as timeout_error:
        logging.error(f"Command '{log_command}' timed out after {limit} seconds.")
        process.terminate()  # Ensure the process is terminated
        stdout, stderr, return_code = "", "COMMAND_TIMED_OUT", 1
    except OSError as error:
        logging.error(f"OS error occurred: {error}")
        stdout, stderr, return_code = "", str(error), 127 if "No such file" in str(error) else 255
    finally:
        if process is not None:  # Ensure process exists before accessing its attributes
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

    total_run_time = time.time() - start
    logging.debug(f"Command '{log_command}' completed in {total_run_time:.2f} seconds.")

    # Handle timeout or retries
    if return_code in (1, 2):  # Generic exit codes for errors or termination
        if attempts > 0:
            logging.warning(f"Retrying command '{log_command}' ({attempts} retries remaining).")
            return execute_command_with_popen(command, limit, shell_execution, environment, attempts - 1, username)
    elif return_code == 0:
        logging.info(f"Command '{log_command}' executed successfully.")
    else:
        logging.error(f"Command '{log_command}' failed with exit code {return_code}.")
        if stderr:
            logging.error(f"Error: {stderr}")
        if stdout:
            logging.debug(f"Output: {stdout}")

    logging.debug(f"Command: {log_command}, Exit code: {return_code}, Output: {stdout}, Error: {stderr}")

    return stdout, stderr, return_code



def _terminate_process(process, command, limit):
    logging.warning(f"Command '{command}' exceeded the time limit of {limit} seconds and will be terminated.")
    try:
        process.terminate()
        process.wait(5)  # Give it 5 seconds to terminate gracefully
        if process.poll() is None:
            logging.warning(f"Command '{command}' did not terminate gracefully, forcing kill.")
            process.kill()
    except Exception as e:
        logging.error(f"Failed to terminate process: {e}")