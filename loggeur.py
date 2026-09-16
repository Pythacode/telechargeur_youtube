from datetime import datetime
import os, re

RED = "[31m"
YELLOW = "[33m"
RESET = "[39m"

class Loggeur() :
    def __init__(self, appData_folder) :

        log_file = os.path.join(appData_folder, "logs")

        if not os.path.exists(log_file):
            os.makedirs(log_file)

        self.file = open(os.path.join(log_file, f"{datetime.now().strftime('%Y_%m_%d')}.log"), 'a+', encoding='utf-8')
        
        message = f"[START] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] --------------------------------------"
        self.file.write(message + '\n')

    def debug(self, message) :
        message = f"[DEBUG] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(self.remove_colors(message) + '\n')
        print(message)

    def info(self, message) :
        message = f"[INFO] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(self.remove_colors(message) + '\n')
        print(message)

    def error(self, message) :
        message = f"[ERROR] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(self.remove_colors(message) + '\n')
        print(RED + message + RESET)

    def warning(self, message) :
        message = f"[WARNING] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(self.remove_colors(message) + '\n')
        print(YELLOW + message + RESET)

    def remove_colors(self, msg):
        color_code_pattern = r'\x1b\[[0-9;]*m'
        return re.sub(color_code_pattern, '', msg)