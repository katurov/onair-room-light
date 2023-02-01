# ONAIR light for room

In 2022 I need something that works with macOS Monterey as soon as system doesn't report me a mic state if used AirPods and something like that. Also I need to update the indicator: make it bigger and brighter.

## The idea

Work form home is one of a main change in our lifes from 2020. Sometimes people in the same room cannot determine are you busy at conference-call or just listen the music. To help 'em in that question I made simply ONAIR lights like these in big studios. 

Nobody can keep thinking about turn it on and off, so I started to think how can I made it authomatic. Don't know how to made it in different platforms, but I have MacBook Pro M1 2020 (Monterey) and here is my version of the python3 script to determine is cam on with system report and is mic on with finding an orange dot in the right upper corner of the screen.

## Arhitecture

LED module connected to local WiFi network and accepts signals: "voice", "air" and "vacant". For "voice" it make yellow lingt on, for "air" - green one, "vacant" means both have to be off.

A daemon on host machine constantly checks is mic or camera on or off. If mic is on - sends "voice" signal (to slack and led module), if camera is on - "air" signal. If new state if both "off" (and earier one of 'em were on) sends "vacant" signal. 

Software can disappear in a moment, so LED module have a timeout: no signal for about 9 seconds means host is down or anyway "vacant".

## How Does It Work

* ESP01S connected to WiFi and starts web-server, now waiting for a signal.
* Script on a host mashine check the state and makes GET request if something is on use
* As soon as signal received, ESP lights the LED up
