import sys
import platform

# Python version
print(f"Python version: {sys.version}")

# Platform information
print(f"Platform: {platform.system()} {platform.release()}")

# Architecture
print(f"Architecture: {platform.architecture()}")

# Machine type
print(f"Machine type: {platform.machine()}")

# Processor
print(f"Processor: {platform.processor()}")

# Python executable location
print(f"Python executable: {sys.executable}")

# Current working directory
print(f"Current working directory: {os.getcwd()}")
