
import random
def get_quarter():
    return random.randint(0, 15)

def get_two_quarters():
    return random.randint(15, 30)

def get_twenty():
    return random.randint(18, 32)

def get_three_quarters():
    return random.randint(30, 45)

def get_four_quarters():
    return random.randint(45, 60)

def get_any():
    return random.randint(5, 60)

def placement_minimum():
    return random.randint(6, 15)

def get_five_min():
    return 300