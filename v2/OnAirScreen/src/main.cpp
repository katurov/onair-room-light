#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

#define PIN         0
#define NUMPIXELS   8
#define DELAYVAL    150

const     char*         ssid          = "WIFI NETWORK NAME";
const     char*         password      = "WIFI NETWORK PASSWORD";
volatile  bool          onceupdated   = false;
volatile  unsigned long lastupdatedat = 0;

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
ESP8266WebServer server(80);

void fillCircle( int c_red, int c_green, int c_blue ) {
  pixels.clear();
  for (int i = 0; i < NUMPIXELS; i ++ ) {
    pixels.setPixelColor(i, pixels.Color( c_red, c_green, c_blue));
    pixels.show();
    delay(DELAYVAL);
  }
  lastupdatedat = millis();
  onceupdated   = true;
}

void setMicOn () {
    fillCircle( 255, 165, 0 );
}

void setCamOn () {
    fillCircle( 5, 102, 8 );
}

void handleRoot() {
  server.send(200, "text/plain", "Air Sign ok\n");
}

void handleNotFound() {
  server.send(404, "text/plain", "Not found\n");
}

void handleVoice () {
  server.send(200, "text/plain", "Voice\n");
  setMicOn ();
}

void handleVideo () {
  server.send(200, "text/plain", "Video\n");
  setCamOn ();
}


void setup() {

  Serial.begin( 115200 );

  delay(2000);

  int i = 0;
  pixels.begin();
  pixels.clear();
  pixels.show();
  pixels.setBrightness(50);

  Serial.println("Pixel ok");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    pixels.setPixelColor(i, pixels.Color( 120, 120, 120));
    pixels.show();
    if ( i >= NUMPIXELS) {
      pixels.clear();
      pixels.show();
      i = 0;
    }
    else i ++;
    delay( DELAYVAL );
  }

  pixels.clear();
  pixels.show();

  Serial.println("WiFi ok");

  MDNS.begin("airsign");

  Serial.print("DNS ok");

  server.on("/", handleRoot);
  server.on("/air", handleVoice);
  server.on("/voice", handleVoice);
  server.on("/video", handleVideo);
  server.onNotFound(handleNotFound);

  server.begin();
}

void loop() {
  server.handleClient();
  MDNS.update();

  if (((millis() - lastupdatedat) > 10000) && onceupdated) {
    // Probably we lost signal from OSX (client) and have to clear the screen
    onceupdated = false;
    pixels.clear();
    pixels.show();
  }

}