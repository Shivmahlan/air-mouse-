import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Setup
cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.8)
draw = mp.solutions.drawing_utils

keyboard_open = False
selected_key = None
key_last_pressed_time = 0

# QWERTY 60% layout
keys = [
    ['1','2','3','4','5','6','7','8','9','0','-','='],
    ['Q','W','E','R','T','Y','U','I','O','P','[',']'],
    ['A','S','D','F','G','H','J','K','L',';','\''],
    ['Z','X','C','V','B','N','M',',','.','/'],
    ['Space','Back','Enter']
]

key_rects = []
key_w, key_h = 50, 50
keyboard_x, keyboard_y = 10, 40  # adjust as needed

def draw_keyboard(img):
    key_rects.clear()
    y_offset = keyboard_y
    for i, row in enumerate(keys):
        x_offset = keyboard_x
        for key in row:
            w = key_w * 2 if key in ['Space'] else key_w
            cv2.rectangle(img, (x_offset, y_offset), (x_offset+w, y_offset+key_h), (255 - 40*i, 100 + 30*i, 150), -1)
            cv2.putText(img, key, (x_offset+10, y_offset+40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
            key_rects.append((key, x_offset, y_offset, x_offset + w, y_offset + key_h))
            x_offset += w + 10
        y_offset += key_h + 10

def check_key_press(x, y):
    global selected_key, key_last_pressed_time
    current_time = time.time()
    for key, x1, y1, x2, y2 in key_rects:
        if x1 < x < x2 and y1 < y < y2:
            if selected_key != key or current_time - key_last_pressed_time > 0.5:
                if key == 'Space':
                    pyautogui.press('space')
                elif key == 'Back':
                    pyautogui.press('backspace')
                elif key == 'Enter':
                    pyautogui.press('enter')
                else:
                    pyautogui.press(key.lower())
                selected_key = key
                key_last_pressed_time = current_time
            return
    selected_key = None

def detect_handedness(results):
    hand_map = {}
    if results.multi_handedness:
        for i, hand in enumerate(results.multi_handedness):
            label = hand.classification[0].label
            hand_map[label] = i
    return hand_map

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    hand_indices = detect_handedness(results)
    index_fingers = {}

    if results.multi_hand_landmarks:
        for label, i in hand_indices.items():
            hand = results.multi_hand_landmarks[i]
            draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            index = hand.landmark[8]
            ix = int(index.x * frame_w)
            iy = int(index.y * frame_h)
            index_fingers[label] = (ix, iy)

            if label == 'Right':
                screen_x = int(index.x * screen_width)
                screen_y = int(index.y * screen_height)
                pyautogui.moveTo(screen_x, screen_y, duration=0.01)
            elif label == 'Left':
                middle = hand.landmark[12]
                my = int(middle.y * frame_h)
                if abs(iy - my) > 40:
                    pyautogui.scroll(50 if iy < my else -50)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('k'):
        keyboard_open = not keyboard_open
        time.sleep(0.3)

    if keyboard_open:
        draw_keyboard(frame)
        for pos in index_fingers.values():
            x, y = pos
            cv2.circle(frame, (x, y), 10, (255, 255, 255), -1)
            check_key_press(x, y)

    cv2.namedWindow("Gesture Controller", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Gesture Controller", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Gesture Controller", frame)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
