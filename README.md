# Clone Hero ESP32 UDP

Projeto simples para usar guitarra ou bateria feita com ESP32 no Clone Hero. O ESP32 le os botoes e envia comandos por UDP para este script Python, que aperta teclas no Windows.

## O que precisa

- ESP32
- Arduino IDE
- Bibliotecas Arduino:
  - `WiFiManager`
  - `WiFi`
  - `WiFiUdp`
- Python 3.11 instalado no PC
- Clone Hero instalado

## Instalar dependencias do Python

No terminal, dentro desta pasta:

```bash
pip install pynput
```

## Configurar o ESP32

1. Abra o codigo do ESP32 na Arduino IDE.
2. Instale a biblioteca `WiFiManager` pelo Library Manager.
3. Confira a porta UDP:

```cpp
const int PORTA_UDP = 4210;
```

4. Para mais estabilidade, envie direto para o IP do PC. Exemplo:

```cpp
IPAddress broadcastIP(10, 0, 0, 195);
```

Use o IPv4 do seu PC, visto no `ipconfig`.

5. Grave o codigo no ESP32.
6. Se ele abrir o portal Wi-Fi, conecte no Wi-Fi criado pelo ESP32, por exemplo `GUITARRA_CLONE_HERO` ou `DRUMS`, e escolha sua rede.

## Rodar o receptor Python

Nesta pasta, execute:

```bash
python hero.py
```

Ele deve mostrar:

```text
Aguardando guitarra ESP32...
Porta UDP: 4210
```

Quando apertar botoes no ESP32, devem aparecer mensagens como:

```text
('10.0.0.xxx', 4210) -> GREEN:DOWN
```

Para bateria, pode aparecer algo como:

```text
('10.0.0.xxx', 4210) -> DRUM_RED:DOWN
```

## Mapeamento da guitarra

```text
GREEN  -> A
RED    -> S
YELLOW -> J
BLUE   -> K
ORANGE -> L
STRUM  -> seta para cima
START  -> seta para baixo
```

## Mapeamento da bateria

```text
DRUM_RED    -> S
DRUM_YELLOW -> J
DRUM_BLUE   -> K
DRUM_GREEN  -> A
DRUM_ORANGE -> L
KICK        -> espaco
START       -> seta para baixo
```

Configure essas mesmas teclas dentro do Clone Hero.

## Se nao funcionar

- Confirme que o PC e o ESP32 estao na mesma rede Wi-Fi.
- Confirme que o IP no codigo do ESP32 e o IPv4 correto do PC.
- Libere o Python no Firewall do Windows.
- Confira se a porta e a mesma nos dois codigos: `4210`.
- Rode o `hero.py` antes de apertar os botoes.
