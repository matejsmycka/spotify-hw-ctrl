# Spotify hardware controller

You can control spotify with a hardware controller. The controller has a rotary potentiometer to control the volume, a push button to play/pause and an LCD display to show the current song.

# Hardware

- rp2040 microcontroller
- 1 rotary potentiometer
- 1 push button
- 1 I2C LCD display

# Setup

1. Setup rp2040 with micropython
1. Copy `/io_controller` to the rp2040
1. Install required libraries in requirements.txt on host machine
1. Setup spotify api and get client id and client secret
1. Run server.py
