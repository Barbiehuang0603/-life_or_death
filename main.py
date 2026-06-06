import pygame
import sys
from systems.room import generate_room

pygame.init()

WIDTH = 960
HEIGHT = 540

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Life or Death")

clock = pygame.time.Clock()

# =====================================
# 遊戲狀態
# =====================================

GAME_PLAYING = 0
GAME_DIED = 1
GAME_TIMEOUT = 2

game_state = GAME_PLAYING

# =====================================
# 房間
# =====================================

room = generate_room()

directions = ["front", "right", "back", "left"]
current_view = 0

# =====================================
# 計時器
# =====================================

ROOM_TIME_LIMIT = 10

room_start_time = pygame.time.get_ticks()

timer_font = pygame.font.SysFont(
    "Courier New",
    36,
    bold=True
)

# =====================================
# 圖片
# =====================================

door_base_img = pygame.image.load(
    "assets/room/back.jpg"
)
door_base_img = pygame.transform.scale(
    door_base_img,
    (WIDTH, HEIGHT)
)

wall_img = pygame.image.load(
    "assets/room/wall.jpg"
)
wall_img = pygame.transform.scale(
    wall_img,
    (WIDTH, HEIGHT)
)

life_img = pygame.image.load(
    "assets/room/life.jpg"
)

death_img = pygame.image.load(
    "assets/room/death.jpg"
)

# 門圖案大小
SIGN_WIDTH = 225
SIGN_HEIGHT = 275

life_img = pygame.transform.scale(
    life_img,
    (SIGN_WIDTH, SIGN_HEIGHT)
)

death_img = pygame.transform.scale(
    death_img,
    (SIGN_WIDTH, SIGN_HEIGHT)
)

# 門圖案位置
SIGN_X = 370
SIGN_Y = 176

# 死亡畫面

dead_image = pygame.image.load(
    "assets/room/dead.jpg"
)

dead_image = pygame.transform.scale(
    dead_image,
    (WIDTH, HEIGHT)
)

# 時間到畫面

timesup_image = pygame.image.load(
    "assets/room/timesup.jpg"
)

timesup_image = pygame.transform.scale(
    timesup_image,
    (WIDTH, HEIGHT)
)

# 危險狀態閃爍計時器

danger_alpha = 0

# =====================================
# 前進動畫
# =====================================

gogo_frames = []

for i in range(1, 6):

    img = pygame.image.load(
        f"assets/room/gogo/{i:03d}.jpg"
    )

    img = pygame.transform.scale(
        img,
        (WIDTH, HEIGHT)
    )

    gogo_frames.append(img)

# =====================================
# 畫房間
# =====================================

def draw_room():

    current_direction = directions[current_view]

    # 後方
    if current_direction == "back":

        screen.blit(
            door_base_img,
            (0, 0)
        )

        return

    room_type = room[current_direction]

    # 牆壁
    if room_type == "wall":

        screen.blit(
            wall_img,
            (0, 0)
        )

    # 生門
    elif room_type == "life":

        screen.blit(
            door_base_img,
            (0, 0)
        )

        screen.blit(
            life_img,
            (SIGN_X, SIGN_Y)
        )

    # 死門
    elif room_type == "death":

        screen.blit(
            door_base_img,
            (0, 0)
        )

        screen.blit(
            death_img,
            (SIGN_X, SIGN_Y)
        )

# =====================================
# 門淡出動畫
# =====================================

def fade_door(selected_type):

    if selected_type == "life":

        original_img = life_img.copy()

    else:

        original_img = death_img.copy()

    for alpha in range(255, -1, -4):

        screen.blit(
            door_base_img,
            (0, 0)
        )

        temp = original_img.copy()

        temp.set_alpha(alpha)

        screen.blit(
            temp,
            (SIGN_X, SIGN_Y)
        )

        pygame.display.update()

        pygame.time.delay(15)

# =====================================
# 前進動畫
# =====================================

def play_gogo_animation():

    for frame in gogo_frames:

        screen.blit(
            frame,
            (0, 0)
        )

        pygame.display.update()

        pygame.time.delay(120)

    pygame.time.delay(300)

