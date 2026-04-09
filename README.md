# OnAirService (v5)

Modern macOS microphone and camera activity monitoring service for controlling an external "On-Air" indicator.

This is the fifth iteration of the project, evolving from a simple monitoring script into a full-fledged background service. The key improvement in v5 is the use of the native macOS event loop (`NSRunLoop`), allowing for efficient and stable device polling without leaks or process blocks.

## The Idea
The idea is simple: let people around you know your mood. When you are on a call, you are likely not ready to be interrupted. When you are just listening to music or working in silence, it’s a different story.

Since macOS has no native external "On-Air" light support, this project bridges that gap by monitoring system-level device usage and signaling an external LED indicator (ESP8266 + NeoPixel) over the network.

## Architecture
The system consists of two parts:
1. **The Host Daemon (v5)**: A Python service running on your MacBook. It utilizes `PyObjC` to interface directly with `CoreAudio` and `CoreMediaIO` frameworks. It runs a `NSRunLoop` with a timer to check the status of all microphones and cameras every 8 seconds.
2. **The LED Module**: An ESP01S (ESP8266) directly controlling an Adafruit RGB NeoPixel ring (8 LEDs).

**Signals:**
The daemon sends three types of HTTP GET requests to the LED module:
*   `/video`: Green light (Camera active).
*   `/air`: Yellow/Orange light (Microphone active).
*   (Stop sending): Vacant (The LED module has a ~9s safety timeout; if no signal is received, it turns off automatically).

## Project Evolution
- **v5 (Current)**: Full `PyObjC` service using `AppHelper.runConsoleEventLoop`. Fixed v4's limitation where device states wouldn't refresh without restarting the process.
- **v4**: Used `CoreAudio`/`CoreMediaIO` but required running the check in a separate subprocess (`checkIsMicOn.py`) via `subprocess` every 8 seconds due to environment constraints.
- **v3**: Used a "hack" analyzing screenshots to detect the system's "orange dot" (microphone indicator) in the menu bar.
- **v2**: Based on parsing system utility outputs (`ioreg` and system profile).
- **v1**: Initial prototypes using ESP01S and ATtiny as a port-proxy.

## Features
- **Native Event Loop**: `NSTimer` inside `NSRunLoop` ensures responsiveness and proper interaction with Apple system frameworks.
- **Low Resource Usage**: No heavy subprocesses or screen recording permissions required.
- **Reliability**: PID-file protection against duplicate instances, structured logging, and automatic persistence via `launchd`.

## Installation & Usage

### Option 1: Via uv (Recommended)
If you have [uv](https://github.com/astral-sh/uv) installed, dependencies and environment will be managed automatically:
```bash
uv run OnAirService.py
```

### Option 2: Via pip
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the service:
   ```bash
   python OnAirService.py
   ```

## Autostart (macOS)

To run the service in the background and start automatically on login:

1. Copy the configuration file:
   ```bash
   mkdir -p ~/Library/LaunchAgents/
   cp com.katurov.onairservice.plist ~/Library/LaunchAgents/
   ```

2. Load the agent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.katurov.onairservice.plist
   ```

Logs are available at `~/Library/Logs/OnAirService.stdout.log`.

### Management
- **Status**: `launchctl list | grep onairservice`
- **Stop**: `launchctl unload ~/Library/LaunchAgents/com.katurov.onairservice.plist`
