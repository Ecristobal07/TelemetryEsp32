#Beginning of Project, 6/05/2026

### Goal: Set up esp32 on Arduino IDE

## What I tried:
- Downloading esp boards on IDE
- Plugging into computer
- selected correct board and COM3
- Uploaded GetChipID

## Problem
- The esp did not want to connect to the arduino IDE popped up an error called "failed to get serial data"

## Investigation
- Watched Youtube videos on how to fix connection problem
- Visited https://docs.espressif.com/projects/esptool/en/latest/esp32/troubleshooting.html
- Added a url to preferences on Arduino IDE
- Dropped Upload speed
- connected usb to different port
- Asked ChatGPT, which then pointed me at a driver error
- Com3 was not reading the esp32, but there was another port CP2102 that had yellow marker. This was the culprit

## Conclusion
The esp32 was being detected but I did not have the right drivers installed.

### Fix
Install the Silicon Labs CP210x driver, restart the computer, reconnect the ESP32, and select the new Silicon Labs COM port in Arduino IDE.

## What I learned
- A COM being able to be selected does not mean it will work automatically. Make sure you have the right drivers installed for whatever you are using.
- Device manager is a handy tool to see if there's an issue with ports
- The CP2102 chip converts USB from the computer into serial communcation for the esp32, i.e data transfer.

### Maintanence/config setup Day (6/12/2026)

## Goal (Pushed back)
- use DHT22 sensor

## Issue
- My breadboard could not fit the esp32. I had enough spaces for one side, not the other

##  SOlution
- REmove a power rail from breadboard connect two boards together. Frankenstein BReadboard

## What I learned Today
-Bread boards are very modular

# 6/16/2026

## Goal: Read Data from DHT22 Sensor
- I have a DHT22 sensor I want to read temp, humidity from

## Investigation
- https://esp32io.com/tutorials/esp32-dht22 is a very good source for tutorials
- Connected a GIOP pin to the DHT22 Sensor
- Connected GND and 3.3v to respective pins
- Put sensor in different areas

## Conclusion
- DHT22 Sensor works, temp changes depending on location, as well as humidity.

## What I learned today
I learned that power comes directly from the micro-usb cable
I learned that each pin can do something different on esp32, or your code should relate to the respective pin you chose




# 6/19/2026

## Goal 
- I want to connect mpu6050 to esp32

## Investigation
- I tried to do it with an unsoldered mpu-sensore. It did not work. I bought another one.
- THe new one did work.
- I ran an example from Arduino IDE.

## Conclusion
- The sensor reads x, y, and z as well as rotation
- actually pretty cool as spinning it increases the rotation in rad/s.
- Also note the z axis does actually have 9.8 m/s^2 and when you flip it, well it changes lol.


# Part 1 is complete
- All sensors work seperately.
- The next thing to do is to connect all of them together and have a UI. This is part 2
