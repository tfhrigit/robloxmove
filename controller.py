import pyautogui
import keyboard
import time

class GameController:
    def __init__(self):
        # Configuration
        self.movement_sensitivity = 0.05
        self.mouse_sensitivity = 3.0
        self.gesture_cooldown = 0.2
        
        # State tracking
        self.current_mode = "movement"
        self.active_keys = set()
        self.is_mouse_dragging = False
        self.last_gesture_time = 0
        self.hand_center_x = 0
        self.hand_center_y = 0
        self.reference_x = 0.5
        self.reference_y = 0.5
        
        # Initialize pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
    def handle_gesture(self, gesture, landmarks):
        current_time = time.time()
        
        # Apply cooldown
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return
            
        # Calculate hand center
        self.hand_center_x = sum([lm.x for lm in landmarks]) / len(landmarks)
        self.hand_center_y = sum([lm.y for lm in landmarks]) / len(landmarks)
        
        # Handle different gestures
        if gesture == "fist":
            self.handle_fist()
        elif gesture == "open_hand":
            self.handle_open_hand()
        elif gesture == "thumbs_up":
            self.handle_thumbs_up()
        elif gesture == "two_fingers":
            self.handle_two_fingers()
        elif gesture == "pointing":
            self.handle_pointing()
        elif gesture == "five_fingers":
            self.handle_five_fingers()
        else:
            self.reset_movement()
    
    def handle_fist(self):
        self.current_mode = "mouse"
        self.last_gesture_time = time.time()
        self.reset_movement()
        
        if not self.is_mouse_dragging:
            self.is_mouse_dragging = True
            current_x, current_y = pyautogui.position()
            pyautogui.mouseDown(current_x, current_y)
    
    def handle_open_hand(self):
        self.current_mode = "movement"
        self.last_gesture_time = time.time()
        self.stop_mouse_drag()
        
        # Calculate movement based on hand position
        dx = self.hand_center_x - self.reference_x
        dy = self.hand_center_y - self.reference_y
        
        threshold = 0.08
        
        # Reset movement keys
        self.reset_movement()
        
        # Horizontal movement
        if abs(dx) > threshold:
            if dx > 0:
                keyboard.press('d')
                self.active_keys.add('d')
            else:
                keyboard.press('a')
                self.active_keys.add('a')
        
        # Vertical movement
        if abs(dy) > threshold:
            if dy > 0:
                keyboard.press('s')
                self.active_keys.add('s')
            else:
                keyboard.press('w')
                self.active_keys.add('w')
    
    def handle_thumbs_up(self):
        self.reset_all()
        self.last_gesture_time = time.time()
        keyboard.press_and_release('space')
        time.sleep(0.1)
    
    def handle_two_fingers(self):
        self.reset_all()
        self.last_gesture_time = time.time()
        keyboard.press_and_release('ctrl')
        time.sleep(0.1)
    
    def handle_pointing(self):
        self.reset_all()
        self.last_gesture_time = time.time()
        keyboard.press_and_release('e')
        time.sleep(0.2)
    
    def handle_five_fingers(self):
        self.reset_all()
        self.last_gesture_time = time.time()
        keyboard.press_and_release('i')
        time.sleep(0.3)
    
    def reset_movement(self):
        movement_keys = ['w', 'a', 's', 'd']
        for key in movement_keys:
            if key in self.active_keys:
                keyboard.release(key)
                self.active_keys.discard(key)
    
    def reset_all(self):
        self.reset_movement()
        self.stop_mouse_drag()
    
    def stop_mouse_drag(self):
        if self.is_mouse_dragging:
            self.is_mouse_dragging = False
            pyautogui.mouseUp()
    
    def cleanup(self):
        # Release all active keys
        for key in list(self.active_keys):
            keyboard.release(key)
        
        # Stop mouse drag
        if self.is_mouse_dragging:
            pyautogui.mouseUp()