import subprocess

def install_requirements():
    try:
        subprocess.check_call(['pip3', 'install', '-r', 'utils/requirements.txt'])
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install requirements. {e}")
        
if __name__ == "__main__":
    install_requirements()