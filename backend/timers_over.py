from datetime import datetime, timedelta
import time

start_time = datetime.now()
temporizador = 15

while True:
    now_time = datetime.now()

    if now_time - start_time >= timedelta(seconds=temporizador):
        print("Pasaron 15 segundos:")
        break

    time.sleep(1)