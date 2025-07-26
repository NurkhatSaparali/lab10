import pygame
import random
import psycopg2
from config import load_config
pygame.init()
#настройки экрана и цвета
width = 600
height = 600
cell = 30
screen = pygame.display.set_mode((width, height))
colorWHITE = (255, 255, 255)
colorGRAY = (200, 200, 200)
colorRed = (255, 0, 0)
colorYELLOW = (255, 255, 0)
colorGREEN = (0, 255, 0)
FPS = 7
font = pygame.font.SysFont("Arial", 24)

#сетка
def draw_grid_chess():
    colors = [colorWHITE, colorGRAY]
    for i in range(height // cell):
        for j in range(width // cell):
            pygame.draw.rect(screen, colors[(i + j) % 2], (i * cell, j * cell, cell, cell), 1)

#точка
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

#стены
class Wall:
    def __init__(self):
        self.positions = []
    def generate(self, level):
        self.positions.clear()
        if level >= 3:
            for x in range(5, 15):
                self.positions.append(Point(x, 10))
            for y in range(15, 20):
                self.positions.append(Point(20, y))

    def draw(self):
        for wall in self.positions:
            pygame.draw.rect(screen, (100, 100, 100), (wall.x * cell, wall.y * cell, cell, cell))

    def check_collision(self, head):
        for wall in self.positions:
            if head.x == wall.x and head.y == wall.y:
                return True
        return False

#змейка
class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.grow = False

    def move(self, walls):
        new_head = Point(self.body[0].x + self.dx, self.body[0].y + self.dy)
        new_head.x %= width // cell
        new_head.y %= height // cell
        for segment in self.body:
            if new_head.x == segment.x and new_head.y == segment.y:
                return False
        if walls.check_collision(new_head):
            return False
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        return True

    def draw(self):
        pygame.draw.rect(screen, colorRed, (self.body[0].x * cell, self.body[0].y * cell, cell, cell))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, colorYELLOW, (segment.x * cell, segment.y * cell, cell, cell))

    def check_collision(self, food):
        if self.body[0].x == food.pos.x and self.body[0].y == food.pos.y:
            self.grow = True
            return True
        return False

#еда
class Food:
    def __init__(self, snake):
        self.spawn_time = pygame.time.get_ticks()
        self.weight = random.choice([1, 2, 3])
        self.pos = self.get_random_pos(snake)

    def get_random_pos(self, snake):
        while True:
            x = random.randint(0, (width // cell) - 1)
            y = random.randint(0, (height // cell) - 1)
            if not any(part.x == x and part.y == y for part in snake.body):
                return Point(x, y)

    def draw(self):
        pygame.draw.rect(screen, colorGREEN, (self.pos.x * cell, self.pos.y * cell, cell, cell))

    def respawn(self, snake):
        self.spawn_time = pygame.time.get_ticks()
        self.weight = random.choice([1, 2, 3])
        self.pos = self.get_random_pos(snake)

#сохранение результата
def save_score_to_db(username, score, level):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user is None:
                    cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id", (username,))
                    user_id = cur.fetchone()[0]
                else:
                    user_id = user[0]
                cur.execute("INSERT INTO user_score (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
                conn.commit()
    except Exception as e:
        print("Ошибка при сохранении:", e)

#получение текущего уровня пользователя
def get_current_level(username):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(level) FROM user_score us JOIN users u ON us.user_id = u.user_id WHERE u.username = %s", (username,))
                result = cur.fetchone()
                return result[0] if result[0] is not None else 1
    except Exception as e:
        print("Ошибка при получении уровня:", e)
        return 1

#имя пользователя
username = input("Введите ваше имя: ")
level = get_current_level(username)
print(f"Ваш текущий уровень: {level}")

#инициализация
clock = pygame.time.Clock()
snake = Snake()
food = Food(snake)
walls = Wall()
walls.generate(level)
running = True
score = 0
foods_eaten = 0
pause = False

while running:
    screen.fill((0, 0, 0))
    draw_grid_chess()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score_to_db(username, score, level)
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and snake.dx == 0:
                snake.dx = 1
                snake.dy = 0
            elif event.key == pygame.K_LEFT and snake.dx == 0:
                snake.dx = -1
                snake.dy = 0
            elif event.key == pygame.K_UP and snake.dy == 0:
                snake.dx = 0
                snake.dy = -1
            elif event.key == pygame.K_DOWN and snake.dy == 0:
                snake.dx = 0
                snake.dy = 1
            elif event.key == pygame.K_p:
                pause = not pause
                if pause:
                    print("Пауза. Сохраняем")
                    save_score_to_db(username, score, level)

    if not pause:
        if not snake.move(walls):
            print("Game Over!")
            save_score_to_db(username, score, level)
            running = False
        if pygame.time.get_ticks() - food.spawn_time > 5000:
            food.respawn(snake)
        if snake.check_collision(food):
            score += food.weight
            foods_eaten += 1
            food.respawn(snake)
            if foods_eaten >= 3:
                level += 1
                foods_eaten = 0
                FPS += 2
                walls.generate(level)
    snake.draw()
    food.draw()
    walls.draw()
    text = font.render("Score: " + str(score) + "  Level: " + str(level), True, (255, 255, 255))
    screen.blit(text, (10, 10))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
