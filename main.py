
import pygame
import sys
from map_generator_wrapper import generate_strict_path, MAP_SIZE
from systems.room import generate_room
from systems.observer_scene import draw_observer_map
from systems.gameover_scene import ( draw_game_over, init_gameover)
from systems.room_scene import( draw_room, fade_door, play_gogo_animation)

from systems.menu import MenuScene
from systems.setting import SettingScene
from systems.story_scenes import StoryScene

from data.intro_data import INTRO_SCENES
from data.outro_data import OUTRO_SCENES
import random

pixel_font = "assets/font/PixelOperator-Bold.ttf"

pygame.init()
pixel_font = "assets/font/PixelOperator-Bold.ttf"

WIDTH=960
HEIGHT=540

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("生死門 - Life or Death")
clock = pygame.time.Clock()

menu = MenuScene(WIDTH, HEIGHT)

setting = SettingScene(WIDTH, HEIGHT)

intro = StoryScene( WIDTH, HEIGHT, INTRO_SCENES)

outro = StoryScene(WIDTH, HEIGHT, OUTRO_SCENES)

# =====================================
# ⭐ 遊戲狀態：加入看地圖階段
# =====================================

GAME_MENU = 0        # 首頁
GAME_SETTING = 1     # 設定
GAME_HELP = 2
GAME_INTRO = 3       # 開頭劇情
GAME_OBSERVING = 4   # 開場看地圖 10 秒
GAME_PLAYING = 5     # 第一人稱遊戲中
GAME_OVER = 6        # 結束
GAME_OUTRO = 7       # 結尾劇情
GAME_CLEAR = 8       # 通關


GAME_OVER_BY_DEATH = 0    # 全部命都用完（走錯門/墜樓）
GAME_OVER_BY_TIMEOUT = 1  # 時間用完（30秒超時）

MAX_LIVES=3
lives=3

game_state = GAME_MENU  #  開局預設為首頁
game_over_reason = None
heart_img=pygame.image.load("assets/ui/heart.png")
empty_heart_img=pygame.image.load("assets/ui/empty_heart.png")

heart_img=pygame.transform.scale(heart_img,(40,40))
empty_heart_img=pygame.transform.scale(empty_heart_img,(40,40))

# =====================================
# 圖片載入
# =====================================

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


SIGN_X = 370
SIGN_Y = 176
# =====================================
# 生成地圖與路徑
# =====================================

dungeon_map, start_pos, end_pos, full_path = generate_strict_path()

current_step_index = 0
player_x, player_y = start_pos
current_view = 0  # 0=front, 1=right, 2=back, 3=left

map_font = pygame.font.SysFont("microsoftjhenghei", 32)
map_font.set_bold(True)

world_photos = {0: None, 1: None, 2: None, 3: None}
world_room = {0: None, 1: None, 2: None, 3: None}

