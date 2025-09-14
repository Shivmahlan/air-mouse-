import cv2
import mediapipe as mp
import numpy as np

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
draw = mp.solutions.drawing_utils

# Game window size
width, height = 1920, 1080
paddle_height = 100
paddle_width = 15


# Paddle & Ball Initial State
def reset_game():
    return {
        "player_y": height // 2,
        "opponent_y": height // 2,
        "ball_x": width // 2,
        "ball_y": height // 2,
        "ball_dx": 5,
        "ball_dy": 5,
        "player_score": 0,
        "opponent_score": 0,
        "paused": False
    }


game = reset_game()

# Quit gesture state
exit_gesture_counter = 0
EXIT_THRESHOLD = 20  # number of frames the exit gesture must persist

# Webcam
cap = cv2.VideoCapture(0)


def fingers_up(hand):
    lm = hand.landmark
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb (x-axis comparison)
    fingers.append(lm[tips[0]].x > lm[tips[0] - 1].x)

    # Other fingers (y-axis comparison)
    for id in range(1, 5):
        fingers.append(lm[tips[id]].y < lm[tips[id] - 2].y)
    return fingers  # [thumb, index, middle, ring, pinky]


while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    game_screen = np.zeros((height, width, 3), dtype=np.uint8)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # Paddle control
        index_finger = hand.landmark[8]
        index_y = int(index_finger.y * height)
        game["player_y"] = index_y - paddle_height // 2

        # Gesture detection
        finger_states = fingers_up(hand)
        total_up = sum(finger_states)

        # Pause gesture (fist)
        if total_up == 0:
            game["paused"] = not game["paused"]
            cv2.putText(game_screen, "Paused", (width // 2 - 100, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (0, 0, 255), 4)
            cv2.imshow("Gesture Pong", game_screen)
            cv2.waitKey(1000)
            continue

        # Restart gesture (index + middle + ring)
        if finger_states[1:4] == [True, True, True] and not finger_states[4] and not finger_states[0]:
            game = reset_game()
            continue

        # Exit gesture (4 fingers up, thumb down)
        if finger_states[0] == False and finger_states[1:] == [True, True, True, True]:
            exit_gesture_counter += 1
            if exit_gesture_counter > EXIT_THRESHOLD:
                break
        else:
            exit_gesture_counter = 0

    if not game["paused"]:
        # Ball movement
        game["ball_x"] += game["ball_dx"]
        game["ball_y"] += game["ball_dy"]

        if game["ball_y"] <= 0 or game["ball_y"] >= height:
            game["ball_dy"] *= -1

        # Opponent AI
        if game["opponent_y"] + paddle_height // 2 < game["ball_y"]:
            game["opponent_y"] += 4
        else:
            game["opponent_y"] -= 4
        game["opponent_y"] = max(0, min(height - paddle_height, game["opponent_y"]))

        # Paddle collision
        if game["ball_x"] <= paddle_width and game["player_y"] < game["ball_y"] < game["player_y"] + paddle_height:
            game["ball_dx"] *= -1

        elif game["ball_x"] >= width - paddle_width and game["opponent_y"] < game["ball_y"] < game[
            "opponent_y"] + paddle_height:
            game["ball_dx"] *= -1

        # Scoring
        if game["ball_x"] < 0:
            game["opponent_score"] += 1
            game["ball_x"], game["ball_y"] = width // 2, height // 2

        elif game["ball_x"] > width:
            game["player_score"] += 1
            game["ball_x"], game["ball_y"] = width // 2, height // 2

    # Draw paddles and ball
    cv2.rectangle(game_screen, (0, game["player_y"]), (paddle_width, game["player_y"] + paddle_height), (255, 255, 255),
                  -1)
    cv2.rectangle(game_screen, (width - paddle_width, game["opponent_y"]),
                  (width, game["opponent_y"] + paddle_height), (255, 255, 255), -1)
    cv2.circle(game_screen, (game["ball_x"], game["ball_y"]), 10, (255, 255, 255), -1)

    # Draw scores
    cv2.putText(game_screen, f"You: {game['player_score']}", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    cv2.putT
