from utils import constants
from utils.settings import open_file, write_file

# Save the chest priority levels and unit priority levels on their respective keys.
def update_settings(entry_chest, entry_unit):

    # Load the existing JSON data
    settings_data = open_file()

    # Update values for "chest"
    for chest_key in constants.chest_priorities:
        if chest_key in entry_chest:
            # If the chest key already exists in entry_chest, update the value as an integer
            settings_data[chest_key] = convert_to_integer(entry_chest[chest_key])
        else:
            # If the chest key does not exist, add it with an empty string value
            settings_data[chest_key] = 0

    # Update "priority" for units in "userUnits"
    user_units = settings_data.get("userUnits", [])
    for user_id_to_update, priority in entry_unit.items():
        for unit in user_units:
            if unit.get("unitId") == user_id_to_update:
                priority = convert_to_integer(priority)
                unit["priority"] = priority

    # Save the updated JSON data back to the file
    write_file(settings_data)

def convert_to_integer(value):
    try:
        # Attempt to convert the value to an integer
        result = int(value)
    except (ValueError, TypeError):
        # Handle the case where the conversion fails or the value is not a valid integer
        result = 0
    return result