import math

class HandGestureDetector:

    
    def __init__(self):

        # indeks landmark untuk ujung jari
        self.finger_tip_indices = [4, 8, 12, 16, 20]    # Jempol, Telunjuk, Tengah, Manis, Kelingking
        self.finger_dip_indices = [2, 7, 11, 15, 19]    # Sendi DIP (distal interphalangeal)
        self.finger_pip_indices = [3, 6, 10, 14, 18]    # Sendi PIP (proximal interphalangeal)
        self.finger_mcp_indices = [1, 5, 9, 13, 17]     # Sendi MCP (metacarpophalangeal)
        
    def calculate_distance(self, point1, point2):
        
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_finger_extended(self, landmarks, finger_index):
        # untuk jempol (index 0)
        if finger_index == 0:
            # periksa jarak jempol ke pangkal tangan
            wrist = landmarks[0]  # Pangkal tangan
            thumb_tip = landmarks[self.finger_tip_indices[0]]
            thumb_mcp = landmarks[self.finger_mcp_indices[0]]
            
            # jika ujung jempol lebih jauh dari sendi MCP, maka jempol terulur
            return self.calculate_distance(thumb_tip, wrist) > self.calculate_distance(thumb_mcp, wrist)
        
        # untuk jari lainnya
        else:
            tip = landmarks[self.finger_tip_indices[finger_index]]
            dip = landmarks[self.finger_dip_indices[finger_index]]
            pip = landmarks[self.finger_pip_indices[finger_index]]
            mcp = landmarks[self.finger_mcp_indices[finger_index]]
            
            # Jari dianggap terulur jika:
            # 1. ujung jari lebih tinggi dari sendi DIP
            # 2. ujung jari lebih tinggi dari sendi PIP
            # 3. sendi PIP lebih tinggi dari sendi MCP (untuk memastikan jari tidak tertekuk)
            return (tip.y < dip.y and 
                   tip.y < pip.y and 
                   pip.y < mcp.y)
    
    def count_extended_fingers(self, landmarks):
        count = 0
        for i in range(5):  # 5 jari
            if self.is_finger_extended(landmarks, i):
                count += 1
        return count
    
    def detect_gesture(self, landmarks):
        # hitung jumlah jari yang terulur
        extended_fingers = self.count_extended_fingers(landmarks)
        
        # deteksi gesture berdasarkan jumlah dan konfigurasi jari
        if extended_fingers == 0:
            # semua jari tertutup - tangan mengepal
            return "fist"
            
        elif extended_fingers == 1:
            # hanya satu jari terulur
            if self.is_finger_extended(landmarks, 0):  # jempol
                return "thumbs_up"
            elif self.is_finger_extended(landmarks, 1):  # telunjuk
                return "pointing"
            else:
                return "unknown_single"
                
        elif extended_fingers == 2:
            # dua jari terulur
            if (self.is_finger_extended(landmarks, 1) and  # telunjuk
                self.is_finger_extended(landmarks, 2)):    # jari tengah
                return "two_fingers"
            else:
                return "unknown_two"
                
        elif extended_fingers == 5:
            # semua jari terulur - tangan terbuka penuh
            return "open_hand"
            
        else:
            # gesture lainnya
            return "unknown"