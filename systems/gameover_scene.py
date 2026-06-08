import pygame

WIDTH = 960
HEIGHT = 540

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

timeup_frames=[]
for i in range(1,3):
    img=pygame.image.load(
        f"assets/room/timeup/{i:03d}.png"
    )
    img=pygame.transform.scale(
        img,
        (WIDTH,HEIGHT)
    )
    timeup_frames.append(img)


bgm_gameover = None

played_gameover = False
animation_finished = False
gameover_start_time = None

def play_timeout_game_over(screen):
    global played_gameover
    frame1 = timeup_frames[0]
    frame2 = timeup_frames[1]
    for alpha in range(20,256,2):
        temp = frame1.copy()
        temp.set_alpha(alpha)
        screen.fill((0,0,0))
        screen.blit(temp,(0,0))
        pygame.display.update()
        pygame.event.pump()
        pygame.time.delay(15)
    pygame.event.pump()
    pygame.time.delay(500)
    for alpha in range(0,256,3):
        temp1 = frame1.copy()
        temp1.set_alpha(255-alpha)
        temp2 = frame2.copy()
        temp2.set_alpha(alpha)
        screen.fill((0,0,0))
        screen.blit(temp1,(0,0))
        screen.blit(temp2,(0,0))
        pygame.display.update()
        pygame.event.pump()
        pygame.time.delay(20)
        if not played_gameover:
            bgm_gameover.play()
            played_gameover = True
    pygame.event.pump()
    pygame.time.delay(1000)


def play_game_over_animation(screen):
    global played_gameover
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
    # ===== 006 007 =====
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
    # ===== 007 ~008 =====
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
        if not played_gameover:
            bgm_gameover.play()
            played_gameover = True
    pygame.event.pump()
    pygame.time.delay(700)

def draw_game_over(
        screen,
        game_over_reason,
        GAME_OVER_BY_DEATH,
        GAME_OVER_BY_TIMEOUT
):

    global animation_finished
    global gameover_start_time

    # ===== 死亡 =====
    if game_over_reason == GAME_OVER_BY_DEATH:

        if not animation_finished:

            play_game_over_animation(screen)

            animation_finished = True

            gameover_start_time = pygame.time.get_ticks()

        screen.blit(
            game_over_frames[7],
            (0,0)
        )

    # ===== 超時 =====
    elif game_over_reason == GAME_OVER_BY_TIMEOUT:

        if not animation_finished:

            play_timeout_game_over(screen)

            animation_finished = True

            gameover_start_time = pygame.time.get_ticks()

        screen.blit(
            timeup_frames[1],
            (0,0)
        )

    # ===== 停留兩秒後回傳 True =====
    if (
        animation_finished
        and pygame.time.get_ticks() - gameover_start_time >= 2000
    ):
        return True

    return False

def init_gameover():

    global bgm_gameover

    sound_gameover_path = (
        r"sound\gameover.mp3"
    )

    bgm_gameover = pygame.mixer.Sound(
        sound_gameover_path
    )

def reset_gameover():

    global played_gameover
    global animation_finished
    global gameover_start_time

    played_gameover = False
    animation_finished = False
    gameover_start_time = None
