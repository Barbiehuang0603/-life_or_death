import random

MAP_SIZE = 5
dungeon_map = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

# 1. 隨機生成路徑
def generate_path():
    start_x, start_y = 0, random.randint(0, MAP_SIZE - 1)
    end_x, end_y = MAP_SIZE - 1, random.randint(0, MAP_SIZE - 1)
    
    current_x, current_y = start_x, start_y
    dungeon_map[current_y][current_x] = 1
    
    while (current_x, current_y) != (end_x, end_y):
        directions = []
        if current_x < MAP_SIZE - 1: directions.append((1, 0))
        if current_y < MAP_SIZE - 1: directions.append((0, 1))
        if current_y > 0: directions.append((0, -1))
        
        dx, dy = random.choice(directions)
        current_x += dx
        current_y += dy
        dungeon_map[current_y][current_x] = 1
        
    return (start_x, start_y), (end_x, end_y)

start_pos, end_pos = generate_path()
player_x, player_y = start_pos

DIRECTIONS = ['北 (▲)', '東 (►)', '南 (▼)', '西 (◄)']
facing_index = 0

print("=== 今際之國：生死門 [追加：禁止回頭機制] ===")
print("操作說明：A(左轉) / D(右轉) / Y(開正前方的門)")
print("🚨 注意：你剛離開的房間會立刻被火焰吞噬，絕對無法回頭！")
print("---------------------------------------------")

while True:
    print(f"\n📍 目前位置：房間 ({player_x}, {player_y})")
    print(f"👀 目前朝向：{DIRECTIONS[facing_index]}")
    
    if (player_x, player_y) == end_pos:
        print("\n🎉 恭喜逃出生天！成功抵達出口大門！")
        break
        
    # [開發者外掛] 檢視地圖
    print("\n[開發者後台地圖視覺檢視]")
    for y in range(MAP_SIZE):
        row_str = ""
        for x in range(MAP_SIZE):
            if x == player_x and y == player_y:
                arrows = ["▲", "►", "▼", "◄"]
                row_str += f" {arrows[facing_index]} "
            elif x == end_pos[0] and y == end_pos[1]:
                row_str += " 🏁 "
            else:
                row_str += f"  {dungeon_map[y][x]} "
        print(row_str)
    
    action = input("\n請輸入指令 (A/D/Y): ").upper()
    
    if action == 'A':
        facing_index = (facing_index - 1) % 4
        print("🔄 你向左轉了 90 度。")
        continue
    elif action == 'D':
        facing_index = (facing_index + 1) % 4
        print("🔄 你向右轉了 90 度。")
        continue
    elif action == 'Y':
        print("🚪 你深吸一口氣，決定打開正前方的門...")
    else:
        print("❌ 無效指令。")
        continue
        
    # 計算前方的格子座標
    next_x, next_y = player_x, player_y
    current_facing = DIRECTIONS[facing_index]
    
    if '北' in current_facing: next_y -= 1
    elif '南' in current_facing: next_y += 1
    elif '東' in current_facing: next_x += 1
    elif '西' in current_facing: next_x -= 1

    # 生死判定
    if not (0 <= next_x < MAP_SIZE and 0 <= next_y < MAP_SIZE):
        print("\n💥 碰！門一推開外面是空的！你墜樓身亡！ GAME OVER")
        break
        
    if dungeon_map[next_y][next_x] == 0:
        # 這裡會同時抓到「原本就錯的門」或是「剛剛走過、已經變成 0 的舊房間」
        print("\n⚡ 嗶——！你開錯了死門（或回頭走向起火的舊房間），被天降雷射射穿身亡！ GAME OVER")
        break
        
    # === 【關鍵改動：破壞舊房間】 ===
    # 在玩家移動過去之前，把當前所在的格子洗成 0 
    dungeon_map[player_y][player_x] = 0 
    print(f"🔥 碰！你身後的房間 ({player_x}, {player_y}) 開始起火，門已被鎖死！")
    
    # 更新玩家座標到新房間
    player_x, player_y = next_x, next_y
    print("✅ 安全通過！你進入了下一間房間。")
    print("------------------------------------------------")