# =====================================
# 主迴圈
# =====================================

while True:

    if game_state == GAME_PLAYING:

        elapsed_time = (
            pygame.time.get_ticks()
            - room_start_time
        ) / 1000

        remaining_time = max(
            0,
            ROOM_TIME_LIMIT
            - int(elapsed_time)
        )

        if remaining_time <= 0:

            game_state = GAME_TIMEOUT

    else:

        remaining_time = 0

    # =================================
    # Event
    # =================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        if (
            event.type == pygame.KEYDOWN
            and game_state == GAME_PLAYING
        ):

            # 向右看

            if event.key == pygame.K_RIGHT:

                current_view = (
                    current_view + 1
                ) % len(directions)

            # 向左看

            elif event.key == pygame.K_LEFT:

                current_view = (
                    current_view - 1
                ) % len(directions)

            # 前進

            elif event.key == pygame.K_UP:

                current_direction = (
                    directions[current_view]
                )

                if current_direction == "back":

                    print(
                        "後方不可前進"
                    )

                else:

                    room_type = room[
                        current_direction
                    ]

                    # 生門

                    if room_type == "life":

                        fade_door(
                            "life"
                        )

                        play_gogo_animation()

                        room = generate_room()

                        current_view = 0

                        room_start_time = (
                            pygame.time.get_ticks()
                        )

                    # 死門

                    elif room_type == "death":

                        fade_door(
                            "death"
                        )

                        play_gogo_animation()

                        game_state = GAME_DIED

                    # 牆壁

                    else:

                        print(
                            "這裡是牆壁"
                        )

    # =================================
    # Draw
    # =================================

    if game_state == GAME_PLAYING:

        draw_room()

        timer_color = (
            (255, 0, 0)
            if remaining_time <= 10
            else (255, 255, 255)
        )
        border_color = (
            (255, 0, 0)
            if remaining_time <= 10
            else (255, 255, 255)
        )

        timer_text = timer_font.render(
            f"{remaining_time:02d}",
            True,
            timer_color
        )
        padding = 12

        box_x=15
        box_y=15

        box_width = (
            timer_text.get_width() + padding * 2            
        )
        box_height = (
            timer_text.get_height() + padding * 2            
        )

        box_surface = pygame.Surface(
            (box_width, box_height)
        )

        box_surface.set_alpha(180)

        box_surface.fill((0, 0, 0))

        screen.blit(
            box_surface,
            (box_x, box_y)
        )

        # 白色邊框
        pygame.draw.rect(
            screen,border_color,
            (
                box_x,
                box_y,
                box_width,
                box_height
            ),
            2
        )

        screen.blit(
            timer_text,
            (
                box_x + padding,
                box_y + padding
            )
        )
        # ==========================
        # 危險紅色閃爍邊框
        # ==========================

        if remaining_time <= 10:

            pulse = abs(
                pygame.time.get_ticks() % 1000 - 500
            ) / 500

            base_alpha = int(
                150 * (1 - pulse)
            )

            warning_surface = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            border_width = 50
            for i in range(border_width):

                alpha = int(
                    base_alpha *
                    ((border_width - i) / border_width)
                )

                color = (255,0,0,alpha)

                # 上
                pygame.draw.line(
                    warning_surface,
                    color,
                    (0,i),
                    (WIDTH,i)
                )

                # 下
                pygame.draw.line(
                    warning_surface,
                    color,
                    (0,HEIGHT - i),
                    (WIDTH,HEIGHT - i)
                )

                # 左
                pygame.draw.line(
                    warning_surface,
                    color,
                    (i,0),
                    (i,HEIGHT)
                )

                # 右
                pygame.draw.line(
                    warning_surface,
                    color,
                    (WIDTH - i,0),
                    (WIDTH - i,HEIGHT)
                )

                screen.blit(
                    warning_surface,
                    (0, 0)
                )


    elif game_state == GAME_DIED:

        screen.blit(
            dead_image,
            (0, 0)
        )

    elif game_state == GAME_TIMEOUT:

        screen.blit(
            timesup_image,
            (0, 0)
        )

    pygame.display.update()

    clock.tick(10)