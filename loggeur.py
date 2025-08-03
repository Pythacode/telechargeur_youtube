from datetime import datetime
import os
from colorama import Fore, init

init(autoreset=True)

class Loggeur() :
    def __init__(self, appData_folder) :

        log_file = os.path.join(appData_folder, "logs")

        if not os.path.exists(log_file):
            os.makedirs(log_file)

        self.file = open(os.path.join(log_file, f"{datetime.now().strftime('%Y_%m_%d')}.log"), 'a+', encoding='utf-8')
        message = f"[START] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]"
        self.file.write(message + '\n')

    def log(self, message) :
        message = f"[INFO] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(message + '\n')
        print(message)

    def error(self, message) :
        message = f"[ERROR] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(message + '\n')
        print(Fore.RED + message)

    def warnig(self, message) :
        message = f"[WARNING] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}"
        self.file.write(message + '\n')
        print(Fore.YELLOW + message)