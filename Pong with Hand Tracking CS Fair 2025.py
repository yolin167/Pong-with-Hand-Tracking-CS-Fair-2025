import cv2
import mediapipe as mp
import tkinter as tk
import random

# Initialize Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

# Tkinter Setup
WIDTH, HEIGHT = 600, 400
paddle_width, paddle_height = 100, 10
ball_size = 10
player_x = (WIDTH - paddle_width) // 2
ai_x = (WIDTH - paddle_width) // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_speed_x, ball_speed_y = 10, 10
ai_speed = 50  # Tunable AI speed
score_player, score_ai = 0, 0
game_over = False

root = tk.Tk()
root.title("AI Pong")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

# Restart Game
def restart_game():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, score_player, score_ai, game_over
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_speed_x, ball_speed_y = 10, 10
    score_player, score_ai = 0, 0
    game_over = False
    move_ball()

restart_btn = tk.Button(root, text="Restart", command=restart_game)
restart_btn.pack()

# Ball Movement
def move_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, score_player, score_ai, game_over

    if game_over:
        return

    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Ball hits side walls
    if ball_x <= 0 or ball_x >= WIDTH - ball_size:
        ball_speed_x = -ball_speed_x

    # Ball hits AI paddle
    if ai_x <= ball_x <= ai_x + paddle_width and ball_y <= paddle_height:
        ball_speed_y = abs(ball_speed_y) + 0.2  # Increase speed slightly

    # Ball hits Player paddle
    if player_x <= ball_x <= player_x + paddle_width and HEIGHT - paddle_height <= ball_y <= HEIGHT:
        ball_speed_y = -abs(ball_speed_y) - 0.2  # Increase speed slightly

    # Score update
    if ball_y >= HEIGHT:
        score_ai += 1
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    elif ball_y <= 0:
        score_player += 1
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2

    # Win-by-2 rule (first to 10, win by 2)
    if max(score_ai, score_player) >= 5 and abs(score_ai - score_player) >= 2:
        game_over = True
        winner = "Player" if score_player > score_ai else "AI"
        canvas.create_text(WIDTH//2, HEIGHT//2, text=f"{winner} Wins!", font=("Arial", 24), fill="red")
        return

    # Move AI Paddle
    move_ai()

    # Redraw scene
    canvas.delete("all")
    canvas.create_rectangle(player_x, HEIGHT - paddle_height, player_x + paddle_width, HEIGHT, fill="white")
    canvas.create_rectangle(ai_x, 0, ai_x + paddle_width, paddle_height, fill="red")
    canvas.create_oval(ball_x, ball_y, ball_x + ball_size, ball_y + ball_size, fill="white")
    canvas.create_text(50, 20, text=f"Player: {score_player}", font=("Arial", 14), fill="white")
    canvas.create_text(550, 20, text=f"AI: {score_ai}", font=("Arial", 14), fill="red")
    
    root.after(30, move_ball)

# AI Paddle Movement
def move_ai():
    global ai_x
    if ai_x + paddle_width / 2 < ball_x:
        ai_x += ai_speed
    elif ai_x + paddle_width / 2 > ball_x:
        ai_x -= ai_speed
    ai_x = max(0, min(ai_x, WIDTH - paddle_width))

# Hand Tracking for Player Paddle
def track_hand():
    global player_x
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * WIDTH)
            player_x = min(max(x - paddle_width // 2, 0), WIDTH - paddle_width)

    # Show Camera Feed
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.putText(frame, "Move Hand to Control Paddle", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow("Hand Tracking", frame)

    root.after(10, track_hand)

# Start Game
track_hand()
move_ball()

root.mainloop()
cap.release()
cv2.destroyAllWindows()