import RPi.GPIO as GPIO
import threading, time

class Led:
    def __init__(self, pin):
        self._blinking = False
        self._thread   = None
        self._pin = pin
        self._lock =  threading.Lock()

        GPIO.setup(self._pin, GPIO.OUT)

    def _blink(self, frequency):
        while self._blinking:
            with self._lock:
                GPIO.output(self._pin,True)
                time.sleep(frequency);
                GPIO.output(self._pin,False)
                time.sleep(frequency)

    '''
    '   Blink the Led
    '   Frequency expressed in s, default to 1s
    '''
    def start_blinking(self, frequency=1):
        self._blinking = True
        self._thread = threading.Thread(target=self._blink, args=[frequency])
        self._thread.start()

    def stop_blinking(self):
        self._blinking = False

    def isBlinking(self):
        return self._blinking

    def off(self):
        if self.isBlinking():
            self.stop_blinking()

        with self._lock:
            GPIO.output(self._pin,False)

    def on(self):
        if self.isBlinking():
            self.stop_blinking()

        with self._lock:
            GPIO.output(self._pin,True)
