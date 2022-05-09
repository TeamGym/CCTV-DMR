from dataclasses import dataclass

@dataclass
class ControlPTZ:
    pan: int
    tilt: int
    zoom: int
