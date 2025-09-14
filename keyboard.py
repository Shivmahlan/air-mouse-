import cv2
import mediapipe as mp
import numpy as np
import time


class VirtualKeyboard:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Keyboard layout
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['SPACE', 'BACKSPACE']
        ]

        # Key dimensions and positions
        self.key_width = 45
        self.key_height = 45
        self.key_margin = 5
        self.start_x = 20
        self.start_y = 300

        # Text variables
        self.typed_text = ""
        self.last_key_time = 0
        self.key_delay = 0.3  # Reduced delay between key presses
        self.is_pressing = False  # Track if currently pressing

        # Create key rectangles
        self.key_rects = {}
        self.create_key_layout()

    def create_key_layout(self):
        """Create rectangles for each key"""
        y_offset = 0

        for row_idx, row in enumerate(self.keys):
            x_offset = 0

            # Center the row
            if row_idx == 1:  # ASDF row
                x_offset = 30
            elif row_idx == 2:  # ZXCV row
                x_offset = 60

            for key in row:
                x = self.start_x + x_offset
                y = self.start_y + y_offset

                # Special handling for space and backspace
                if key == 'SPACE':
                    width = 150
                elif key == 'BACKSPACE':
                    width = 90
                else:
                    width = self.key_width

                self.key_rects[key] = {
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': self.key_height
                }

                x_offset += width + self.key_margin

            y_offset += self.key_height + self.key_margin

    def draw_keyboard(self, img):
        """Draw the virtual keyboard on the image"""
        for key, rect in self.key_rects.items():
            x, y, w, h = rect['x'], rect['y'], rect['width'], rect['height']

            # Draw key background
            cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 50), -1)
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)

            # Draw key text
            text = key if key not in ['SPACE', 'BACKSPACE'] else ('SPC' if key == 'SPACE' else 'BACK')
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def highlight_key(self, img, key):
        """Highlight a key when finger is over it"""
        if key in self.key_rects:
            rect = self.key_rects[key]
            x, y, w, h = rect['x'], rect['y'], rect['width'], rect['height']
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), -1)
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)

            # Draw key text
            text = key if key not in ['SPACE', 'BACKSPACE'] else ('SPC' if key == 'SPACE' else 'BACK')
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    def get_key_at_position(self, x, y):
        """Get the key at the given position"""
        for key, rect in self.key_rects.items():
            if (rect['x'] <= x <= rect['x'] + rect['width'] and
                    rect['y'] <= y <= rect['y'] + rect['height']):
                return key
        return None

    def is_finger_up(self, landmarks):
        """Check if index finger is up (pointing gesture)"""
        # Index finger tip and PIP joint
        tip = landmarks[8]  # Index finger tip
        pip = landmarks[6]  # Index finger PIP joint

        # Check if tip is above PIP (finger pointing up)
        return tip.y < pip.y

    def get_finger_distance(self, landmarks):
        """Calculate distance between index finger tip and thumb tip"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        # Calculate Euclidean distance
        distance = np.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
        return distance

    def is_pinching(self, landmarks):
        """Better pinch detection using multiple finger positions"""
        # Get landmarks for thumb and index finger
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        index_pip = landmarks[6]

        # Calculate distance between thumb tip and index tip
        tip_distance = np.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)

        # Calculate distance between thumb and index at joint level for reference
        joint_distance = np.sqrt((thumb_ip.x - index_pip.x) ** 2 + (thumb_ip.y - index_pip.y) ** 2)

        # Pinch detected when tips are close relative to joint distance
        pinch_ratio = tip_distance / joint_distance if joint_distance > 0 else 1

        return pinch_ratio < 0.3  # Threshold for pinch detection

    def process_key_press(self, key):
        """Process a key press"""
        current_time = time.time()

        # Check if enough time has passed since last key press
        if current_time - self.last_key_time < self.key_delay:
            return False

        if key == 'SPACE':
            self.typed_text += ' '
        elif key == 'BACKSPACE':
            self.typed_text = self.typed_text[:-1]
        else:
            self.typed_text += key.lower()

        self.last_key_time = current_time
        return True

    def run(self):
        """Main loop for the virtual keyboard"""
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera")
            return

        print("Virtual Keyboard Controls:")
        print("- Point with your index finger to hover over keys")
        print("- Pinch (bring thumb and index finger close) to press a key")
        print("- Press 'q' to quit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame
            results = self.hands.process(rgb_frame)

            # Draw keyboard
            self.draw_keyboard(frame)

            # Draw typed text
            text_bg_height = 80
            cv2.rectangle(frame, (20, 20), (w - 20, 20 + text_bg_height), (0, 0, 0), -1)
            cv2.rectangle(frame, (20, 20), (w - 20, 20 + text_bg_height), (255, 255, 255), 2)

            # Split text into lines if too long
            max_chars_per_line = 50
            display_text = self.typed_text
            if len(display_text) > max_chars_per_line:
                display_text = "..." + display_text[-(max_chars_per_line - 3):]

            cv2.putText(frame, f"Text: {display_text}", (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            current_key = None

            # Process hand landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    # Get index finger tip position
                    index_tip = hand_landmarks.landmark[8]
                    finger_x = int(index_tip.x * w)
                    finger_y = int(index_tip.y * h)

                    # Draw finger position
                    cv2.circle(frame, (finger_x, finger_y), 10, (255, 0, 0), -1)

                    # Check if finger is over a key
                    current_key = self.get_key_at_position(finger_x, finger_y)

                    if current_key:
                        # Highlight the key
                        self.highlight_key(frame, current_key)

                        # Check for pinch gesture (key press)
                        is_pinching = self.is_pinching(hand_landmarks.landmark)

                        # Visual feedback for pinch detection
                        pinch_color = (0, 255, 0) if is_pinching else (255, 0, 0)
                        cv2.circle(frame, (finger_x, finger_y), 15, pinch_color, 3)

                        # If pinching and not already pressing, press the key
                        if is_pinching and not self.is_pressing:
                            if self.process_key_press(current_key):
                                cv2.putText(frame, f"PRESSED: {current_key}", (finger_x - 60, finger_y - 40),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            self.is_pressing = True
                        elif not is_pinching:
                            self.is_pressing = False
                    else:
                        # Reset pressing state when not over any key
                        self.is_pressing = False

            # Show instructions
            instructions = [
                "Point to hover over keys",
                "Pinch (thumb + index) to press",
                "Green circle = pinching detected"
            ]

            for i, instruction in enumerate(instructions):
                y_pos = h - 80 + (i * 25)
                cv2.putText(frame, instruction, (20, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Display the frame
            cv2.imshow('Virtual Keyboard', frame)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    keyboard = VirtualKeyboard()
    keyboard.run()