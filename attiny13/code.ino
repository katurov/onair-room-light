/*
Main idea is to use ATtiny13 as port-proxy

Problem:
  ESP01S need HIGH on GPIO0 and GPIO2 to start normal booting. But when pins are connected to 
  transistors here is LOW signal on these pins. I've tried to solve problem with capacitors,
  but this gave me wrong-on during work load.
  
Solution:
  Bad: use ATtiny13 at startup procedure to generate HIGH on GPIO0 and GPIO2 (doesn't help)
  
  Good: use ATtiny13 as port-proxy. This solve the problem.
  
*/

void setup() {
  pinMode(PB3, OUTPUT);
  pinMode(PB4, OUTPUT);
  pinMode(PB1, INPUT);
  pinMode(PB2, INPUT);
}

void loop() {
  digitalWrite(PB3, digitalRead(PB2));
  digitalWrite(PB4, digitalRead(PB1));
  delay(100);
}

/*
WHAT by Paul A Katurov <katurov@gmail.com>
*/
