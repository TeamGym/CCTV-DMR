from dataclasses import dataclass

@dataclass
class ControlPTZ:
    pan: int
    tilt: int
    zoom: int

    def getMessageString(self):
        return str(self.pan) + ',' \
                + str(self.tilt) + ',' \
                + str(self.zoom) + '\n'
