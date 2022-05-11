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

    def getMessageString(self):
        timestampLine = str(self.timestamp) + '\n'

        boxLines = []

        for box in self.boxes:
            boxLines.append(
                    str(box.left) + ',' +
                    str(box.right) + ',' +
                    str(box.top) + ',' +
                    str(box.bottom) + ',' +
                    str(box.confidence) + ',' +
                    str(box.classID) + ',' +
                    box.label + '\n')

        return timestampLine \
                + ''.join(boxLines)
