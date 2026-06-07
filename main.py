import pygame
import sys
import random
from systems.room import generate_room

pygame.init()

pixel_font = "assets/font/PixelOperator-Bold.ttf"

WIDTH=960
HEIGHT=540

screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Life or Death")
clock=pygame.time.Clock()

# 遊戲狀態
GAME_PLAYING=0
GAME_DIED=1
GAME_TIMEOUT=2
GAME_OVER_ANIMATION=3
game_state=GAME_PLAYING

# 生命值
MAX_LIVES=3
lives=3

heart_img=pygame.image.load("assets/ui/heart.png")
empty_heart_img=pygame.image.load("assets/ui/empty_heart.png")

heart_img=pygame.transform.scale(heart_img,(40,40))
empty_heart_img=pygame.transform.scale(empty_heart_img,(40,40))

# 房間
room=generate_room()
directions=["front","right","back","left"]
current_view=0

# 計時器
ROOM_TIME_LIMIT=10
room_start_time=pygame.time.get_ticks()

timer_font=pygame.font.Font(
    pixel_font,
    36,
    bold=True
)

# 背景
door_base_img=pygame.image.load("assets/room/back.jpg")
door_base_img=pygame.transform.scale(
    door_base_img,
    (WIDTH,HEIGHT)
)

wall_img=pygame.image.load("assets/room/wall.jpg")
wall_img=pygame.transform.scale(
    wall_img,
    (WIDTH,HEIGHT)
)

# 門大小
SIGN_WIDTH=225
SIGN_HEIGHT=275

# 生門
life_imgs=[]

for i in range(1,6):

    img=pygame.image.load(
        f"assets/room/door/life_{i}.png"
    )

    img=pygame.transform.scale(
        img,
        (SIGN_WIDTH,SIGN_HEIGHT)
    )

    life_imgs.append(img)

# 死門
death_imgs=[]

for i in range(1,6):

    img=pygame.image.load(
        f"assets/room/door/death_{i}.png"
    )

    img=pygame.transform.scale(
        img,
        (SIGN_WIDTH,SIGN_HEIGHT)
    )

    death_imgs.append(img)

current_life_img=random.choice(life_imgs)
current_death_img=random.choice(death_imgs)

# 門位置
SIGN_X=370
SIGN_Y=176

# gogo動畫
gogo_frames=[]

for i in range(1,6):

    img=pygame.image.load(
        f"assets/room/gogo/{i:03d}.jpg"
    )

    img=pygame.transform.scale(
        img,
        (WIDTH,HEIGHT)
    )

    gogo_frames.append(img)

# game over 動畫
game_over_frames=[]

for i in range(1,9):
    img=pygame.image.load(
        f"assets/room/game_over/{i:03d}.png"
    )
    img=pygame.transform.scale(
        img,
        (WIDTH,HEIGHT)
    )
    game_over_frames.append(img)

# 畫房間
def draw_room():

    current_direction=directions[current_view]

    if current_direction=="back":
        screen.blit(door_base_img,(0,0))
        return

    room_type=room[current_direction]

    if room_type=="wall":

        screen.blit(
            wall_img,
            (0,0)
        )

    elif room_type=="life":

        screen.blit(
            door_base_img,
            (0,0)
        )

        screen.blit(
            current_life_img,
            (SIGN_X,SIGN_Y)
        )

    elif room_type=="death":

        screen.blit(
            door_base_img,
            (0,0)
        )

        screen.blit(
            current_death_img,
            (SIGN_X,SIGN_Y)
        )


# 門淡出動畫
def fade_door(selected_type):

    if selected_type=="life":
        original_img=current_life_img.copy()
    else:
        original_img=current_death_img.copy()

    for alpha in range(255,-1,-4):

        screen.blit(
            door_base_img,
            (0,0)
        )

        temp=original_img.copy()
        temp.set_alpha(alpha)

        screen.blit(
            temp,
            (SIGN_X,SIGN_Y)
        )

        pygame.display.update()

        pygame.time.delay(15)


