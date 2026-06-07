
import pygame
import sys
from map_generator_wrapper import generate_strict_path, MAP_SIZE
from systems.room import generate_room
import random

pixel_font = "assets/font/PixelOperator-Bold.ttf"

pygame.init()
pixel_font = "assets/font/PixelOperator-Bold.ttf"

WIDTH=960
HEIGHT=540

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("生死門 - Life or Death")
clock = pygame.time.Clock()

# =====================================
# ⭐ 遊戲狀態：加入看地圖階段
# =====================================

GAME_OBSERVING = 0  # 階段 0：開場看地圖 10 秒
GAME_PLAYING = 1    # 階段 1：第一人稱遊戲中
GAME_OVER = 2       # 階段 2：結束
GAME_CLEAR = 3      # 階段 3：通關
GAME_OVER_BY_DEATH = 0    # 全部命都用完（走錯門/墜樓）
GAME_OVER_BY_TIMEOUT = 1  # 時間用完（30秒超時）

MAX_LIVES=3
lives=3

game_state = GAME_OBSERVING  #  開局預設為看地圖狀態
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

sound_10s_path = r"C:\Barbie\computerprogramming\project\-life_or_death\sound\countdown-ten-seconds.mp3"
sound_30s_path = r"C:\Barbie\computerprogramming\project\-life_or_death\sound\60-second-countdown.mp3"
sound_5s_path = r"C:\Barbie\computerprogramming\project\-life_or_death\sound\countdown-5-to-1.mp3"
sound_gameover_path = r"C:\Barbie\computerprogramming\project\-life_or_death\sound\gameover.mp3"
observe_10s = pygame.mixer.Sound(sound_10s_path)
bgm_30s = pygame.mixer.Sound(sound_30s_path)
cue_5s = pygame.mixer.Sound(sound_5s_path)
bgm_gameover = pygame.mixer.Sound(sound_gameover_path)
# 狀態鎖：確保在同一個房間/生命週期裡，音效各自只會被 play() 一次
played_10s_observe = False
played_30s_bgm = False
played_5s_cue = False
played_gameover = False
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

