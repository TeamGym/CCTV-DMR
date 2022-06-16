#!/bin/sh
gst-launch-1.0 -v rtspsrc latency=0 location="$1" ! rtph264depay ! avdec_h264 ! autovideosink
