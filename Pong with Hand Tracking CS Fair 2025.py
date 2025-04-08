import cv2
import mediapipe as mp
import tkinter as tk

# Initialize MediaPipe hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Start webcam capture
cap = cv2.VideoCapture(0)

# Game and UI setup
WIDTH, HEIGHT = 600, 400  # Canvas size
paddle_width, paddle_height = 100, 10  # Paddle dimensions
ball_size = 10  # Ball size

# Initial positions
player_x = (WIDTH - paddle_width) // 2
ai_x = (WIDTH - paddle_width) // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_speed_x, ball_speed_y = 10, 10  # Ball speed (x and y direction)
ai_speed = 9  # AI paddle speed
score_player, score_ai = 0, 0  # Score tracking
game_over = False  # Game state

# Create the main window and canvas
root = tk.Tk()
root.title("AI Pong")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

# Restart the game: reset ball, speed, scores, and state
def restart_game():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, score_player, score_ai, game_over
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_speed_x, ball_speed_y = 10, 10
    score_player, score_ai = 0, 0
    game_over = False
    move_ball()  # Resume ball movement

# Button to trigger restart
restart_btn = tk.Button(root, text="Restart", command=restart_game)
restart_btn.pack()

# Main game loop for ball movement and collision detection
def move_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, score_player, score_ai, game_over

    if game_over:
        return  # Stop if game has ended

    # Update ball position
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Bounce off side walls
    if ball_x <= 0 or ball_x >= WIDTH - ball_size:
        ball_speed_x = -ball_speed_x

    # Ball hits AI paddle (top)
    if ai_x <= ball_x <= ai_x + paddle_width and ball_y <= paddle_height:
        ball_speed_y = abs(ball_speed_y) + 0.2  # Bounce downward, slightly faster

    # Ball hits Player paddle (bottom)
    if player_x <= ball_x <= player_x + paddle_width and HEIGHT - paddle_height <= ball_y <= HEIGHT:
        ball_speed_y = -abs(ball_speed_y) - 0.2  # Bounce upward, slightly faster

    # Ball goes off bottom – AI scores
    if ball_y >= HEIGHT:
        score_ai += 1
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2  # Reset ball position

    # Ball goes off top – Player scores
    elif ball_y <= 0:
        score_player += 1
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2

    # Check win condition: first to 5, win by 2
    if max(score_ai, score_player) >= 5 and abs(score_ai - score_player) >= 2:
        game_over = True
        winner = "Player" if score_player > score_ai else "AI"
        canvas.create_text(WIDTH//2, HEIGHT//2, text=f"{winner} Wins!", font=("Arial", 24), fill="red")
        return

    move_ai()  # Update AI paddle position

    # Redraw everything
    canvas.delete("all")
    canvas.create_rectangle(player_x, HEIGHT - paddle_height, player_x + paddle_width, HEIGHT, fill="white")
    canvas.create_rectangle(ai_x, 0, ai_x + paddle_width, paddle_height, fill="red")
    canvas.create_oval(ball_x, ball_y, ball_x + ball_size, ball_y + ball_size, fill="white")
    canvas.create_text(50, 20, text=f"Player: {score_player}", font=("Arial", 14), fill="white")
    canvas.create_text(550, 20, text=f"AI: {score_ai}", font=("Arial", 14), fill="red")
    
    # Call this function again after 16ms (~60 FPS)
    root.after(16, move_ball)

# AI paddle movement logic – follows the ball
def move_ai():
    global ai_x
    if ai_x + paddle_width / 2 < ball_x:
        ai_x += ai_speed  # Move right
    elif ai_x + paddle_width / 2 > ball_x:
        ai_x -= ai_speed  # Move left
    # Keep AI paddle within bounds
    ai_x = max(0, min(ai_x, WIDTH - paddle_width))

# Track hand with MediaPipe and control player paddle
def track_hand():
    global player_x
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)  # Mirror image for natural movement
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
    results = hands.process(rgb_frame)  # Run hand tracking

    # If hand is detected, use wrist landmark to control paddle
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * WIDTH)
            # Center paddle on wrist x-position, keep it within screen
            player_x = min(max(x - paddle_width // 2, 0), WIDTH - paddle_width)

    # Resize and show camera frame to reduce lag
    frame = cv2.resize(frame, (320, 240))
    cv2.putText(frame, "Move Hand to Control Paddle", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.imshow("Hand Tracking", frame)

    # Exit on pressing Esc
    if cv2.waitKey(1) & 0xFF == 27:
        root.destroy()
        return

    # Schedule next frame check (30ms delay = ~33 FPS)
    root.after(30, track_hand)

# Start both hand tracking and game loop
track_hand()
move_ball()

# Keep the window open and running
root.mainloop()

# Clean up resources when window closes
cap.release()
cv2.destroyAllWindows()
