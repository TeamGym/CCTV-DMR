from dataclasses import dataclass
from typing import List

@dataclass
class DetectionResult:
    timestamp: int
    boxes: List['DetectionResult.DetectionBox']

    @dataclass
    class DetectionBox:
        left: int
        right: int
        top: int
        bottom: int
        confidence: float
        classID: int
        label: str
