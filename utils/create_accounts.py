from utils.settings import write_file
from utils import constants


def create_account():
    
    write_file(constants.py_accounts, constants.default_entry)
    
    print(constants.welcome_message)