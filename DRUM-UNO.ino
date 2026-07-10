/*
  DRUMS - Arduino Uno
  Envia apenas eventos DOWN pela Serial

  Ligações:
  Botão -> Pino digital
  Outro terminal -> GND

  Serial: 115200
*/

const byte BTN_RED    = 2;
const byte BTN_YELLOW = 3;
const byte BTN_BLUE   = 4;
const byte BTN_GREEN  = 5;
const byte BTN_ORANGE = 6;
const byte BTN_KICK   = 7;
const byte BTN_START  = 8;

const unsigned long DEBOUNCE = 20;

struct Botao {
  byte pino;
  const char* nome;
  bool ultimoEstado;
  unsigned long ultimoTempo;
};

Botao botoes[] = {
  {BTN_RED,    "DRUM_RED:DOWN",    HIGH, 0},
  {BTN_YELLOW, "DRUM_YELLOW:DOWN", HIGH, 0},
  {BTN_BLUE,   "DRUM_BLUE:DOWN",   HIGH, 0},
  {BTN_GREEN,  "DRUM_GREEN:DOWN",  HIGH, 0},
  {BTN_ORANGE, "DRUM_ORANGE:DOWN", HIGH, 0},
  {BTN_KICK,   "KICK:DOWN",        HIGH, 0},
  {BTN_START,  "START:DOWN",       HIGH, 0}
};

const byte TOTAL_BOTOES = sizeof(botoes) / sizeof(botoes[0]);

void setup() {
  Serial.begin(115200);

  for (byte i = 0; i < TOTAL_BOTOES; i++) {
    pinMode(botoes[i].pino, INPUT_PULLUP);
    botoes[i].ultimoEstado = digitalRead(botoes[i].pino);
  }
}

void loop() {

  unsigned long agora = millis();

  for (byte i = 0; i < TOTAL_BOTOES; i++) {

    bool leitura = digitalRead(botoes[i].pino);

    if (leitura != botoes[i].ultimoEstado) {

      if (agora - botoes[i].ultimoTempo < DEBOUNCE)
        continue;

      botoes[i].ultimoTempo = agora;
      botoes[i].ultimoEstado = leitura;

      if (leitura == LOW) {
        Serial.println(botoes[i].nome);
      }
    }
  }
}
