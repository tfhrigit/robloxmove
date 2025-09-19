import pyautogui
import keyboard
import time
import threading

class GameController:

    
    def __init__(self):

        # parameter sensitivitas
        self.movement_sensitivity = 0.03    # sensitivitas gerakan WASD
        self.mouse_sensitivity = 2.0        # sensitivitas kontrol mouse
        self.gesture_hold_time = 0.1        # waktu tahan untuk aksi berkelanjutan
        
        # state kontrol
        self.current_mode = "movement"      # mode: "movement" atau "mouse"
        self.active_keys = set()            # key yang sedang ditekan
        self.is_mouse_dragging = False      # status drag mouse
        self.last_gesture_time = 0          # waktu gesture terakhir
        self.gesture_cooldown = 0.3         # jeda antar gesture
        
        # referensi posisi untuk gerakan
        self.reference_x = 0.5              # posisi referensi X tengah
        self.reference_y = 0.5              # posisi referensi Y tengah
        self.hand_center_x = 0              # posisi X tangan saat ini
        self.hand_center_y = 0              # posisi Y tangan saat ini
        
        # inisialisasi pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0  # tidak ada jeda otomatis
        
        # flag untuk thread cleanup
        self.cleanup_flag = False
        
    def handle_gesture(self, gesture, landmarks):

        current_time = time.time()
        
        # hitung posisi tengah tangan
        self.hand_center_x = sum([lm.x for lm in landmarks]) / len(landmarks)
        self.hand_center_y = sum([lm.y for lm in landmarks]) / len(landmarks)
        
        # terapkan cooldown untuk mencegah gesture spam
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return

        if gesture == "fist":
            self._handle_fist_gesture()
        elif gesture == "open_hand":
            self._handle_open_hand_gesture()
        elif gesture == "thumbs_up":
            self._handle_thumbs_up_gesture()
        elif gesture == "two_fingers":
            self._handle_two_fingers_gesture()
        elif gesture == "pointing":
            self._handle_pointing_gesture()
        else:
            self._reset_controls()
    
    def _handle_fist_gesture(self):

        self.current_mode = "mouse"
        self.last_gesture_time = time.time()
        
        # mulai mouse drag jika belum aktif
        if not self.is_mouse_dragging:
            self.is_mouse_dragging = True
            current_x, current_y = pyautogui.position()
            pyautogui.mouseDown(current_x, current_y)
    
    def _handle_open_hand_gesture(self):

        self.current_mode = "movement"
        self.last_gesture_time = time.time()
        
        # hentikan mouse drag jika aktif
        self._stop_mouse_drag()
        
        # hitung pergerakan berdasarkan posisi tangan
        dx = self.hand_center_x - self.reference_x
        dy = self.hand_center_y - self.reference_y
        
        # threshold untuk mencegah gerakan yang terlalu sensitif
        threshold = 0.05
        
        # reset key gerakan
        self._release_movement_keys()
        
        # gerakan horizontal (A/D)
        if abs(dx) > threshold:
            if dx > 0:
                keyboard.press('d')
                self.active_keys.add('d')
            else:
                keyboard.press('a')
                self.active_keys.add('a')
        
        # gerakan vertikal (W/S)
        if abs(dy) > threshold:
            if dy > 0:
                keyboard.press('s')
                self.active_keys.add('s')
            else:
                keyboard.press('w')
                self.active_keys.add('w')
    
    def _handle_thumbs_up_gesture(self):

        self._reset_controls()
        self.last_gesture_time = time.time()
        
        # tekan dan lepaskan tombol spasi
        keyboard.press_and_release('space')
        time.sleep(0.1)  # jeda kecil untuk mencegah spam
    
    def _handle_two_fingers_gesture(self):

        self._reset_controls()
        self.last_gesture_time = time.time()
        
        # tekan tombol Ctrl
        keyboard.press('ctrl')
        time.sleep(0.2)  # tahan sebentar
        
        # lepaskan setelah jeda
        keyboard.release('ctrl')
    
    def _handle_pointing_gesture(self):

        self._reset_controls()
        self.last_gesture_time = time.time()
        
        # tekan dan lepaskan tombol E
        keyboard.press_and_release('e')
        time.sleep(0.3)  # jeda lebih lama untuk mencegah spam
    
    def _handle_five_fingers_gesture(self):
    
        self._reset_controls()
        self.last_gesture_time = time.time()
        
        # tekan dan lepaskan tombol I
        keyboard.press_and_release('i')
        time.sleep(0.5)  # jeda panjang untuk mencegah spam
    
    def _reset_controls(self):

        self._release_movement_keys()
        self._stop_mouse_drag()
    
    def _release_movement_keys(self):

        movement_keys = ['w', 'a', 's', 'd']
        for key in movement_keys:
            if key in self.active_keys:
                keyboard.release(key)
                self.active_keys.discard(key)
    
    def _stop_mouse_drag(self):

        if self.is_mouse_dragging:
            self.is_mouse_dragging = False
            pyautogui.mouseUp()
    
    def cleanup(self):
    
        print("membersihkan kontrol game...")
        
        # lepaskan semua key yang sedang ditekan
        for key in list(self.active_keys):
            keyboard.release(key)
        
        # hentikan mouse drag
        if self.is_mouse_dragging:
            pyautogui.mouseUp()
        
        # set flag cleanup
        self.cleanup_flag = True
        
        print("kontrol game telah dibersihkan")