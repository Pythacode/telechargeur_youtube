import json
import os
from context import log, appData_folder

class Config :
    def __init__(self):
        self.file = os.path.join(appData_folder, 'config.json')
        try :
            with open(self.file, 'r', encoding='utf-8') as f:
                log.log(f"Open configuration file : \"{self.file}\"")
                self.configuration = json.load(f)
        except :
            log.warnig(f"Can't oppend configuration file \"{os.path.join(appData_folder, 'config.json')}\". Start with blank configuration")
            self.configuration = {}
        finally :
            for key, value in self.configuration.items():
                    log.log(f'Create configuration : "{key}" = "{value}"')
                    setattr(self, key, value)

    def updtadeConfig(self, key, value) :
        self.key = value
        self.configuration[key] = value
        log.log(f'Update configuration : "{key}" = "{value}"')
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(self.configuration, f, ensure_ascii=False, indent=4)