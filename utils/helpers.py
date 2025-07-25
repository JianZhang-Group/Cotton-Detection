def format_coordinates(coordinates):
    return [(round(x, 2), round(y, 2)) for x, y in coordinates]

def log_message(message):
    with open("app.log", "a") as log_file:
        log_file.write(f"{message}\n")

def load_config(config_file):
    import yaml
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)