def draw_observer_map(remaining_time):
    screen.fill((30, 30, 30)) # 深灰色背景
    
    grid_size = 75  
    # 稍微把左邊的地圖往左挪一點，留更多空間給右邊的文字
    start_draw_x = 80 
    start_draw_y = (HEIGHT - (MAP_SIZE * grid_size)) // 2
    
    # ─── 繪製 5x5 地圖 ───
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            rect = pygame.Rect(start_draw_x + x * grid_size, start_draw_y + y * grid_size, grid_size, grid_size)
            
            if (x, y) == start_pos:
                pygame.draw.rect(screen, (150, 40, 20), rect) # 起點
                p1 = (rect.centerx, rect.top + 15)              
                p2 = (rect.left + 15, rect.bottom - 15)          
                p3 = (rect.right - 15, rect.bottom - 15)         
                pygame.draw.polygon(screen, (255, 255, 255), [p1, p2, p3])
                text = map_font.render("起", True, (0, 0, 0))
                screen.blit(text, (rect.x + (grid_size - text.get_width())//2, rect.y + (grid_size - text.get_height())//2 + 10))
                
            elif (x, y) == end_pos:
                pygame.draw.rect(screen, (0, 100, 180), rect) # 終點
                text = map_font.render("終", True, (255, 255, 255))
                screen.blit(text, (rect.x + (grid_size - text.get_width())//2, rect.y + (grid_size - text.get_height())//2))
            elif dungeon_map[y][x] == 1:
                pygame.draw.rect(screen, (220, 150, 0), rect) # 通路
            else:
                pygame.draw.rect(screen, (60, 60, 60), rect) # 牆壁
                
            pygame.draw.rect(screen, (150, 150, 150), rect, 1)
            
    # ─── 🚀 右側文字排版優化 🚀 ───
    
    # 為了防止超出邊界，我們在這裡建立一個專門給提示台詞用的小一號字體
    hint_font = pygame.font.SysFont("microsoftjhenghei", 24)
    hint_font.set_bold(True)
    if remaining_time > 5:
        status_color = (255, 255, 255)
        hint_color = (200, 200, 200)
        time_color = (0, 255, 0)
        title_str = "【 遊戲初始化：地圖掃描 】"
        hint_str1 = "白色 ▲ 為初始朝向。選錯門即刻處決。"
        hint_str2 = "把這條唯一的通路烙印在腦袋裡..."
    elif remaining_time > 3:
        status_color = (255, 128, 0)   
        hint_color = (255, 128, 0)
        time_color = (255, 128, 0)
        title_str = "【 警告：掃描即將結束 】"
        hint_str1 = "天界雷射已就位，正在鎖定玩家位置。"
        hint_str2 = "時間不夠了...你真的全部記住了嗎？！"
    else:
        is_blink = (pygame.time.get_ticks() % 400) > 200
        status_color = (255, 0, 0) if is_blink else (100, 0, 0)
        hint_color = (255, 50, 50)
        time_color = (255, 0, 0)
        title_str = "【 EXTREME WARNING 】"
        hint_str1 = "系統即將強制關閉！準備直面生死！"
        hint_str2 = "倒數結束後，回頭的路將化為火海。"

    # 渲染文字
    title_surface = map_font.render(title_str, True, status_color)
    hint1_surface = hint_font.render(hint_str1, True, hint_color) # 改用 hint_font
    hint2_surface = hint_font.render(hint_str2, True, (150, 150, 150)) # 改用 hint_font
    
    time_label = f" TIME: {remaining_time:02d}s " if remaining_time <= 3 else f"TIME: {remaining_time:02d}s"
    time_surface = timer_font.render(time_label, True, time_color)
    
    # 將文字起點往左移動到 500 的位置，確保右邊有 460 像素的超大安全空間不越界
    text_start_x = 500
    screen.blit(title_surface, (text_start_x, HEIGHT // 2 - 110))
    screen.blit(hint1_surface, (text_start_x, HEIGHT // 2 - 50))
    screen.blit(hint2_surface, (text_start_x, HEIGHT // 2 - 10))
    screen.blit(time_surface, (text_start_x, HEIGHT // 2 + 50))
# =====================================
# 前進動畫
# =====================================
gogo_frames = []
for i in range(1, 6):
    img = pygame.transform.scale(pygame.image.load(f"assets/room/gogo/{i:03d}.jpg"), (WIDTH, HEIGHT))
    gogo_frames.append(img)

# =====================================
# 畫房間
# =====================================
def draw_room():
    # 🌟 真正的第一人稱物理查表：你面向哪個絕對方位，就直接畫那面牆的裝潢！
    # 0=北, 1=東, 2=南, 3=西
    actual_world_dir = current_view 

    room_type = world_room[actual_world_dir]
    
    if room_type == "wall":
        # 🧱 只有這面牆是水泥死牆，才畫牆壁
        screen.blit(wall_img, (0, 0))
    elif room_type == "back":
        # 🚪 只有在來時路的方位，才畫乾淨的來時大門（不貼生死牌）
        screen.blit(door_base_img, (0, 0))
    else:
        # 🃏 如果是門（door），則在門底圖上疊加貼上生門/死門欺敵圖片！
        screen.blit(door_base_img, (0, 0))
        if world_photos[actual_world_dir] is not None:
            screen.blit(world_photos[actual_world_dir], (SIGN_X, SIGN_Y))

def fade_door(selected_type):
    # 動態開門動畫也完全比照辦理
    actual_world_dir = current_view
    room_type = world_room[actual_world_dir]
    
    if room_type == "back":
        original_img = door_base_img.copy()
        for alpha in range(255, -1, -4):
            screen.blit(wall_img, (0, 0))
            temp = original_img.copy()
            temp.set_alpha(alpha)
            screen.blit(temp, (0, 0))
            pygame.display.update()
            pygame.time.delay(15)
    else:
        if world_photos[actual_world_dir] is not None:
            original_img = world_photos[actual_world_dir].copy()
            for alpha in range(255, -1, -4):
                screen.blit(door_base_img, (0, 0))
                temp = original_img.copy()
                temp.set_alpha(alpha)
                screen.blit(temp, (SIGN_X, SIGN_Y))
                pygame.display.update()
                pygame.time.delay(15)
            
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

def play_timeout_game_over():
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


def play_game_over_animation():
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

# =====================================
# 前進動畫
# =====================================
def play_gogo_animation():
    for frame in gogo_frames:
        screen.blit(frame, (0, 0))
        pygame.display.update()
        pygame.time.delay(120)
    pygame.time.delay(300)

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
                        fade_door("death")
                        play_gogo_animation()
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
                            fade_door("life") 
                            play_gogo_animation()
                            
                            if current_step_index + 1 >= len(full_path):
                                stop_all_audio()
                                game_state = GAME_CLEAR
                            else:
                                current_step_index += 1
                                player_x, player_y = full_path[current_step_index] # 正式移過去
                                
                                # 到了新房間，重新發照片固定 東西南北 裝潢
                                reset_room_audio()
                                assign_room_photos()
                                room_start_time = pygame.time.get_ticks() 
                                print_terminal_status()
                        else:
                            # ─── 【死路：踩進大樓內側的錯誤門】 ───
                            fade_door("death")
                            play_gogo_animation()
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
    if game_state == GAME_OBSERVING:
        draw_observer_map(remaining_time)

    elif game_state == GAME_PLAYING:
        draw_room()

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
        if game_over_reason == GAME_OVER_BY_DEATH:
            if game_over_reason is not None:
                play_game_over_animation()
                game_over_reason = None 
            screen.blit(game_over_frames[7], (0, 0))

        elif game_over_reason == GAME_OVER_BY_TIMEOUT:
            if game_over_reason is not None:
                play_timeout_game_over()
                game_over_reason = None
            screen.blit(timeup_frames[1], (0, 0))
                 
    elif game_state == GAME_CLEAR:
        screen.fill((0, 0, 0))
        clear_font = pygame.font.SysFont("Courier New", 48, bold=True)
        clear_text = clear_font.render("CLEAR!", True, (0, 255, 0))
        screen.blit(clear_text, (WIDTH // 2 - clear_text.get_width() // 2, HEIGHT // 2 - clear_text.get_height() // 2))

    pygame.display.update()
    clock.tick(30)