# 前進動畫
def play_gogo_animation():

    for frame in gogo_frames:

        screen.blit(
            frame,
            (0,0)
        )

        pygame.display.update()

        pygame.time.delay(120)

    pygame.time.delay(300)

def play_game_over_animation():

    # ===== 001 =====
    frame1 = game_over_frames[0]

    for alpha in range(80,256,3):

        temp = frame1.copy()
        temp.set_alpha(alpha)

        screen.fill((0,0,0))
        screen.blit(temp,(0,0))

        pygame.display.update()

        pygame.time.delay(15)

    pygame.time.delay(500)


    # ===== 002~004 =====
    for i in range(1,4):

        screen.blit(
            game_over_frames[i],
            (0,0)
        )

        pygame.display.update()

        pygame.time.delay(200)


    # ===== 005~006 =====
    for i in range(4,6):

        screen.blit(
            game_over_frames[i],
            (0,0)
        )

        pygame.display.update()
        pygame.event.pump()
        pygame.time.delay(240)

    # ===== 006 → 007 =====

    frame6 = game_over_frames[5]
    frame7 = game_over_frames[6]

    for alpha in range(50,256,2):

        temp6 = frame6.copy()
        temp6.set_alpha(255-alpha)

        temp7 = frame7.copy()
        temp7.set_alpha(alpha)

        screen.fill((0,0,0))

        screen.blit(temp6,(0,0))
        screen.blit(temp7,(0,0))

        pygame.display.update()

        pygame.event.pump()

        pygame.time.delay(15)

    # ===== 007 → 008 =====

    frame8 = game_over_frames[7]

    for alpha in range(0,256,3):

        temp7 = frame7.copy()
        temp7.set_alpha(255-alpha)

        temp8 = frame8.copy()
        temp8.set_alpha(alpha)

        screen.fill((0,0,0))

        screen.blit(temp7,(0,0))
        screen.blit(temp8,(0,0))

        pygame.display.update()

        pygame.event.pump()

        pygame.time.delay(20)

    pygame.event.pump()
    pygame.time.delay(700)

# 轉場畫面
def show_message(
    title,
    subtitle,
    bg_color,
    title_color,
    subtitle_color
):

    title_font=pygame.font.Font(
        pixel_font,
        120,
        bold=True
    )

    subtitle_font=pygame.font.Font(
        pixel_font,
        70,
        bold=True
    )

    screen.fill(bg_color)

    title_text=title_font.render(
        title,
        True,
        title_color
    )

    subtitle_text=subtitle_font.render(
        subtitle,
        True,
        subtitle_color
    )

    screen.blit(
        title_text,
        (
            WIDTH//2-title_text.get_width()//2,
            HEIGHT//2-120
        )
    )

    screen.blit(
        subtitle_text,
        (
            WIDTH//2-subtitle_text.get_width()//2,
            HEIGHT//2+40
        )
    )

    pygame.display.update()

    pygame.time.delay(2000)

