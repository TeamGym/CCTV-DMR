from dataclasses import dataclass
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GstElement

@dataclass
class RtspCctvSession:
    dest: GstElement

