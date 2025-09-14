import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
drawing_utils = mp.solutions.drawing_utils

# Screen info
screen_width, screen_height = pyautogui.size()
frame_width, frame_height = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

# Smoothing for cursor
smooth_x, smooth_y = 0, 0
SMOOTHING_FACTOR = 0.7

# Gesture state
prev_click_time = 0
prev_scroll_time = 0
prev_y = None

# Create window and set always on top
window_name = "Virtual Mouse"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hands.process(rgb_frame)
    hands_landmarks = output.multi_hand_landmarks

    if hands_landmarks:
        for hand in hands_landmarks:
            drawing_utils.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            landmarks = hand.landmark

            # Extract key points
            index = [int(landmarks[8].x * frame_width), int(landmarks[8].y * frame_height)]
            thumb = [int(landmarks[4].x * frame_width), int(landmarks[4].y * frame_height)]
            middle = [int(landmarks[12].x * frame_width), int(landmarks[12].y * frame_height)]
            wrist = [int(landmarks[0].x * frame_width), int(landmarks[0].y * frame_height)]

            # Cursor movement (index)
            screen_x = landmarks[8].x * screen_width
            screen_y = landmarks[8].y * screen_height
            smooth_x = SMOOTHING_FACTOR * smooth_x + (1 - SMOOTHING_FACTOR) * screen_x
            smooth_y = SMOOTHING_FACTOR * smooth_y + (1 - SMOOTHING_FACTOR) * screen_y
            pyautogui.moveTo(smooth_x, smooth_y, _pause=False)

            # Left click (index close to thumb)
            if distance(index, thumb) < 25:
                current_time = cv2.getTickCount() / cv2.getTickFrequency()
                if current_time - prev_click_time > 0.5:  # Debounce
                    pyautogui.click()
                    prev_click_time = current_time

            # Right click (middle close to thumb)
            if distance(middle, thumb) < 25:
                current_time = cv2.getTickCount() / cv2.getTickFrequency()
                if current_time - prev_click_time > 0.5:  # Debounce
                    pyautogui.rightClick()
                    prev_click_time = current_time

            # Double click (custom gesture: index and thumb open/close rapidly, or use a flag)
            # Here, double click if index and thumb are close twice in a short time
            # (For simplicity, just show the idea; you may need to track state)
            # For robust double click, track gesture state and timing

            # Smooth scrolling (pinch-and-move or index-middle spread)
            # Option 1: Pinch-and-move (thumb and index close, move up/down)
            if distance(index, thumb) < 25:
                if prev_y is not None:
                    if index[1] < prev_y - 5:  # Finger moved up
                        pyautogui.scroll(10)
                    elif index[1] > prev_y + 5:  # Finger moved down
                        pyautogui.scroll(-10)
                prev_y = index[1]
            else:
                prev_y = None

            # Option 2: Index and middle spread (for horizontal scroll)
            # if distance(index, middle) > 50:
            #     if index[0] > middle[0]:
            #         pyautogui.hscroll(10)
            #     else:
            #         pyautogui.hscroll(-10)

    # FPS counter
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    timer = cv2.getTickCount()

    # Show frame
    cv2.imshow(window_name, frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
