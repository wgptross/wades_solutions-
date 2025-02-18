import requests
import subprocess
import os

def check_and_update():
    try:
        from version import __version__  # Import your version
    except ImportError:
        __version__ = "0.0.0"

    def update_application():
        try:
            # Get the current directory of the script.
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Construct the full path to the git executable.
            git_executable = "git"

            # Run git pull from the correct directory.
            subprocess.run([git_executable, "pull", "origin", "master"], cwd=script_dir, check=True)
            print("Application updated. Please Confirm version on app.")
            return True # Indicate successful update
        except subprocess.CalledProcessError as e:
            print(f"Error updating application: {e}")
            return False # Indicate failed update
        except FileNotFoundError:
            print("Git executable not found.  Make sure Git is installed and in your PATH.")
            return False

    def check_for_updates():
        try:
            url = "https://raw.githubusercontent.com/loganfryer22/Random_Projects/refs/heads/master/version.py"
            response = requests.get(url)
            response.raise_for_status()

            remote_version_code = response.text

            try:
                remote_version = remote_version_code.split('__version__ = ')[1].strip().replace('"', '').replace("'", "")
            except IndexError:
                print("Could not parse remote version. Check version.py on GitHub.")
                return None

            if remote_version != __version__:
                print(f"Update available: {__version__} -> {remote_version}")
                return remote_version
            else:
                # print("Application is up to date.")                   # Do not display if it is up to date
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error checking for updates: {e}")
            return None
        except Exception as e:
            print(f"A general error occurred: {e}")
            return None

    if __name__ == "__main__":
        new_version = check_for_updates()
        if new_version:
            if update_application():

                pass # Replace with restart logic if needed.
            else:
                print("Update failed.  Please check the logs.")

check_and_update()