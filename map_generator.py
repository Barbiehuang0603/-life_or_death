# map_generator.py
import random

MAP_SIZE = 5

def count_turns(path):
    """計算這條路徑總共轉彎了幾次"""
    if len(path) < 3:
        return 0
    turns = 0
    for i in range(1, len(path) - 1):
        prev_pt = path[i-1]
        curr_pt = path[i]
        next_pt = path[i+1]
        
        dir1_x, dir1_y = curr_pt[0] - prev_pt[0], curr_pt[1] - prev_pt[1]
        dir2_x, dir2_y = next_pt[0] - curr_pt[0], next_pt[1] - curr_pt[1]
        
        if (dir1_x, dir1_y) != (dir2_x, dir2_y):
            turns += 1
    return turns

def generate_strict_path():
    """生成『絕對唯一通路』『絕無捷徑』且『至少三轉彎』的迷宮"""
    
    # 邊界起點名單
    border_positions = []
    for i in range(MAP_SIZE):
        border_positions.append((i, 0))
        border_positions.append((i, MAP_SIZE - 1))
        if i != 0 and i != MAP_SIZE - 1:
            border_positions.append((0, i))
            border_positions.append((MAP_SIZE - 1, i))
            
    while True:
        start_x, start_y = random.choice(border_positions)
        path = [(start_x, start_y)]
        visited = set(path)
        
        curr_x, curr_y = start_x, start_y
        stuck = False
        
        # 預期長度：既然不能有捷徑，在5x5裡通常會走 7~10 格
        target_length = random.randint(7, 10)
        
        for _ in range(target_length):
            possible_moves = []
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = curr_x + dx, curr_y + dy
                
                # 基本檢查：必須在大樓內，且沒走過
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and (nx, ny) not in visited:
                    
                    # ⭐ 關鍵防捷徑檢查：這格 nx, ny 的「四周」
                    # 除了牠走過來的上一格 (curr_x, curr_y) 之外，絕對不能碰觸到任何其他已經是 1 的路徑格！
                    adjacent_path_count = 0
                    for adj_dx, adj_dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ax, ay = nx + adj_dx, ny + adj_dy
                        if (ax, ay) in visited:
                            adjacent_path_count += 1
                    
                    # 如果四周碰到的舊路徑格 > 1 (代表除了來時路，還碰到了別的舊路)，走過去就會變捷徑！
                    # 所以只有當鄰近舊路徑只有1個時，這格才安全，牆壁才不會破
                    if adjacent_path_count <= 1:
                        possible_moves.append((nx, ny))
            
            if not possible_moves:
                stuck = True
                break # 撞進死胡同（被自己堵死），重來
                
            curr_x, curr_y = random.choice(possible_moves)
            path.append((curr_x, curr_y))
            visited.add((curr_x, curr_y))
            
        if stuck:
            continue
            
        # 檢查轉彎次數是否符合標準 (>=3)
        if count_turns(path) >= 3:
            end_pos = path[-1]
            
            # 生成矩陣地圖
            dungeon_map = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
            for x, y in path:
                dungeon_map[y][x] = 1
                
            return dungeon_map, (start_x, start_y), end_pos, path