import random
from pygame import Rect

WIDTH = 640
HEIGHT = 480
TILE_SIZE = 32
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

# Game states
STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_WIN = "win"
STATE_GAMEOVER = "gameover"
game_state = STATE_MENU

audio_enabled = True  

BTN_WIDTH = 300
BTN_HEIGHT = 50
menu_buttons = {
    "start": Rect((WIDTH // 2 - BTN_WIDTH // 2, 160), (BTN_WIDTH, BTN_HEIGHT)),
    "audio": Rect((WIDTH // 2 - BTN_WIDTH // 2, 240), (BTN_WIDTH, BTN_HEIGHT)),
    "quit": Rect((WIDTH // 2 - BTN_WIDTH // 2, 320), (BTN_WIDTH, BTN_HEIGHT)),
}

walls = []
coins = []
enemies = []
exit_rect = Rect(0, 0, TILE_SIZE, TILE_SIZE)

MIN_WALLS = 30
MAX_WALLS = 55
NUM_COINS = 8
NUM_ENEMIES = 4
PLAYER_SPEED = 2

class Player:

    def __init__(self, x, y):
        self.rect = Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.idle_img = Actor("hero_idle")
        self.idle2_img = Actor("hero_idle2")
        self.walk_img = Actor("hero_walk")
        self.move_img = Actor("hero_move")
        self.current_img = self.idle_img
        self.anim_frame = 0
        self.idle_frame = 0

    def try_move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        if not (0 <= new_rect.x <= WIDTH - self.rect.width and
                0 <= new_rect.y <= HEIGHT - self.rect.height):
            return False
        for wall in walls:
            if new_rect.colliderect(wall):
                return False
        self.rect.x = new_rect.x
        self.rect.y = new_rect.y
        return True

    def update(self):
        dx = dy = 0
        if keyboard.left:
            dx -= PLAYER_SPEED
        if keyboard.right:
            dx += PLAYER_SPEED
        if keyboard.up:
            dy -= PLAYER_SPEED
        if keyboard.down:
            dy += PLAYER_SPEED

        if dx != 0 or dy != 0:
            self.anim_frame += 1
            if (self.anim_frame // 10) % 2 == 0:
                self.current_img = self.walk_img
            else:
                self.current_img = self.move_img
            self.idle_frame = 0
        else:
            self.idle_frame += 1
            if (self.idle_frame // 20) % 2 == 0:
                self.current_img = self.idle_img
            else:
                self.current_img = self.idle2_img
            self.anim_frame = 0

        if dx != 0:
            self.try_move(dx, 0)
        if dy != 0:
            self.try_move(0, dy)

    def draw(self):
        self.current_img.pos = (self.rect.x + TILE_SIZE // 2,
                                self.rect.y + TILE_SIZE // 2)
        self.current_img.draw()


class Enemy:
    def __init__(self, x, y):
        self.rect = Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.timer = random.randint(20, 80)
        self.speed = 1
        self.anim_frame = 0
        self.walk_img = Actor("enemy_walk")
        self.move_img = Actor("enemy_move")
        self.walk2_img = Actor("enemy_walk2")
        self.move2_img = Actor("enemy_move2")
        self.idle_img = Actor("enemy_idle")

        self.frames = [
            self.walk_img,
            self.move_img,
            self.walk2_img,
            self.move2_img,
            self.idle_img
        ]
        self.current_img = self.frames[0]

    def update(self):
        dx = self.dir[0] * self.speed
        dy = self.dir[1] * self.speed

        self.timer -= 1
        if self.timer <= 0:
            self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.timer = random.randint(30, 100)

        new_rect = self.rect.move(dx, dy)
        blocked = False
        if not (0 <= new_rect.x <= WIDTH - self.rect.width and
                0 <= new_rect.y <= HEIGHT - self.rect.height):
            blocked = True
        else:
            for wall in walls:
                if new_rect.colliderect(wall):
                    blocked = True
                    break

        if blocked:
            self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.timer = random.randint(20, 80)
        else:
            self.rect.x += dx
            self.rect.y += dy

        self.anim_frame += 1
        frame_index = (self.anim_frame // 10) % len(self.frames)
        self.current_img = self.frames[frame_index]

    def draw(self):
        """Draw the enemy sprite."""
        self.current_img.pos = (self.rect.x + TILE_SIZE // 2,
                                self.rect.y + TILE_SIZE // 2)
        self.current_img.draw()

def grid_random_position(exclude=set()):
    """Return a random grid position, avoiding excluded cells."""
    while True:
        gx = random.randint(0, COLS - 1)
        gy = random.randint(0, ROWS - 1)
        if (gx, gy) in exclude:
            continue
        return gx, gy


def cell_to_rect(gx, gy, size=TILE_SIZE):
    return Rect(gx * TILE_SIZE, gy * TILE_SIZE, size, size)


def generate_map():
    global walls, coins, enemies, player, exit_rect
    walls = []
    coins = []
    enemies = []

    player_grid = grid_random_position()
    exit_grid = grid_random_position(exclude={player_grid})

    wall_positions = set()
    num_walls = random.randint(MIN_WALLS, MAX_WALLS)
    while len(wall_positions) < num_walls:
        pos = grid_random_position(exclude={player_grid, exit_grid} | wall_positions)
        wall_positions.add(pos)

    coin_positions = set()
    while len(coin_positions) < NUM_COINS:
        pos = grid_random_position(
            exclude={player_grid, exit_grid} | wall_positions | coin_positions
        )
        coin_positions.add(pos)

    enemy_positions = set()
    while len(enemy_positions) < NUM_ENEMIES:
        pos = grid_random_position(
            exclude={player_grid, exit_grid} |
            wall_positions | coin_positions | enemy_positions
        )
        enemy_positions.add(pos)

    walls = [cell_to_rect(gx, gy) for (gx, gy) in wall_positions]
    coins = [
        Rect(gx * TILE_SIZE + TILE_SIZE // 4,
             gy * TILE_SIZE + TILE_SIZE // 4,
             TILE_SIZE // 2, TILE_SIZE // 2)
        for (gx, gy) in coin_positions
    ]

    enemies = [Enemy(gx * TILE_SIZE, gy * TILE_SIZE)
               for (gx, gy) in enemy_positions]
    player = Player(player_grid[0] * TILE_SIZE,
                    player_grid[1] * TILE_SIZE)

    exit_rect.x = exit_grid[0] * TILE_SIZE
    exit_rect.y = exit_grid[1] * TILE_SIZE

def draw_menu():
    screen.clear()
    screen.fill((20, 24, 30))
    screen.draw.text("TREASURE HUNT", center=(WIDTH // 2, 80),
                     fontsize=40, color="white")
    screen.draw.filled_rect(menu_buttons["start"], (70, 130, 180))
    screen.draw.text("Start Game", center=menu_buttons["start"].center,
                     fontsize=28, color="white")
    screen.draw.filled_rect(menu_buttons["audio"], (80, 80, 120))
    txt_audio = "Music: On" if audio_enabled else "Music: Off"
    screen.draw.text(txt_audio, center=menu_buttons["audio"].center,
                     fontsize=22, color="white")
    screen.draw.filled_rect(menu_buttons["quit"], (180, 70, 70))
    screen.draw.text("Quit", center=menu_buttons["quit"].center,
                     fontsize=28, color="white")
    screen.draw.text("Instructions: Use arrow keys to move. "
                     "Collect all yellow points and reach the green exit.",
                     topleft=(20, HEIGHT - 40), fontsize=18,
                     color="lightgray")


def draw_play():
    screen.clear()
    for r in range(ROWS):
        for c in range(COLS):
            rect = Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = (18, 20, 24) if (c + r) % 2 == 0 else (15, 17, 20)
            screen.draw.filled_rect(rect, color)

    for wall in walls:
        screen.draw.filled_rect(wall, (100, 100, 100))
        screen.draw.rect(wall, (120, 120, 120))

    for coin in coins:
        screen.draw.filled_rect(coin, (255, 210, 0))

    screen.draw.filled_rect(exit_rect, (50, 200, 50))

    for enemy in enemies:
        enemy.draw()

    player.draw()

    screen.draw.text(f"Points left: {len(coins)}", (10, 10),
                     fontsize=22, color="white")


def draw_win():
    screen.clear()
    screen.draw.text("YOU WON!", center=(WIDTH // 2, HEIGHT // 2),
                     fontsize=56, color="green")
    screen.draw.text("Click to return to menu",
                     center=(WIDTH // 2, HEIGHT // 2 + 60),
                     fontsize=28, color="white")


def draw_gameover():
    screen.clear()
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2),
                     fontsize=56, color="red")
    screen.draw.text("Click to return to menu",
                     center=(WIDTH // 2, HEIGHT // 2 + 60),
                     fontsize=28, color="white")


def draw():
    if game_state == STATE_MENU:
        draw_menu()
    elif game_state == STATE_PLAY:
        draw_play()
    elif game_state == STATE_WIN:
        draw_win()
    elif game_state == STATE_GAMEOVER:
        draw_gameover()

def update():
    global game_state
    if game_state == STATE_PLAY:
        player.update()
        for enemy in enemies:
            enemy.update()
        for coin in coins[:]:
            if player.rect.colliderect(coin):
                coins.remove(coin)
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                game_state = STATE_GAMEOVER
                break
        if not coins and player.rect.colliderect(exit_rect):
            game_state = STATE_WIN

def on_mouse_down(pos):
    global game_state, audio_enabled
    if game_state == STATE_MENU:
        if menu_buttons["start"].collidepoint(pos):
            start_game()
        elif menu_buttons["quit"].collidepoint(pos):
            quit()
        elif menu_buttons["audio"].collidepoint(pos):
            audio_enabled = not audio_enabled
            if audio_enabled:
                music.play('music_bg')
            else:
                music.stop()
    else:
        if game_state in (STATE_WIN, STATE_GAMEOVER):
            game_state = STATE_MENU

def start_game():
    global game_state
    generate_map()
    game_state = STATE_PLAY

generate_map()
music.set_volume(0.5)
if audio_enabled:
    music.play('music_bg')
