import os
import importlib.util

class Manager:
    def setInterpreterLibPath(self):
        self.Lib_Pth = os.environ.get('VBLIB_PATH')

    def register_libraries(self, libs):
        for lib in libs:
            importStatement = rf"from {self.Lib_Pth}.libs import {lib}"
            print(importStatement)
            exec(importStatement)
            