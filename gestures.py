import math

class HandGestureDetector:
    def __init__(self):
        # Indices for finger landmarks
        self.thumb_tip = 4
        self.index_tip = 8
        self.middle_tip = 12
        self.ring_tip = 16
        self.pinky_tip = 20
        
        self.thumb_ip = 3
        self.index_dip = 7
        self.middle_dip = 11
        self.ring_dip = 15
        self.pinky_dip = 19
        
        self.wrist = 0
        
    def calculate_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_finger_extended(self, landmarks, finger_tip, finger_dip=None):
        if finger_tip == self.thumb_tip:
            # Special case for thumb
            wrist = landmarks[self.wrist]
            thumb_tip = landmarks[self.thumb_tip]
            thumb_ip = landmarks[self.thumb_ip]
            return self.calculate_distance(thumb_tip, wrist) > self.calculate_distance(thumb_ip, wrist)
        else:
            # For other fingers
            tip = landmarks[finger_tip]
            dip = landmarks[finger_dip] if finger_dip else landmarks[finger_tip - 2]
            return tip.y < dip.y - 0.05  # Add threshold for better detection
    
    def count_extended_fingers(self, landmarks):
        count = 0
        # Check each finger
        if self.is_finger_extended(landmarks, self.thumb_tip):
            count += 1
        if self.is_finger_extended(landmarks, self.index_tip, self.index_dip):
            count += 1
        if self.is_finger_extended(landmarks, self.middle_tip, self.middle_dip):
            count += 1
        if self.is_finger_extended(landmarks, self.ring_tip, self.ring_dip):
            count += 1
        if self.is_finger_extended(landmarks, self.pinky_tip, self.pinky_dip):
            count += 1
        return count
    
    def detect_gesture(self, landmarks):
        extended_fingers = self.count_extended_fingers(landmarks)
        
        # Fist - no fingers extended
        if extended_fingers == 0:
            return "fist"
        
        # Thumbs up - only thumb extended
        elif extended_fingers == 1 and self.is_finger_extended(landmarks, self.thumb_tip):
            return "thumbs_up"
        
        # Pointing - only index finger extended
        elif extended_fingers == 1 and self.is_finger_extended(landmarks, self.index_tip, self.index_dip):
            return "pointing"
        
        # Two fingers (peace sign) - index and middle extended
        elif (extended_fingers == 2 and 
              self.is_finger_extended(landmarks, self.index_tip, self.index_dip) and
              self.is_finger_extended(landmarks, self.middle_tip, self.middle_dip)):
            return "two_fingers"
        
        # Open hand - most fingers extended
        elif extended_fingers >= 4:
            return "open_hand"
        
        # Five fingers - all extended
        elif extended_fingers == 5:
            return "five_fingers"
        
        return "none"