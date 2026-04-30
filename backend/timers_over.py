from datetime import datetime, timedelta
import time

start_action = datetime.now().second

def corn_harvest(corn_time):
    time_now = datetime.now()

    if time_now - start_action >= timedelta(seconds=corn_harvest):
        print("Corn waws harveted")

while True:
    if corn_harvest(5):
        break
    time.sleep(1)