import sys
import os
import subprocess

def print_environment_details():
    print("Python Version:")
    print(sys.version)
    print("\nPython Executable:")
    print(sys.executable)
    print("\nPython Path:")
    print(sys.path)
    print("\nInstalled Packages:")
    result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    print(result.stdout)
    print("\nEnvironment Variables:")
    for key, value in os.environ.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    print_environment_details()
