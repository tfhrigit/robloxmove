import cv2
import mediapipe as mp
import numpy as np
from gestures import HandGestureDetector
from controller import GameController

class HandControlApplication:   
    def __init__(self):
        # inisialisasi mediapipe tangan
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # konfig deteksi tangan
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # inisialisasi komponen pendukung
        self.gesture_detector = HandGestureDetector()
        self.game_controller = GameController()
        
        # setup kamera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # variabel untuk tracking gesture
        self.current_gesture = "none"
        self.previous_gesture = "none"
        self.gesture_stability_counter = 0
        self.stability_threshold = 3  # Jumlah frame untuk konfirmasi gesture
        
    def process_frame(self, frame):
        # konversi warna BGR ke RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        
        # deteksi tangan
        results = self.hands.process(rgb_frame)
        
        # konversi kembali ke BGR untuk display
        rgb_frame.flags.writeable = True
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        # reset gesture
        self.current_gesture = "none"
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # gambar landmark tangan
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # hitung bounding box
                h, w, _ = frame.shape
                x_coords = [lm.x for lm in hand_landmarks.landmark]
                y_coords = [lm.y for lm in hand_landmarks.landmark]
                x_min, x_max = int(min(x_coords) * w), int(max(x_coords) * w)
                y_min, y_max = int(min(y_coords) * h), int(max(y_coords) * h)
                
                # gambar bounding box
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                
                # deteksi gesture
                self.current_gesture = self.gesture_detector.detect_gesture(hand_landmarks.landmark)
                
                # stabilisasi deteksi gesture
                if self.current_gesture == self.previous_gesture:
                    self.gesture_stability_counter += 1
                else:
                    self.gesture_stability_counter = 0
                    self.previous_gesture = self.current_gesture
                
                # gunakan gesture yang stabil
                if self.gesture_stability_counter >= self.stability_threshold:
                    stable_gesture = self.current_gesture
                else:
                    stable_gesture = "none"
                
                # kontrol game berdasarkan gesture
                self.game_controller.handle_gesture(stable_gesture, hand_landmarks.landmark)
                
                # tampilkan informasi bounding box
                bbox_width = x_max - x_min
                bbox_height = y_max - y_min
                cv2.putText(frame, f"size: {bbox_width}x{bbox_height}", 
                           (x_min, y_max + 20), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 0), 1)
        
        return frame
    
    def display_interface(self, frame):
        # Tam
        # tampilkan informasi gesture
        cv2.putText(frame, f"gesture: {self.previous_gesture}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # tampilkan mode kontrol
        cv2.putText(frame, f"mode: {self.game_controller.current_mode}", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # tampilkan petunjuk
        cv2.putText(frame, "tekan 'q' untuk keluar", 
                   (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 1)
        
        return frame
    
    def run(self):
        """
        menjalankan aplikasi utama
        """
        print("=== sistem kontrol roblox pake gesture tangan ===")
        print("gesture yang tersedia:")
        print("- tangan terbuka: gerakan WASD")
        print("- tangan mengepal: kontrol kamera (mouse drag)")
        print("- jempol ke atas: lompat (space)")
        print("- dua jari (peace): jongkok (ctrl)")
        print("- telunjuk menunjuk: interaksi (E)")
        print("- lima jari terbuka: buka inventory (I)")
        print("tekan 'q' untuk keluar")
        print("=" * 50)
        
        try:
            while True:
                # baca frame dari kamera
                success, frame = self.cap.read()
                if not success:
                    print("Gagal membaca frame dari kamera")
                    break
                
                # flip frame untuk efek mirror
                frame = cv2.flip(frame, 1)
                
                # proses frame
                processed_frame = self.process_frame(frame)
                
                # tampilkan antarmuka
                display_frame = self.display_interface(processed_frame)
                
                # tampilkan frame
                cv2.imshow('kontrol roblox dengan gestur tangan', display_frame)
                
                # keluar dengan tombol 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\naplikasi dihentikan oleh pengguna")
        except Exception as e:
            print(f"terjadi kesalahan: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        membersihkan resource yang digunakan
        """
        print("membersihkan resource...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.game_controller.cleanup()
        print("aplikasi telah ditutup")

def main():
    """
    fungsi utama 
    """
    app = HandControlApplication()
    app.run()

if __name__ == "__main__":
    main()