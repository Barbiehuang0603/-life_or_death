# main.py
import pygame
import sys
import random
from map_generator import generate_strict_path, MAP_SIZE

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 683
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("今際之國：生死門 (按鍵即時刷新版)")

# 載入四張照片
img_come = pygame.transform.scale(pygame.image.load("come.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
img_empty = pygame.transform.scale(pygame.image.load("empty.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
img_life = pygame.transform.scale(pygame.image.load("life.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
img_death = pygame.transform.scale(pygame.image.load("death.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))

# 取得符合嚴格條件的隨機地圖資料與路徑清單
dungeon_map, start_pos, end_pos, full_path = generate_strict_path()

current_step_index = 0
player_x, player_y = start_pos
facing = 0  # 0=北, 1=東, 2=南, 3=西

room_visual_configs = {}

def get_room_visual_type(step_idx, check_facing):
    config_key = (step_idx, check_facing)
    if config_key in room_visual_configs:
        return room_visual_configs[config_key]
        
    curr_pt = full_path[step_idx]
    
    if step_idx > 0:
        prev_pt = full_path[step_idx - 1]
        back_dx, back_dy = prev_pt[0] - curr_pt[0], prev_pt[1] - curr_pt[1]
        expected_back_facing = -1
        if back_dx == 0 and back_dy == -1: expected_back_facing = 0
        elif back_dx == 1 and back_dy == 0: expected_back_facing = 1
        elif back_dx == 0 and back_dy == 1: expected_back_facing = 2
        elif back_dx == -1 and back_dy == 0: expected_back_facing = 3
        
        if check_facing == expected_back_facing:
            room_visual_configs[config_key] = ('come', "來時路 (come.jpg) ❌")
            return room_visual_configs[config_key]

    next_pt = full_path[step_idx + 1] if step_idx < len(full_path) - 1 else None
    correct_facing = -1
    if next_pt:
        go_dx, go_dy = next_pt[0] - curr_pt[0], next_pt[1] - curr_pt[1]
        if go_dx == 0 and go_dy == -1: correct_facing = 0
        elif go_dx == 1 and go_dy == 0: correct_facing = 1
        elif go_dx == 0 and go_dy == 1: correct_facing = 2
        elif go_dx == -1 and go_dy == 0: correct_facing = 3

    all_facings = [0, 1, 2, 3]
    used_facings = []
    
    if step_idx > 0:
        used_facings.append(expected_back_facing)
    else:
        used_facings.append(2)
        
    if next_pt:
        used_facings.append(correct_facing)
        
    remaining_facings = [f for f in all_facings if f not in used_facings]
    
    if check_facing == correct_facing:
        label = random.choice(['life', 'death'])
        text = f"通道 (真實出口是這個方向，門貼的是: {'生門 👼' if label=='life' else '死門 💀'})"
        room_visual_configs[config_key] = (label, text)
    else:
        if len(remaining_facings) > 0 and check_facing == remaining_facings[0]:
            room_visual_configs[config_key] = ('empty', "純牆壁 (empty.jpg) 🧱")
        else:
            if next_pt:
                correct_label = get_room_visual_type(step_idx, correct_facing)[0]
                opposite_label = 'death' if correct_label == 'life' else 'life'
                room_visual_configs[config_key] = (opposite_label, f"通道 (這是假出口 ❌，貼的是: {'生門 👼' if opposite_label=='life' else '死門 💀'})")
            else:
                room_visual_configs[config_key] = ('empty', "純牆壁 (empty.jpg) 🧱")
                
    return room_visual_configs[config_key]

def print_terminal_status(status_text):
    print("\033[H\033[J", end="") 
    dir_names = ["北 (▲)", "東 (►)", "南 (▼)", "西 (◄)"]
    arrows = ["▲", "►", "▼", "◄"]
    
    print("==========================================")
    print("      📊 今際之國：生死門後台控制台 📊     ")
    print("==========================================")
    print(f" 📍 當前位置 : 房間 ({player_x}, {player_y})")
    print(f" 👀 當前朝向 : {dir_names[facing]}")
    print(f" 🚪 眼前畫面 : {status_text}")
    print(f" 🎯 終點座標 : ({end_pos[0]}, {end_pos[1]})")
    print("==========================================")
    print("               🗺️ 上帝視角 🗺️              ")
    print("       ( 1:單向活路軌跡 | 0:死牆牆壁 )       ")
    print("------------------------------------------")
    
    for y in range(MAP_SIZE):
        row_str = "    "
        for x in range(MAP_SIZE):
            if x == player_x and y == player_y:
                row_str += f" [{arrows[facing]}] "
            elif x == end_pos[0] and y == end_pos[1]:
                row_str += "  🏁  "
            else:
                row_str += f"   {dungeon_map[y][x]}  "
        print(row_str)
    print("==========================================\n")

font = pygame.font.SysFont("Microsoft JhengHei", 30)

# 開局初始化首次列印
img_type, status_text = get_room_visual_type(current_step_index, facing)
print_terminal_status(status_text)

running = True
while running:
    # 讀取當前朝向的視覺貼圖並畫在 Pygame 上
    img_type, status_text = get_room_visual_type(current_step_index, facing)
    
    if img_type == 'come': screen.blit(img_come, (0, 0))
    elif img_type == 'empty': screen.blit(img_empty, (0, 0))
    elif img_type == 'life': screen.blit(img_life, (0, 0))
    elif img_type == 'death': screen.blit(img_death, (0, 0))

    info_surface = font.render(f"位置: ({player_x}, {player_y})", True, (255, 255, 255))
    screen.blit(info_surface, (15, 15))
    pygame.display.update()

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_a:     # A 左轉
                facing = (facing - 1) % 4
                # ⭐ 關鍵修正：轉向後，立刻強迫程式重新去抓新方向的文字，並馬上刷新 Terminal
                _, updated_text = get_room_visual_type(current_step_index, facing)
                print_terminal_status(updated_text)
                
            elif event.key == pygame.K_d:   # D 右轉
                facing = (facing + 1) % 4
                # ⭐ 關鍵修正：轉向後，立刻強迫程式重新去抓新方向的文字，並馬上刷新 Terminal
                _, updated_text = get_room_visual_type(current_step_index, facing)
                print_terminal_status(updated_text)
                
            elif event.key == pygame.K_y:   # Y 開門
                dir_chars = ['N', 'E', 'S', 'W']
                current_dir_char = dir_chars[facing]
                next_x, next_y = player_x, player_y
                if current_dir_char == 'N': next_y -= 1
                elif current_dir_char == 'S': next_y += 1
                elif current_dir_char == 'E': next_x += 1
                elif current_dir_char == 'W': next_x -= 1
                
                next_correct_pt = full_path[current_step_index + 1] if current_step_index < len(full_path) - 1 else None
                
                if img_type == 'come':
                    print("\n💥 GAME OVER：回頭路是致命火海！")
                    running = False
                    break
                elif img_type == 'empty':
                    print("\n🧱 咚！這是一面死牆，沒門可開！")
                    continue
                elif next_correct_pt and [next_x, next_y] == list(next_correct_pt):
                    print("\n✅ 方向正確！成功進入下一間房。")
                    current_step_index += 1
                    player_x, player_y = next_x, next_y
                    
                    # ⭐ 關鍵修正：成功進新房間後，以新狀態刷新 Terminal
                    _, updated_text = get_room_visual_type(current_step_index, facing)
                    print_terminal_status(updated_text)
                    
                    if (player_x, player_y) == end_pos:
                        print("\n🏁 🎉 CLEAR：成功抵達終點！你活下來了！")
                        running = False
                        break
                else:
                    print("\n⚡ GAME OVER：開錯門了！天降雷射射穿身亡！")
                    running = False
                    break

pygame.quit()
sys.exit()