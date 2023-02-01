# ONAIR light for room

This is started as a dummy quarantine project to show I'm on the call to help people around understand my mood. It is a bit overkill with three controllers for two LEDs, but it works, I don't need more.

## The idea

Work form home is one of a main change in our lifes from 2020. Sometimes people in the same room cannot determine are you busy at conference-call or just listen the music. To help 'em in that question I made simply ONAIR lights like these in big studios. 

Nobody can keep thinking about turn it on and off, so I started to think how can I made it authomatic. Don't know how to made it in different platforms, but I have MacBook Pro (Monterey), which can provide on system level an answer is camera on. So, fetching these data help to automate this task. To understand that mic is on we have to make a trick (in Catalina it was easy, see v1 for it). The trick is to get a screenshot and find the orange dot in right upper corner made by system if mic is in use.


## Arhitecture

LED module connected to local WiFi network and accepts signals: "voice", "air" and "vacant". For "voice" it make orange lingt on, for "air" - green one, "vacant" means both have to be off. This color schema used in iOS no need to change.

A daemon on host machine constantly checks is mic or camera on or off. If mic is on - sends "voice" signal (to slack and led module), if camera is on - "air" signal. If new state if both "off" (and earier one of 'em were on) sends "vacant" signal. 

Software can disappear in a moment, so LED module have a timeout: no signal for about 9 seconds means host is down or anyway "vacant".

## A Problem

I made a few versions:

Prev vesrion uses ESP01S as server and ATtiny as a port-proxy. [You can see the schematic here](https://github.com/katurov/onair-room-light/blob/main/v1/).

**The current version now** uses ESP01S - a small board with ESP8266 plus small (or big) RGB rong form Adafruit ([code can be found here](https://github.com/katurov/onair-room-light/tree/main/v2/OnAirScreen))

But you caan use any as soon as they are similar in terms of interface.

## macOS difference

Here are [v1](https://github.com/katurov/onair-room-light/tree/main/v1/) which works with Catalina and [v2](https://github.com/katurov/onair-room-light/tree/main/v2/) for Monterey. First one is pretty easy, next is complicated a bit.

## How Does It Work

* Daemon script on host checks is mic or cam in use if yes - sends a request
* ESP01S waits for GET request and if it if in the range - lights up the LED
* LED does shine

## How many LEDs can be connected?

For prev. version I used two LEDs for each transistor. They are bright and fun. In the current version I used 8-led ring
