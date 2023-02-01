# ONAIR light for room

This is dummy quarantine project to show I'm on the call to help people around understand my mood. It is a bit overkill with three controllers for two LEDs, but it works, I don't need more.

## The idea

Work form home is one of a main change in our lifes in 2020. Sometimes people in the same room cannot determine are you busy at conference-call or just listen the music. To help 'em in that question I made simply ONAIR lights like these in big studios. 

Nobody can keep thinking about turn it on and off, so I started to think how can I made it authomatic. Don't know how to made it in different platforms, but I have MacBook Air (Catalina), which can provide on system level an answer is mic on, is camera on. So, fetching these data help to automate this task.

As soon as many people nowadays uses Slack messenger, here is a hook to change "state" for users.

## Arhitecture

LED module connected to local WiFi network and accepts signals: "voice", "air" and "vacant". For "voice" it make yellow lingt on, for "air" - green one, "vacant" means both have to be off.

A daemon on host machine constantly checks is mic or camera on or off. If mic is on - sends "voice" signal (to slack and led module), if camera is on - "air" signal. If new state if both "off" (and earier one of 'em were on) sends "vacant" signal. 

Software can disappear in a moment, so LED module have a timeout: no signal for about 9 seconds means host is down or anyway "vacant".

## A Problem

I made a few versions:

First one was simplier: led are connected directly to ESP10S. It works, but they are npt that bright.

Second one uses transistors as keys to use LEDs on +5v. But it creates new problem: it creates LOW on GPIO0 and GPIO2 so ESP won't start. So i've added two capacitors to add HIGH on a power-on circle, but it made LED blinky after 15 minutes of work. Not that good (btw., may be it is perfect - I hate long meetings).

Third vesrion uses ATtiny as a port-proxy. You can see the schematic below.

## The Schematics

![Schematix](https://raw.githubusercontent.com/katurov/onair-room-light/main/v1/IMG_3250.jpeg)

[More pictures is here](https://github.com/katurov/onair-room-light/blob/main/v1/images/readme.md)

## How Does It Work

* ESP01S connected to WiFi and starts web-server, now waiting for a signal.
* As soon as signal received, ESP put GPIO HIGH
* As soon as INPUT PB on ATTiny13A goes HIGH it put corresponded PB HIGH
* Transistor opens
* LED does shine

## How many LEDs can be connected?

I used two LEDs for each transistor. They are bright and fun.
