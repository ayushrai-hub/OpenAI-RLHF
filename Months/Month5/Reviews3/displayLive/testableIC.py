import subprocess
import threading
import time
import shlex
import os
import signal
import logging
from typing import Union, List, Tuple

def execute_command_with_popen(
        command: Union[str, List[str]],
        limit: int = 300,
        shell_execution: bool = False,
        environment: dict = None,
        attempts: int = 0,
        username: str = None
    ) -> Tuple[str, str, int]:
    """
    Runs an external command with subprocess.Popen with possible timeout and retries.
    Streams output instantly to terminal.
    """
    
    if isinstance(command, str):
        command = shlex.split(command)  # Split command string into list for Popen
        log_command = command
    else:
        log_command = ' '.join(command)

    if username and username != "root":
        command = ['sudo', '-u', username] + command
        log_command = f"sudo -u {username} " + log_command

    start = time.time()
    
    try:
        if environment is not None:
            environment = {**os.environ, **environment}
        
        process = subprocess.Popen(command, shell=shell_execution,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   close_fds=True, env=environment, universal_newlines=True)
        
        # Timer for managing timeouts
        timeout_timer = threading.Timer(limit, _terminate_process, [process, log_command, limit])
        timeout_timer.start()

        # Stream output line by line
        sout_buffer = []
        serr_buffer = []

        def stream_output(pipe, output_acc, stream_type):
            while True:
                line = pipe.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(line, end='')  # Print to terminal
                    logging.info(f"{stream_type}: {line.strip()}")  # Log output
                    output_acc.append(line)
            pipe.close()

        stdout_threading = threading.Thread(target=stream_output, args=(process.stdout, sout_buffer, "stdout"))
        stderr_threading = threading.Thread(target=stream_output, args=(process.stderr, serr_buffer, "stderr"))
        
        stdout_threading.start()
        stderr_threading.start()
        
        stdout_threading.join()
        stderr_threading.join()
        
        timeout_timer.cancel()
        
        return_code = process.poll()
        stdout_result = ''.join(sout_buffer)
        stderr_result = ''.join(serr_buffer)
        
    except OSError as error:
        logging.error(f"OS error occurred: {error}")
        stdout_result, stderr_result, return_code = "", str(error), 127 if "No such file" in str(error) else 255
    finally:
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()

    total_run_time = time.time() - start
    logging.debug(f"Command '{log_command}' completed in {total_run_time:.2f} seconds.")

    if return_code in (-signal.SIGTERM, -signal.SIGKILL):
        if attempts > 0:
            logging.warning(f"Retrying command '{log_command}' ({attempts} retries remaining).")
            return execute_command_with_popen(command, limit, shell_execution, environment, attempts - 1, username)
        stderr_result = "COMMAND_TIMED_OUT"
        logging.error(f"Command '{log_command}' timed out after {limit} seconds.")
    elif return_code == 0:
        logging.info(f"Command '{log_command}' executed successfully.")
    else:
        logging.error(f"Command '{log_command}' failed with exit code {return_code}.")
        if stderr_result:
            logging.error(f"Error: {stderr_result}")
        if stdout_result:
            logging.debug(f"Output: {stdout_result}")

    logging.debug(f"Command: {log_command}, Exit code: {return_code}, Output: {stdout_result}, Error: {stderr_result}")

    return stdout_result, stderr_result, return_code

def _terminate_process(process, log_command, limit):
    """
    Terminate a process when it exceeds the timeout.
    """
    logging.error(f"Command '{log_command}' exceeded the limit of {limit} seconds and will be terminated.")
    process.terminate()
    try:
        process.wait(timeout=10)  # Give the process a moment to terminate gracefully
    except subprocess.TimeoutExpired:
        logging.error(f"Process '{log_command}' did not terminate gracefully; killing now.")
        process.kill()
