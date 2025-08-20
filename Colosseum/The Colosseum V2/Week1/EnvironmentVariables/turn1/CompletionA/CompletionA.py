import sys
import platform

print("Python Version: ", sys.version)
print("Version Info: ", sys.version_info)
print("Executable Path: ", sys.executable)
print("Platform: ", platform.system(), platform.release(), platform.version())
print("Processor: ", platform.processor())
import sys
import platform

print(f'Python Version: {sys.version}')
print(f'Python Version Info: {sys.version_info}')
print(f'Python Executable Path: {sys.executable}')
print(f'Operating System: {platform.system()} {platform.release()}')
print(f'System Version: {platform.version()}')
print(f'Processor: {platform.processor()}')
