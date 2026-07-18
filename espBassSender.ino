#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

//=========================================================
// BAIXO CLONE HERO
// ESP-NOW TRANSMISSOR
// ESP32 Core 2.0.14
//
// LED AZUL (GPIO2)
// - Pisca rapidamente quando um envio é OK
// - Após 3 falhas consecutivas entra em modo piscando
// - Sai do modo piscando automaticamente quando voltar
//   a conseguir enviar.
//
//=========================================================

//======================
// MAC DO RECEPTOR
//======================

uint8_t receiverMAC[] = {
  0x10, 0x06, 0x1C, 0xF6, 0x45, 0xDC
};

//======================
// LED
//======================

const byte LED_AZUL = 2;

//======================
// PINOS
//======================

const byte TOTAL = 7;

const byte botoes[TOTAL] = {
  13, // GREEN
  12, // RED
  14, // YELLOW
  27, // BLUE
  26, // ORANGE
  25, // STRUM
  33  // START
};

//======================
// CÓDIGOS
//======================

const uint8_t downCode[TOTAL] = {
  21, 22, 23, 24, 25, 26, 27
};

const uint8_t upCode[TOTAL] = {
  121, 122, 123, 124, 125, 126, 127
};

//======================
// VARIÁVEIS
//======================

bool estadoAnterior[TOTAL];
unsigned long ultimoDebounce[TOTAL];

const uint16_t debounce = 20;

esp_now_peer_info_t peerInfo;

//======================
// STATUS LED
//======================

volatile bool blinkRapido = false;
volatile unsigned long blinkInicio = 0;

bool modoSemConexao = false;
int falhasSeguidas = 0;

//=========================================================

void piscarSucesso()
{
    blinkRapido = true;
    blinkInicio = millis();
    digitalWrite(LED_AZUL, HIGH);
}

//=========================================================

void OnDataSent(const uint8_t *mac_addr,
                esp_now_send_status_t status)
{
    if (status == ESP_NOW_SEND_SUCCESS)
    {
        falhasSeguidas = 0;
        modoSemConexao = false;

        piscarSucesso();

        Serial.println("OK");
    }
    else
    {
        falhasSeguidas++;

        Serial.print("FALHA ");
        Serial.println(falhasSeguidas);

        if (falhasSeguidas >= 3)
            modoSemConexao = true;
    }
}

//=========================================================

void enviar(uint8_t codigo)
{
    esp_now_send(receiverMAC, &codigo, 1);
}

//=========================================================

void controlarLed()
{
    static unsigned long ultimoPisca = 0;
    static bool estado = false;

    if (modoSemConexao)
    {
        if (millis() - ultimoPisca >= 250)
        {
            ultimoPisca = millis();
            estado = !estado;

            digitalWrite(LED_AZUL, estado);
        }

        return;
    }

    if (blinkRapido)
    {
        if (millis() - blinkInicio >= 50)
        {
            blinkRapido = false;
            digitalWrite(LED_AZUL, LOW);
        }
    }
    else
    {
        digitalWrite(LED_AZUL, LOW);
    }
}

//=========================================================

void setup()
{
    Serial.begin(115200);

    pinMode(LED_AZUL, OUTPUT);
    digitalWrite(LED_AZUL, LOW);

    WiFi.mode(WIFI_STA);

    // Reduz latência
    WiFi.setSleep(false);

    WiFi.disconnect();

    // Força canal 1
    esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

    Serial.print("MAC deste ESP: ");
    Serial.println(WiFi.macAddress());

    if (esp_now_init() != ESP_OK)
    {
        Serial.println("Erro ESP-NOW");

        while (true)
        {
            delay(100);
        }
    }

    esp_now_register_send_cb(OnDataSent);

    memcpy(peerInfo.peer_addr, receiverMAC, 6);
    peerInfo.channel = 1;
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK)
    {
        Serial.println("Erro ao adicionar peer");

        while (true)
        {
            delay(100);
        }
    }

    for (byte i = 0; i < TOTAL; i++)
    {
        pinMode(botoes[i], INPUT_PULLUP);

        estadoAnterior[i] = digitalRead(botoes[i]);
        ultimoDebounce[i] = 0;
    }

    Serial.println("Transmissor do BAIXO iniciado.");
}

//=========================================================

void loop()
{
    controlarLed();

    unsigned long agora = millis();

    for (byte i = 0; i < TOTAL; i++)
    {
        bool leitura = digitalRead(botoes[i]);

        if (leitura != estadoAnterior[i])
        {
            if (agora - ultimoDebounce[i] >= debounce)
            {
                ultimoDebounce[i] = agora;
                estadoAnterior[i] = leitura;

                if (leitura == LOW)
                {
                    enviar(downCode[i]);
                }
                else
                {
                    enviar(upCode[i]);
                }
            }
        }
    }
}
