import pygame
import random
import cv2
import mediapipe as mp
import os
import time

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FRUIT_SIZE = 40
BASKET_WIDTH, BASKET_HEIGHT = 100, 80
FPS = 60
MAX_LIVES = 5
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 0, 255)

# Paths
IMG_PATH = "assets/images"
SOUND_PATH = "assets/sound"

# Assets
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🍓 Fruit Catcher Game")
background_img = pygame.image.load(os.path.join(IMG_PATH, "backgroundimg.jpg"))
basket_img = pygame.transform.scale(pygame.image.load(os.path.join(IMG_PATH, "basket.jpg")), (BASKET_WIDTH, BASKET_HEIGHT))
heart_img = pygame.transform.scale(pygame.image.load(os.path.join(IMG_PATH, "heart.jpg")), (30, 30))
fruit_files = ["banana.jpg", "mango.jpg", "orange.jpg", "pineapple.png", "watermelon.jpg", "grape.png"]
fruit_imgs = [pygame.transform.scale(pygame.image.load(os.path.join(IMG_PATH, f)), (FRUIT_SIZE, FRUIT_SIZE)) for f in fruit_files]
catch_sound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "catch.mp3"))
miss_sound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "miss.mp3"))
pygame.mixer.music.load(os.path.join(SOUND_PATH, "background.mp3"))
pygame.mixer.music.play(-1)

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)
cap = cv2.VideoCapture(0)

font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

difficulty_speeds = {
    "Easy": (2, 4),
    "Medium": (3, 6),
    "Hard": (5, 8)
}

def select_difficulty():
    selected = None
    print("Move hand to LEFT (Easy), CENTER (Medium), RIGHT (Hard)")
    while not selected:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        cv2.putText(frame, "Select Difficulty:", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, PINK, 2)
        cv2.putText(frame, "LEFT = Easy | CENTER = Medium | RIGHT = Hard | Press q to Quit", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            index_finger = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x_pos = int(index_finger.x * w)

            if x_pos < w // 3:
                selected = "Easy"
            elif x_pos < 2 * w // 3:
                selected = "Medium"
            else:
                selected = "Hard"

            for lm in hand.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Select Difficulty", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            exit()

    cv2.destroyWindow("Select Difficulty")
    return selected

def draw_game(fruits, basket, score, lives):
    screen.blit(background_img, (0, 0))
    screen.blit(basket_img, (basket.x, basket.y))
    for fruit in fruits:
        screen.blit(fruit["img"], fruit["rect"])
    for i in range(lives):
        screen.blit(heart_img, (10 + i * 35, 10))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 10))
    pygame.display.flip()

def spawn_fruit(fruits, speed_range):
    idx = random.randint(0, len(fruit_imgs) - 1)
    x = random.randint(0, WIDTH - FRUIT_SIZE)
    speed = random.randint(*speed_range)
    fruit = {
        "rect": pygame.Rect(x, -FRUIT_SIZE, FRUIT_SIZE, FRUIT_SIZE),
        "img": fruit_imgs[idx],
        "speed": speed
    }
    fruits.append(fruit)

# ✅ Robust finger counting
def count_raised_fingers(landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb (check direction)
    if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other 4 fingers
    for i in range(1, 5):
        if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

def main_game_loop(difficulty):
    speed_range = difficulty_speeds[difficulty]
    basket = pygame.Rect(WIDTH // 2, HEIGHT - BASKET_HEIGHT - 10, BASKET_WIDTH, BASKET_HEIGHT)
    fruits = []
    score = 0
    lives = MAX_LIVES
    spawn_timer = 0
    game_over = False

    while True:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                exit()

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        h, w, _ = frame.shape

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            basket.x = int(index_tip.x * WIDTH - BASKET_WIDTH // 2)

            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 6, RED, -1)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=GREEN, thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=RED, thickness=2))

        if not game_over:
            spawn_timer += 1
            if spawn_timer > 30:
                spawn_fruit(fruits, speed_range)
                spawn_timer = 0

            for fruit in fruits[:]:
                fruit["rect"].y += fruit["speed"]
                if fruit["rect"].colliderect(basket):
                    fruits.remove(fruit)
                    score += 10
                    catch_sound.play()
                elif fruit["rect"].y > HEIGHT:
                    fruits.remove(fruit)
                    lives -= 1
                    miss_sound.play()

            if lives <= 0:
                game_over = True

        else:
            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                fingers = count_raised_fingers(hand.landmark)
                cv2.putText(frame, f"Fingers: {fingers}", (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                if fingers == 0:
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    exit()
                elif fingers == 5:
                    return

            cv2.putText(frame, "GAME OVER", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
            cv2.putText(frame, f"Final Score: {score}", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            cv2.putText(frame, "Raise 5 fingers to RESTART", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            cv2.putText(frame, "Show CLOSED PALM to QUIT", (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 200, 200), 2)

        cv2.imshow("Hand Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            exit()

        draw_game(fruits, basket, score, lives)
        clock.tick(FPS)

# Run the Game
while True:
    difficulty = select_difficulty()
    main_game_loop(difficulty)
