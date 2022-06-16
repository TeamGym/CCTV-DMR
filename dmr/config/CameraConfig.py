from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class CameraConfig:
    camId: int
    name: str
    udpPort: int
    channel: int
