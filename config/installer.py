import subprocess
import sys

def install_package(package_name):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}.")
        print("Error:", e)

def main():
    """Main function to install required packages."""
    print("Checking required packages...")
    with open("requirements.txt", "r") as file:
        required_packages = file.read().splitlines()
        for package in required_packages:
            try:
                __import__(package)
                print(f"{package} is already installed.")
            except ImportError:
                install_package(package)

if __name__ == "__main__":
    main()
