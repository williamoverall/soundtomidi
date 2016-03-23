import time
import threading
import soundtomidi
options = soundtomidi.Options()
process_audio = soundtomidi.ProcessAudio(options)
thread = threading.Thread(target=process_audio.start)
thread.daemon = True
thread.start()
while True:
    print("Doing some other stuff")
    time.sleep(1)