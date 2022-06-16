from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from .GlobalSettings import GlobalSettings
from .CameraConfig import CameraConfig

@dataclass_json
@dataclass
class GlobalConfig:
    globalSettings: GlobalSettings
    cameraConfigs: List[CameraConfig]

