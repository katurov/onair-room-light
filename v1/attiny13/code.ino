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
  pinMode(PB1, OUTPUT);
  pinMode(PB2, OUTPUT);
  pinMode(PB3, INPUT);
  pinMode(PB4, INPUT);
}

void loop() {
  digitalWrite(PB1, digitalRead(PB4));
  digitalWrite(PB2, digitalRead(PB3));
  delay(100);
}

/*
WHAT by Paul A Katurov <katurov@gmail.com>
*/
