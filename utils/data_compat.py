# Whenever a new key value is added to the py_raiders_account.json this will make sure they are automatically added in


# Check if the new key already exists, then add before the units
def update_data(newDataKey, newDataValue, data):
    new_data = []
    for account in data:
        # Check if the newDataKey already exists in the account
        if newDataKey not in account:
            index = [key for key, value in account.items()].index("units")

            data_key_value_pairs = list(account.items())
            data_key_value_pairs.insert(index, (newDataKey, newDataValue))

            new_account = {}
            for key, value in data_key_value_pairs:
                new_account[key] = value
            new_data.append(new_account)
        else:
            new_data.append(account)

    return new_data

def update_units(newDataKey, newDataValue, data):
    updated_data = []
    for account in data:
        updated_units = []
        for unit in account["units"]:
            updated_unit = unit.copy()
            if newDataKey not in updated_unit:
                updated_unit[newDataKey] = newDataValue
            updated_units.append(updated_unit)
        updated_account = account.copy()
        updated_account["units"] = updated_units
        updated_data.append(updated_account)
    return updated_data


def update_data_structure(data):
    #print("The data structure is up to date.")
    #return data
    newDataKey = "spec_option"
    newDataValue = None
    
    newDataKey2 = "collect_quests"
    newDataValue2 = True
    new_data = update_data(newDataKey2, newDataValue2, data)
    
    new_data = update_units(newDataKey, newDataValue, new_data)
    
    if new_data != data:
        print("The data structure has been updated with new values.")
    else:
        print("The data structure is up to date.")
    return new_data
