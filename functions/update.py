# testing script to find a way to update my code

# imports
import requests

def update_version(current_version, update_url):
    """
    :param current_version: the current running version of the script
    :param update_url: Git url where the latest versions will be stored
    :return: True if there is an update or False otherwise
    """
    try:
        response = requests.get(update_url)
        response.raise_for_status()
        update_version = response.text.strip()

        if update_version > current_version:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error Checking for update")
        return False