def assign_room_photos():
    global world_photos, world_room
    
    # 1. 每次進新房間，徹底清空大樓 4 個絕對方位的裝潢 (0=北, 1=東, 2=南, 3=西)
    world_photos = {0: None, 1: None, 2: None, 3: None}
    world_room = {0: None, 1: None, 2: None, 3: None}

    if (player_x, player_y) == end_pos:
        return

    # 2. 【正確路徑方位】先找出通往下一步的大樓絕對方向
    next_index = min(current_step_index + 1, len(full_path) - 1)
    target_x, target_y = full_path[next_index]
        
    correct_dir = 0
    if target_y == player_y - 1:   correct_dir = 0  # 下一步在北
    elif target_x == player_x + 1: correct_dir = 1  # 下一步在東
    elif target_y == player_y + 1: correct_dir = 2  # 下一步在南
    elif target_x == player_x - 1: correct_dir = 3  # 下一步在西

    # 3. 【動態來時路】找出你是從大樓的哪個方向走進來的
    from_dir = None  
    if current_step_index > 0:
        prev_x, prev_y = full_path[current_step_index - 1]
        if prev_y == player_y + 1:   from_dir = 2  # 從南邊走過來
        elif prev_y == player_y - 1: from_dir = 0  # 從北邊走過來
        elif prev_x == player_x + 1: from_dir = 1  # 從東邊走過來
        elif prev_x == player_x - 1: from_dir = 3  # 從西邊走過來

        # 普通房間：在來時大樓方位釘上來時大門（back.jpg）
        world_photos[from_dir] = door_base_img
        world_room[from_dir] = "back"

    # 4. 🪙 【視覺欺敵】：隨機抽出一生一死門照片，並擲硬幣決定正確路徑貼哪張
    life_photo = random.choice(life_imgs)
    death_photo = random.choice(death_imgs)
    coin_flip = random.choice([0, 1])
    
    if coin_flip == 0:
        correct_photo = death_photo   # 正確通路貼死門圖
        fake_photo = life_photo       # 詐騙死路貼生門圖
    else:
        correct_photo = life_photo    # 正確通路貼生門圖
        fake_photo = death_photo      # 詐騙死路貼死門圖

    # 正確通路的絕對方位，定死為這扇可以推開的門
    world_photos[correct_dir] = correct_photo
    world_room[correct_dir] = "door"

    # 5. 🎯【核心精準發牌】：找出大樓剩下還空著的絕對方位
    remaining_world_dirs = [d for d in [0, 1, 2, 3] if d != from_dir and d != correct_dir]

    # 不管是哪間房，除了正確門，都必須補上一扇外觀相反的詐騙門，剩下的全部用實心牆塞滿
    leftover_elements = ["fake_door"]
    needed_walls = len(remaining_world_dirs) - 1
    for _ in range(needed_walls):
        leftover_elements.append("wall")

    # 隨機洗牌賸餘元素
    random.shuffle(leftover_elements)

    for i in range(len(remaining_world_dirs)):
        world_d = remaining_world_dirs[i]
        element_type = leftover_elements[i]

        if element_type == "wall":
            world_photos[world_d] = wall_img
            world_room[world_d] = "wall"
        elif element_type == "fake_door":
            world_photos[world_d] = fake_photo
            world_room[world_d] = "door"

    # 6. 安全網
    for d in [0, 1, 2, 3]:
        if world_photos[d] is None:
            world_photos[d] = wall_img
            world_room[d] = "wall"
              
room = generate_room()
assign_room_photos()  # ✅ 在遊戲開始前先把第一間房的門牌照片固定下來
directions = ["front", "right", "back", "left"]

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
init_gameover()

sound_10s_path = r"C:\Users\joooa\OneDrive\桌面\程設專題\-life_or_death\sound\countdown-ten-seconds.mp3"
sound_30s_path = r"C:\Users\joooa\OneDrive\桌面\程設專題\-life_or_death\sound\60-second-countdown.mp3"
sound_5s_path = r"C:\Users\joooa\OneDrive\桌面\程設專題\-life_or_death\sound\countdown-5-to-1.mp3"
observe_10s = pygame.mixer.Sound(sound_10s_path)
bgm_30s = pygame.mixer.Sound(sound_30s_path)
cue_5s = pygame.mixer.Sound(sound_5s_path)
# 狀態鎖：確保在同一個房間/生命週期裡，音效各自只會被 play() 一次
played_10s_observe = False
played_30s_bgm = False
played_5s_cue = False
def reset_room_audio():
    """每次邁入新房間、原地復活、或超時計時重置時呼叫，切斷舊聲音並解開控制鎖"""
    global played_30s_bgm, played_5s_cue
    bgm_30s.stop()
    cue_5s.stop()
    played_30s_bgm = False
    played_5s_cue = False
def stop_all_audio():
    """發生 Game Over 或通關時，一次性切斷所有後台音效"""
    observe_10s.stop()
    bgm_30s.stop()
    cue_5s.stop()
# =====================================
# 計時器設定
# =====================================

ROOM_TIME_LIMIT = 30
OBSERVE_TIME_LIMIT = 10  # ⭐ 新增：地圖展示時間 10 秒

