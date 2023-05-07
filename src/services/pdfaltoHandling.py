import pathlib
import os
import subprocess
import platform

class PdfaltoHandling:
    def __init__(self):
        super(PdfaltoHandling, self).__init__()

    def toXML(self, inp, outp):
        try:
            currentPath = str(pathlib.Path(__file__).parent.resolve())
            pf = platform.system()
            nameFile = "exec/pdfalto-linux"
            if pf == "Darwin":
                nameFile = "exec/pdfalto"
                
            execFile = os.path.join(currentPath, nameFile)
            args = [execFile, "-noImage", "-noImageInline", "-readingOrder", inp, outp]

            result = subprocess.run(args, check=True, capture_output=True)
            if result.returncode == 0:
                return True
            else:
                return False
        except subprocess.CalledProcessError as e:
            return False

    def hexToRgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
