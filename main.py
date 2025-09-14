import cv2
import mediapipe as mp
import pyautogui

cap = cv2.VideoCapture(0)


hand_detector = mp.solutions.hands.Hands(max_num_hands=1)
drawing_utils = mp.solutions.drawing_utils


screen_width, screen_height = pyautogui.size()


smooth_x, smooth_y = 0, 0

def draw_circle_with_label(frame, x, y, color, label):
    cv2.circle(frame, (x, y), 10, color, -1)
    cv2.putText(frame, label, (x - 20, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  # Mirror the image
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks

    index_x = index_y = thumb_y = middle_y = None

    if hands:
        for hand in hands:
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark

            for id, lm in enumerate(landmarks):
                x = int(lm.x * frame_width)
                y = int(lm.y * frame_height)

                if id == 8:  # Index finger
                    draw_circle_with_label(frame, x, y, (0, 255, 255), "Index")
                    index_x = screen_width * lm.x
                    index_y = screen_height * lm.y

                if id == 4:  # Thumb
                    draw_circle_with_label(frame, x, y, (255, 0, 0), "Thumb")
                    thumb_y = screen_height * lm.y

                if id == 12:  # Middle finger
                    draw_circle_with_label(frame, x, y, (0, 0, 255), "Middle")
                    middle_y = screen_height * lm.y

      
        if index_x is not None and index_y is not None:
            smooth_x = 0.3 * smooth_x + 0.3 * index_x
            smooth_y = 0.3 * smooth_y + 0.3 * index_y
            pyautogui.moveTo(smooth_x, smooth_y, duration=0.1)

        # Click detection
        if index_y is not None and thumb_y is not None:
            if abs(index_y - thumb_y) < 30:
                pyautogui.click()
                pyautogui.sleep(0.5)  # Delay to avoid multiple clicks

        # Scroll detection
        if index_y is not None and middle_y is not None:
            diff = index_y - middle_y
            if abs(diff) > 40:
                if diff > 0:
                    pyautogui.scroll(30)  # Scroll up
                else:
                    pyautogui.scroll(-30)  # Scroll down

    # Show video feed
    cv2.imshow("Virtual Mouse", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