# 統一抓取遊戲剛啟動的時間戳
start_ticks = pygame.time.get_ticks() 
room_start_time = 0

#  同樣改成 Font() 與 set_bold
timer_font = pygame.font.Font(pixel_font, 36)
timer_font.set_bold(True)



# =====================================
# ⭐ 畫出開場地圖（含起點三角形面向）
# =====================================
# main.py 裡面的 draw_observer_map 函式全面優化版




# =====================================
# 轉場動畫
# =====================================
def show_message(title,subtitle,bg_color,title_color,subtitle_color):
    title_font = pygame.font.Font(pixel_font, 120)
    title_font.set_bold(True)

    subtitle_font = pygame.font.Font(pixel_font, 70)
    subtitle_font.set_bold(True)


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

# =====================================
# 終端顯示（上帝視角）
# =====================================
def print_terminal_status():
    print("\033[H\033[J", end="")
    dir_names = ["前方", "右方", "後方", "左方"]
    print("==========================================")
    print("      📊 生死門 - 地圖導覽 📊          ")
    print("==========================================")
    print(f" 📍 當前位置 : ({player_x}, {player_y})")
    print(f" 👀 當前方向 : {dir_names[current_view]}")
    print(f" 🎯 終點座標 : ({end_pos[0]}, {end_pos[1]})")
    
    for y in range(MAP_SIZE):
        row_str = "    "
        for x in range(MAP_SIZE):
            if x == player_x and y == player_y:
                # ✅ 因為箭頭比較寬，前後各留 2 個空格，這樣總寬度才會跟普通格子一樣
                if current_view == 0:
                    row_str += "  ▲  "
                elif current_view == 1:
                    row_str += "  ▶  "
                elif current_view == 2:
                    row_str += "  ▼  "
                elif current_view == 3:
                    row_str += "  ◀  "
            elif x == end_pos[0] and y == end_pos[1]: 
                # ✅ 終點也一樣，前後各留 2 個空格
                row_str += "  🏁  "
            else: 
                # 普通數字前後各留 2 個空格（半形 2 + 1 + 2 = 5 格寬）
                row_str += f"  {dungeon_map[y][x]}  "
        print(row_str)
    print("==========================================\n")

