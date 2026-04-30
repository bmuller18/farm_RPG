import time
from crops import Crop

wheath = Crop("Trigo", 5, 10)

wheath.plant()

while True:
    if wheath.is_ready():
        wheath.harvest()
        break
    else:
        print("Faltan: ", wheath.time_remaining())

    time.sleep(1)