while True:

    if game_state==GAME_PLAYING:

        elapsed_time=(
            pygame.time.get_ticks()
            -room_start_time
        )/1000

        remaining_time=max(
            0,
            ROOM_TIME_LIMIT-int(elapsed_time)
        )

        # 時間到
        if remaining_time<=0:

            lives-=1

            if lives<=0:

                game_state=GAME_TIMEOUT

            else:

                show_message(
                    "Time's up!!",
                    f"You have {lives} lives left",
                    (180,30,0),
                    (0,0,0),
                    (0,0,0)
                )

                current_view=0
                room_start_time=pygame.time.get_ticks()

    else:

        remaining_time=0

    # Event
    for event in pygame.event.get():

        if event.type==pygame.QUIT:

            pygame.quit()
            sys.exit()

        if event.type==pygame.KEYDOWN and game_state==GAME_PLAYING:

            if event.key==pygame.K_RIGHT:

                current_view=(
                    current_view+1
                )%len(directions)

            elif event.key==pygame.K_LEFT:

                current_view=(
                    current_view-1
                )%len(directions)

            elif event.key==pygame.K_UP:

                current_direction=directions[current_view]

                if current_direction!="back":

                    room_type=room[current_direction]

                    # 生門
                    if room_type=="life":

                        fade_door("life")
                        play_gogo_animation()

                        room=generate_room()

                        current_life_img=random.choice(
                            life_imgs
                        )

                        current_death_img=random.choice(
                            death_imgs
                        )

                        current_view=0

                        room_start_time=pygame.time.get_ticks()

                    # 死門
                    elif room_type=="death":

                        fade_door("death")
                        play_gogo_animation()

                        lives-=1

                        if lives<=0:
                            play_game_over_animation()
                            game_state=GAME_OVER_ANIMATION

                        else:

                            show_message(
                                "You're dead",
                                f"You have {lives} lives left",
                                (0,0,0),
                                (255,0,0),
                                (255,0,0)
                            )

                            current_view=0

                            room_start_time=pygame.time.get_ticks()

    # Draw
    if game_state==GAME_PLAYING:

        draw_room()

                # Timer
        timer_color=(255,0,0) if remaining_time<=10 else (255,255,255)
        border_color=timer_color

        timer_text=timer_font.render(
            f"{remaining_time:02d}",
            True,
            timer_color
        )

        padding=12
        box_x=15
        box_y=15

        box_width=timer_text.get_width()+padding*2
        box_height=timer_text.get_height()+padding*2

        box_surface=pygame.Surface(
            (box_width,box_height)
        )

        box_surface.set_alpha(180)
        box_surface.fill((0,0,0))

        screen.blit(
            box_surface,
            (box_x,box_y)
        )

        pygame.draw.rect(
            screen,
            border_color,
            (box_x,box_y,box_width,box_height),
            2
        )

        screen.blit(
            timer_text,
            (box_x+padding,box_y+padding)
        )


        # 愛心
        for i in range(MAX_LIVES):

            x=WIDTH-48*(MAX_LIVES-i)-10
            y=20

            if i<lives:

                screen.blit(
                    heart_img,
                    (x,y)
                )

            else:

                screen.blit(
                    empty_heart_img,
                    (x,y)
                )


        # 危險紅色邊框
        if remaining_time<=10:

            pulse=abs(
                pygame.time.get_ticks()%1000-500
            )/500

            base_alpha=int(
                150*(1-pulse)
            )

            warning_surface=pygame.Surface(
                (WIDTH,HEIGHT),
                pygame.SRCALPHA
            )

            border_width=100

            for i in range(border_width):

                alpha=int(
                    base_alpha*
                    ((border_width-i)/border_width)
                )

                color=(100,0,0,alpha)

                pygame.draw.rect(
                    warning_surface,
                    color,
                    (
                        i,
                        i,
                        WIDTH-2*i,
                        HEIGHT-2*i
                    ),
                    1
                )

            screen.blit(
                warning_surface,
                (0,0)
            )
    
    elif game_state==GAME_OVER_ANIMATION:
        screen.blit(
            game_over_frames[7],
            (0,0)
        )

  



    elif game_state==GAME_TIMEOUT:

        screen.fill((180,30,0))

        title_font=pygame.font.Font(
            pixel_font,
            120,
            bold=True
        )

        subtitle_font=pygame.font.Font(
            pixel_font,
            70,
            bold=True
        )

        title=title_font.render(
            "Time's up!!",
            True,
            (0,0,0)
        )

        subtitle=subtitle_font.render(
            "Game Over...",
            True,
            (0,0,0)
        )

        screen.blit(
            title,
            (
                WIDTH//2-title.get_width()//2,
                HEIGHT//2-90
            )
        )

        screen.blit(
            subtitle,
            (
                WIDTH//2-subtitle.get_width()//2,
                HEIGHT//2+20
            )
        )


    pygame.display.update()

    clock.tick(10)