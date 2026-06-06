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






  