# =====================================
# 主迴圈
# =====================================
while True:

    # ⭐ 1. 看地圖計時邏輯
    if game_state == GAME_OBSERVING:
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        remaining_time = max(0, OBSERVE_TIME_LIMIT - int(elapsed_time-0.5))
        
        if remaining_time <= 10 and not played_10s_observe:
            observe_10s.play()
            played_10s_observe = True
        # ──────────────────────────────────────────

        if remaining_time <= 0:
            observe_10s.stop()
        if remaining_time <= 0:
            # 10 秒到了！切換狀態，並記錄正式開始玩遊戲的時間戳
            game_state = GAME_PLAYING
            reset_room_audio()
            room_start_time = pygame.time.get_ticks()
            print_terminal_status() # 後台也同步列印

    # ⭐ 2. 正式遊戲計時邏輯
    elif game_state == GAME_PLAYING:
        elapsed_time = (pygame.time.get_ticks() - room_start_time) / 1000
        remaining_time = max(0, ROOM_TIME_LIMIT - int(elapsed_time))
        # 🔊 A. 剩餘時間 30 秒到 6 秒之間（前 25 秒）：播放背景倒數
        if remaining_time > 5.8 and not played_30s_bgm:
            bgm_30s.play()
            played_30s_bgm = True
        # 🔊 B. 最後 5 秒瞬間：前半段立刻閉嘴，5秒致命倒數無縫切入！
        if remaining_time <= 5.8 and not played_5s_cue:
            bgm_30s.stop() 
            cue_5s.play()
            played_5s_cue = True
        if remaining_time<=0:
            lives-=1
            if lives<=0:
                stop_all_audio()
                game_over_reason = GAME_OVER_BY_TIMEOUT
                game_state = GAME_OVER
            else:
                reset_room_audio()
                show_message(
                    "Time's up!!",
                    f"You have {lives} lives left",
                    (180,30,0),
                    (0,0,0),
                    (0,0,0)
                )
                player_x, player_y = full_path[current_step_index]
                room_start_time=pygame.time.get_ticks()
    else:
        remaining_time=0
    # =================================
    # Event 鍵盤監聽 (只在 GAME_PLAYING 時有效)
    # =================================
    for event in pygame.event.get():
        if game_state == GAME_MENU:

            result = menu.handle_event(event)

            if result == "PLAY":

                intro.reset()
                game_state = GAME_INTRO

            elif result == "SETTINGS":

                game_state = GAME_SETTING

            elif result == "HELP":

                game_state = GAME_HELP

            elif result == "EXIT":

                pygame.quit()
                sys.exit()

        elif game_state == GAME_SETTING:

            result = setting.handle_event(event)

            if result == "BACK":

                game_state = GAME_MENU

        elif game_state == GAME_INTRO:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    intro.next_scene()

        elif game_state == GAME_OUTRO:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    outro.next_scene()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and game_state == GAME_PLAYING:
            if event.key == pygame.K_RIGHT:
                # 🌟 右轉頭：純粹改變面向數值（0->1->2->3->0），絕對不去動到房間牆壁的照片！
                current_view = (current_view + 1) % 4
                print_terminal_status()
            elif event.key == pygame.K_LEFT:
                # 🌟 左轉頭：純粹改變面向數值
                current_view = (current_view - 1) % 4
                print_terminal_status()
            elif event.key == pygame.K_UP:
                actual_world_dir = current_view
                room_type = world_room[actual_world_dir]
                
                # ─── 🛡️ 第一道防線：回頭與撞牆的防呆裝置 ───
                if room_type == "back":
                    print("\n 後方已被封死，不可回頭！")
                    
                elif room_type == "wall":
                    # ✅ 終極防呆：只要畫面是牆壁，管它大樓內還是大樓外，一律彈回來！
                    # 這樣絕對不會有穿牆破圖、座標變 -1 的風險，玩家也安全不扣血。
                    print("\n🧱 這裡是牆，根本沒有門！")
                    
                else:
                    # ─── 🚪 第二道防線：門的判定（room_type == "door"） ───
                    # 根據玩家目前大樓的絕對面向，計算模擬前進的下一步座標
                    nx, ny = player_x, player_y
                    if current_view == 0:   ny -= 1  # 北
                    elif current_view == 1: nx += 1  # 東
                    elif current_view == 2: ny += 1  # 南
                    elif current_view == 3: nx -= 1  # 西

                    # 🌟 優先判定：推開大樓側邊的「假門」，下一格掉出大樓外！
                    if nx < 0 or nx >= MAP_SIZE or ny < 0 or ny >= MAP_SIZE:
                        # 💀 處決：推開邊緣假門墜樓死亡
                        fade_door(
                            screen,
                            "death",
                            current_view,
                            world_room,
                            world_photos,
                            wall_img,
                            door_base_img,
                            SIGN_X,
                            SIGN_Y
                        )
                        play_gogo_animation(screen)
                        lives -= 1
                        
                        if lives <= 0:
                            stop_all_audio()
                            game_over_reason = GAME_OVER_BY_DEATH
                            game_state = GAME_OVER
                        else:
                            reset_room_audio()
                            show_message(
                                    "You're dead",
                                    f"You have {lives} lives left",
                                    (0,0,0), (255,0,0), (255,0,0)
                            )
                            
                            player_x, player_y = full_path[current_step_index] # 確保座標鎖在對的格子
                        room_start_time = pygame.time.get_ticks()

                    # 🌟 常規判定：還在大樓內，檢查 C 語言地圖是 1 還是 0
                    else:
                        if dungeon_map[ny][nx] == 1:
                            # ─── 【生路：前進下一間房】 ───
                            fade_door(
                                screen,
                                "life",
                                current_view,
                                world_room,
                                world_photos,
                                wall_img,
                                door_base_img,
                                SIGN_X,
                                SIGN_Y
                            )
                            play_gogo_animation(screen)
                            
                            current_step_index += 1
                            player_x, player_y = full_path[current_step_index]

                            if current_step_index >= len(full_path)-1:

                                stop_all_audio()

                                outro.reset()

                                game_state = GAME_OUTRO

                            else:

                                reset_room_audio()
                                assign_room_photos()
                                room_start_time = pygame.time.get_ticks()
                                print_terminal_status()
                        else:
                            # ─── 【死路：踩進大樓內側的錯誤門】 ───
                            fade_door(
                                screen,
                                "death",
                                current_view,
                                world_room,
                                world_photos,
                                wall_img,
                                door_base_img,
                                SIGN_X,
                                SIGN_Y
                            )
                            play_gogo_animation(screen)
                            lives -= 1
                            if lives <= 0:
                                stop_all_audio()
                                game_over_reason = GAME_OVER_BY_DEATH
                                game_state = GAME_OVER
                            else:
                                reset_room_audio()
                                show_message(
                                    "You're dead",
                                    f"You have {lives} lives left",
                                    (0,0,0), (255,0,0), (255,0,0)
                                )
                                player_x, player_y = full_path[current_step_index]
                            room_start_time = pygame.time.get_ticks()
                            
    # =================================
    # Draw 渲染畫面
    # =================================
    if game_state == GAME_MENU:

        menu.draw(screen)

    elif game_state == GAME_SETTING:

        setting.draw(screen)

    elif game_state == GAME_INTRO:

        intro.update()
        intro.draw(screen)

        if intro.finished:

            start_ticks = pygame.time.get_ticks()
            game_state = GAME_OBSERVING
    
    elif game_state == GAME_OBSERVING:
        draw_observer_map(
            remaining_time,
            screen,
            HEIGHT,
            MAP_SIZE,
            start_pos,
            end_pos,
            dungeon_map,
            map_font,
            timer_font
        )

    elif game_state == GAME_PLAYING:
        draw_room(
            screen,
            current_view,
            world_room,
            world_photos,
            wall_img,
            door_base_img,
            SIGN_X,
            SIGN_Y
        )

        timer_color = (255, 0, 0) if remaining_time <= 10 else (255, 255, 255)
        border_color = (255, 0, 0) if remaining_time <= 10 else (255, 255, 255)

        timer_text = timer_font.render(f"{remaining_time:02d}", True, timer_color)
        padding = 12
        box_x, box_y = 15, 15
        box_width, box_height = timer_text.get_width() + padding * 2, timer_text.get_height() + padding * 2

        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(180)
        box_surface.fill((0, 0, 0))
        screen.blit(box_surface, (box_x, box_y))

        pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2)
        screen.blit(timer_text, (box_x + padding, box_y + padding))

        for i in range(MAX_LIVES):
            x = WIDTH - 48 * (MAX_LIVES - i) - 10
            y = 20
            if i < lives:
                screen.blit(heart_img, (x, y))
            else:
                screen.blit(empty_heart_img, (x, y))

        # 危險紅色閃爍邊框
        if remaining_time <= 10:
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
            base_alpha = int(150 * (1 - pulse))

            warning_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            border_width = 100

            for i in range(border_width):
                alpha = int(base_alpha * ((border_width - i) / border_width))
                color = (100, 0, 0, alpha)
                pygame.draw.rect(warning_surface, color, (i, i, WIDTH - 2 * i, HEIGHT - 2 * i), 1)

            screen.blit(warning_surface, (0, 0))

    elif game_state == GAME_OVER:

        draw_game_over(
            screen,
            game_over_reason,
            GAME_OVER_BY_DEATH,
            GAME_OVER_BY_TIMEOUT
        )

    elif game_state == GAME_OUTRO:
        outro.update()
        outro.draw(screen)

        if outro.finished:
           game_state = GAME_MENU    

    pygame.display.update()
    clock.tick(30)