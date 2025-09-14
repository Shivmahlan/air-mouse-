import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import os
import platform

# === Constants ===
CLICK_THRESHOLD_PIXELS = 25
SCROLL_THRESHOLD_NORM = 0.05
HAND_DISTANCE_THRESHOLD = 50
CURSOR_SMOOTHING_ALPHA = 0.5
CURSOR_MOVE_DURATION = 0.01

# === Global State ===
prev_x, prev_y = 0, 0
osk_launched = False
index_fingers = {}
pyautogui.FAILSAFE = True

# === Init Camera ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("No camera found")
screen_width, screen_height = pyautogui.size()

# === MediaPipe Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
draw = mp.solutions.drawing_utils


# === Utility Functions ===

def detect_handedness(results):
    """Returns a map of hand label to index in multi_hand_landmarks"""
    hand_map = {}
    if results.multi_handedness:
        for i, hand in enumerate(results.multi_handedness):
            label = hand.classification[0].label  # 'Left' or 'Right'
            hand_map[label] = i
    return hand_map


def smooth_cursor(x, y):
    """Applies smoothing to cursor movement"""
    global prev_x, prev_y
    smooth_x = CURSOR_SMOOTHING_ALPHA * x + (1 - CURSOR_SMOOTHING_ALPHA) * prev_x
    smooth_y = CURSOR_SMOOTHING_ALPHA * y + (1 - CURSOR_SMOOTHING_ALPHA) * prev_y
    prev_x, prev_y = smooth_x, smooth_y
    return int(smooth_x), int(smooth_y)


def launch_osk():
    """Toggle On-Screen Keyboard (Windows only)"""
    global osk_launched
    if platform.system() != "Windows":
        print("On-screen keyboard toggle only supported on Windows.")
        return

    if not osk_launched:
        os.system("start osk")
    else:
        os.system("taskkill /IM osk.exe /F")
    osk_launched = not osk_launched
    time.sleep(0.5)


def euclidean(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def process_right_hand(hand, frame_w, frame_h):
    """Handles cursor and click actions for the right hand"""
    index = hand.landmark[8]
    thumb = hand.landmark[4]
    middle = hand.landmark[12]

    ix, iy = int(index.x * frame_w), int(index.y * frame_h)
    screen_x = int(index.x * screen_width)
    screen_y = int(index.y * screen_height)

    # Move cursor
    try:
        smooth_x, smooth_y = smooth_cursor(screen_x, screen_y)
        pyautogui.moveTo(smooth_x, smooth_y, duration=CURSOR_MOVE_DURATION)
    except Exception as e:
        print(f"[Cursor] Move failed: {e}")

    # Click detection (thumb + index = left click)
    click_dist = euclidean((ix, iy), (int(thumb.x * frame_w), int(thumb.y * frame_h)))
    if click_dist < CLICK_THRESHOLD_PIXELS:
        try:
            pyautogui.click()
            time.sleep(0.2)
        except Exception as e:
            print(f"[Click] Error: {e}")

    # Optional: Right-click via middle + thumb
    m_dist = euclidean((int(middle.x * frame_w), int(middle.y * frame_h)),
                       (int(thumb.x * frame_w), int(thumb.y * frame_h)))
    if m_dist < CLICK_THRESHOLD_PIXELS:
        try:
            pyautogui.rightClick()
            time.sleep(0.2)
        except Exception as e:
            print(f"[Right Click] Error: {e}")


def process_left_hand(hand):
    """Handles scroll and navigation for the left hand"""
    thumb = hand.landmark[4]
    index = hand.landmark[8]
    middle = hand.landmark[12]
    ring = hand.landmark[16]
    pinky = hand.landmark[20]

    def norm_dist(a, b):
        return np.linalg.norm(np.array([a.x - b.x, a.y - b.y]))

    try:
        if norm_dist(thumb, middle) < SCROLL_THRESHOLD_NORM:
            pyautogui.scroll(30)
        elif norm_dist(thumb, index) < SCROLL_THRESHOLD_NORM:
            pyautogui.scroll(-30)
        elif norm_dist(thumb, ring) < SCROLL_THRESHOLD_NORM:
            pyautogui.hotkey('alt', 'left')
        elif norm_dist(thumb, pinky) < SCROLL_THRESHOLD_NORM:
            pyautogui.hotkey('alt', 'right')
    except Exception as e:
        print(f"[Scroll/Nav] Error: {e}")


# === Main Loop ===
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_h, frame_w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)
        hand_indices = detect_handedness(results)
        index_fingers.clear()

        if results.multi_hand_landmarks:
            for label, idx in hand_indices.items():
                hand = results.multi_hand_landmarks[idx]
                draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                index = hand.landmark[8]
                index_fingers[label] = (int(index.x * frame_w), int(index.y * frame_h))

                if label == 'Right':
                    process_right_hand(hand, frame_w, frame_h)
                elif label == 'Left':
                    process_left_hand(hand)

        # Toggle OSK if both hands are close
        if 'Left' in index_fingers and 'Right' in index_fingers:
            lx, ly = index_fingers['Left']
            rx, ry = index_fingers['Right']
            if euclidean((lx, ly), (rx, ry)) < HAND_DISTANCE_THRESHOLD:
                launch_osk()

        # Display
        cv2.namedWindow("Gesture Controller", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Gesture Controller", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Gesture Controller", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"[Error] Main loop exception: {e}")

finally:
    cap.release()
    cv2.destroyAllWindows()
