import threading
import os
from time import sleep

def infinity():
    while True:
        pass

threading.Thread(target=infinity).start()

MIN_PID = os.getpid()
print("Sleeping check PID: " + str(MIN_PID))
print(os.system("pgrep python3 | awk '$1>=" + str(MIN_PID)  + "'"))

sleep(5)

# Nuclear launch codes
print("Launching nukes...")
os.system("kill -9 $(pgrep python3 | awk '$1>=" + str(MIN_PID)  + "')")