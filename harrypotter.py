import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import os

pyautogui.FAILSAFE = True

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("No camera found")

screen_width, screen_height = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
draw = mp.solutions.drawing_utils

CLICK_THRESHOLD = 25
prev_x, prev_y = 0, 0
alpha = 0.5
osk_launched = False
index_fingers = {}


def detect_handedness(results):
    hand_map = {}
    if results.multi_handedness:
        for i, hand in enumerate(results.multi_handedness):
            label = hand.classification[0].label
            hand_map[label] = i
    return hand_map


def smooth_cursor(x, y):
    global prev_x, prev_y
    smooth_x = alpha * x + (1 - alpha) * prev_x
    smooth_y = alpha * y + (1 - alpha) * prev_y
    prev_x, prev_y = smooth_x, smooth_y
    return int(smooth_x), int(smooth_y)


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
            for label, i in hand_indices.items():
                hand = results.multi_hand_landmarks[i]
                draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                index = hand.landmark[8]
                ix = int(index.x * frame_w)
                iy = int(index.y * frame_h)
                index_fingers[label] = (ix, iy)

                thumb = hand.landmark[4]
                middle = hand.landmark[12]
                ring = hand.landmark[16]
                pinky = hand.landmark[20]

                if label == 'Right':
                    screen_x, screen_y = smooth_cursor(int(index.x * screen_width), int(index.y * screen_height))
                    try:
                        pyautogui.moveTo(screen_x, screen_y, duration=0.01)
                    except:
                        pass

                    tx = int(thumb.x * frame_w)
                    ty = int(thumb.y * frame_h)
                    distance = ((ix - tx) ** 2 + (iy - ty) ** 2) ** 0.5
                    if distance < CLICK_THRESHOLD:
                        try:
                            pyautogui.click()
                            time.sleep(0.2)
                        except:
                            pass

                    # Middle and thumb for left-click
                    mx = int(middle.x * frame_w)
                    my = int(middle.y * frame_h)
                    m_dist = ((tx - mx) ** 2 + (ty - my) ** 2) ** 0.5
                    if m_dist < CLICK_THRESHOLD:
                        try:
                            pyautogui.click()
                            time.sleep(0.2)
                        except:
                            pass

                elif label == 'Left':
                    tm_dist = ((thumb.x - middle.x)**2 + (thumb.y - middle.y)**2) ** 0.5
                    ti_dist = ((thumb.x - index.x)**2 + (thumb.y - index.y)**2) ** 0.5
                    tr_dist = ((thumb.x - ring.x)**2 + (thumb.y - ring.y)**2) ** 0.5
                    tp_dist = ((thumb.x - pinky.x)**2 + (thumb.y - pinky.y)**2) ** 0.5

                    if tm_dist < 0.05:
                        try:
                            pyautogui.scroll(30)
                        except:
                            pass
                    elif ti_dist < 0.05:
                        try:
                            pyautogui.scroll(-30)
                        except:
                            pass
                    elif tr_dist < 0.05:
                        try:
                            pyautogui.hotkey('alt', 'left')
                        except:
                            pass
                    elif tp_dist < 0.05:
                        try:
                            pyautogui.hotkey('alt', 'right')
                        except:
                            pass

        if 'Left' in index_fingers and 'Right' in index_fingers:
            lx, ly = index_fingers['Left']
            rx, ry = index_fingers['Right']
            dist = ((lx - rx)**2 + (ly - ry)**2) ** 0.5
            if dist < 50:
                if not osk_launched:
                    os.system("start osk")
                    osk_launched = True
                    time.sleep(0.5)
                else:
                    os.system("taskkill /IM osk.exe /F")
                    osk_launched = False
                    time.sleep(0.5)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        cv2.namedWindow("Gesture Controller", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Gesture Controller", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Gesture Controller", frame)

except:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
