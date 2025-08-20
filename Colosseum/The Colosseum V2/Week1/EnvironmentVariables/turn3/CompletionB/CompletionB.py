import sys
import platform

# Get Python version
python_version = sys.version

# Get system information
system = platform.system()
release = platform.release()
architecture = platform.architecture()

# Print the information
print(f'Python Version: {python_version}')
print(f'System: {system}')
print(f'Release: {release}')
print(f'Architecture: {architecture}')
