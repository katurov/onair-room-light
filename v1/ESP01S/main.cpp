#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

const     char*         ssid          = "<YOUR-NET-HERE>";       // Put here name of your WiFi network
const     char*         password      = "<YOUS-PASSWORD-HERE>";  // Put here the password of your WiFi network
const     int           yellow        = 0;                       // I've used YELLOW LED to show that my mic is on
const     int           green         = 2;                       // I've used GREEN LED to show my camera is on
volatile  bool          onceupdated   = false;
volatile  unsigned long lastupdatedat = 0;

ESP8266WebServer server(80);

/*
Here is no idea what to answer for root, so - empty

NB: ESP cannot answer HTTP-202, so I've used 200 + space as an answer
*/
void handleRoot() {
  server.send(200, "text/plain", " ");
}

/*
OK, so we are on air (voice + picture) so lets UP GREEN
*/
void handle_OnAir() {
  digitalWrite(yellow, 0);
  digitalWrite(green, 1);
  lastupdatedat = millis();
  onceupdated = true;
  server.send(200, "text/plain", " ");
}

/*
OK, just a voice, lets show YELLOW 
*/
void handle_OnVoice () {
  digitalWrite(green, 0);
  digitalWrite(yellow, 1);
  lastupdatedat = millis();
  onceupdated = true;
  server.send(200, "text/plain", " ");
}

/*
The meeting is over, we have to kill all lights
*/
void handle_OnVacant () {
  digitalWrite(yellow, 0);
  digitalWrite(green, 0);
  lastupdatedat = millis();
  onceupdated = false;
  server.send(200, "text/plain", " ");
}

/*
This is just to have someting to say if we have 404
*/
void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}

/*
Actually we have no reason to use Serail as a monitoring, BUT this is usefull duing testing, so I let it be here

Setting all things up

NB: ESP trying to use domain name airscreen (e.g. airscreen.local) for presence, this is a good practice
*/
void setup() {
  pinMode(yellow, OUTPUT);
  pinMode(green, OUTPUT);
  digitalWrite(yellow, 0);
  digitalWrite(green, 0);

  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  if (MDNS.begin("airscreen")) {
    Serial.println("MDNS responder started");
  }

  server.on("/", handleRoot);
  server.on("/air", handle_OnAir);
  server.on("/voice", handle_OnVoice);
  server.on("/video", handle_OnAir);
  server.on("/vacant", handle_OnVacant);

  server.onNotFound(handleNotFound);

  server.begin();
  Serial.println("HTTP server started");
}


/*
THE LOOP

NB: sometimes I just close the lid, so signal lost, by this there is a trigger by time:
if no signal for 10 seconds, lets suppose the computer is down, kill all lights
*/
void loop() {
  server.handleClient();
  MDNS.update();

  if (((millis() - lastupdatedat) > 10000) && onceupdated) {
    // Probably we lost signal from OSX (client) and have to clear the screen
    onceupdated = false;
    digitalWrite(yellow, 0);
    digitalWrite(green, 0);
  }

}
