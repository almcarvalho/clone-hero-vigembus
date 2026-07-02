//RECEBE OS COMANDOS DE UM ARDUINO UNO VIA PROTOCOLO UART TX > RX PASSANDO POR 2 RESISTORES DE 300OHMS
#include <WiFi.h>
#include <WiFiManager.h>
#include <WiFiUdp.h>

const char* NOME_PORTAL="DRUMS";
const int LED_AZUL=2;

WiFiManager wm;
WiFiUDP udp;
HardwareSerial Uno(2);

const uint16_t PORTA_UDP=5001;
IPAddress broadcastIP(255,255,255,255);

bool portalAberto=false;

void configModeCallback(WiFiManager*){portalAberto=true;}

void enviar(const char* b,const char* a){
  udp.beginPacket(broadcastIP,PORTA_UDP);
  udp.print(b); udp.print(":"); udp.print(a);
  udp.endPacket();
}

void controlarLed(){
 static bool e=false; static unsigned long t=0;
 if(WiFi.status()==WL_CONNECTED){portalAberto=false; digitalWrite(LED_AZUL,HIGH);}
 else if(portalAberto){
  if(millis()-t>300){t=millis(); e=!e; digitalWrite(LED_AZUL,e);}
 } else digitalWrite(LED_AZUL,LOW);
}

void tratarLinha(String s){
 s.trim();
 if(s=="R"){enviar("DRUM_RED","DOWN");delay(5);enviar("DRUM_RED","UP");}
 else if(s=="Y"){enviar("DRUM_YELLOW","DOWN");delay(5);enviar("DRUM_YELLOW","UP");}
 else if(s=="B"){enviar("DRUM_BLUE","DOWN");delay(5);enviar("DRUM_BLUE","UP");}
 else if(s=="G"){enviar("DRUM_GREEN","DOWN");delay(5);enviar("DRUM_GREEN","UP");}
 else if(s=="O"){enviar("DRUM_ORANGE","DOWN");delay(5);enviar("DRUM_ORANGE","UP");}
 else if(s=="K_DOWN") enviar("KICK","DOWN");
 else if(s=="K_UP") enviar("KICK","UP");
 else if(s=="S_DOWN") enviar("START","DOWN");
 else if(s=="S_UP") enviar("START","UP");
}

void setup(){
 Serial.begin(115200);
 Uno.begin(115200,SERIAL_8N1,16,17);
 pinMode(LED_AZUL,OUTPUT);
 wm.setAPCallback(configModeCallback);
 wm.setConfigPortalBlocking(false);
 wm.autoConnect(NOME_PORTAL);
 udp.begin(PORTA_UDP);
}

void loop(){
 wm.process();
 controlarLed();
 while(Uno.available()){
   String s=Uno.readStringUntil('\n');
   tratarLinha(s);
 }
}
