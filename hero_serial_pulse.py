import serial,time,vgamepad as vg

PORT="COM4"     # ajuste se necessário
BAUD=2000000
PULSE=0.004     # 4 ms

gp=vg.VX360Gamepad()

MAP={
1:vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
2:vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
3:vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
4:vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
5:vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
6:vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
7:vg.XUSB_BUTTON.XUSB_GAMEPAD_START
}

ser=serial.Serial(PORT,BAUD,timeout=0)

pending=[]

print("Hero Serial Pulse iniciado")

while True:
    now=time.perf_counter()

    data=ser.read(128)
    for c in data:
        btn=MAP.get(c)
        if btn is None:
            continue
        gp.press_button(button=btn)
        gp.update()
        pending.append((now+PULSE,btn))

    if pending:
        now=time.perf_counter()
        i=0
        while i<len(pending):
            t,btn=pending[i]
            if now>=t:
                gp.release_button(button=btn)
                gp.update()
                pending.pop(i)
            else:
                i+=1

    time.sleep(0.0002)
