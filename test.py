from config import Config
from tracker import WindowTracker
import time

config = Config()
tracker = WindowTracker(config)

print("Calling tracker.start()...")
tracker.start()
print("Tracker.start() returned")

print("Tracking for 30 seconds...")
time.sleep(30)

print("Calling tracker.stop()...")
tracker.stop()