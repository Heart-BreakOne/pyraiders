from datetime import datetime

# Log request errors to a file
def log_to_file(message):
    now = datetime.now().strftime("%H:%M:%S")
    log = f"[{now}]: {message}"
    filename = 'logger.txt'
    
    # Append log to the file, create file if file doesn't exist
    try:
        with open(filename, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        content = ''

    updated_content = log + '\n' + content

    with open(filename, 'w') as file:
        file.write(updated_content)