import cv2
import mediapipe as mp
from gestures import HandGestureDetector
from controller import GameController
import time

class HandControlApp:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Initialize components
        self.gesture_detector = HandGestureDetector()
        self.controller = GameController()
        
        # Video capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Variables for gesture tracking
        self.last_gesture = "none"
        self.gesture_stable_count = 0
        self.stability_threshold = 2
        
    def run(self):
        print("Hand Control for Roblox Started!")
        print("Controls:")
        print("- Open hand + move: WASD movement")
        print("- Fist: Mouse control mode")
        print("- Thumbs up: Jump (Space)")
        print("- Two fingers: Crouch (Ctrl)")
        print("- Index finger: Interact (E)")
        print("- Five fingers: Inventory (I)")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            gesture = "none"
            hand_landmarks = None
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Draw bounding box
                h, w, _ = frame.shape
                x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))
                
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                
                # Detect gesture
                gesture = self.gesture_detector.detect_gesture(hand_landmarks.landmark)
                
                # Stabilize gesture detection
                if gesture == self.last_gesture:
                    self.gesture_stable_count += 1
                else:
                    self.gesture_stable_count = 0
                    self.last_gesture = gesture
                
                # Use stable gesture
                if self.gesture_stable_count >= self.stability_threshold:
                    stable_gesture = gesture
                else:
                    stable_gesture = "none"
                
                # Control game based on gesture
                self.controller.handle_gesture(stable_gesture, hand_landmarks.landmark)
            
            # Display gesture info
            cv2.putText(frame, f"Gesture: {self.last_gesture}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Mode: {self.controller.current_mode}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Show frame
            cv2.imshow('Hand Control for Roblox', frame)
            
            # Break on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cleanup()
        
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.controller.cleanup()

if __name__ == "__main__":
    app = HandControlApp()
    app.run()