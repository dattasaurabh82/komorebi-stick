import board
import digitalio
import threading
import time

class Button:
    def __init__(self, pin, debounce_time=0.01, long_press_time=5):
        self.pin = getattr(board, f'D{pin}')
        self.button = digitalio.DigitalInOut(self.pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        
        self.debounce_time = debounce_time
        self.long_press_time = long_press_time
        
        self.last_state = self.button.value
        self.last_change_time = time.monotonic()
        self.press_start_time = None
        
        self.on_short_press = None
        self.on_long_press = None
        
        self.thread = threading.Thread(target=self._check_button, daemon=True)
        self.thread.start()

    def _check_button(self):
        while True:
            current_state = self.button.value
            current_time = time.monotonic()
            
            if current_state != self.last_state and (current_time - self.last_change_time) > self.debounce_time:
                # Button released
                if current_state:
                    if self.press_start_time:
                        press_duration = current_time - self.press_start_time
                        if press_duration >= self.long_press_time:
                            if self.on_long_press:
                                self.on_long_press()
                        else:
                            if self.on_short_press:
                                self.on_short_press()
                        self.press_start_time = None
                # Button pressed
                else:
                    self.press_start_time = current_time
                
                self.last_state = current_state
                self.last_change_time = current_time
            
            # Check every 1 ms
            time.sleep(0.001)  