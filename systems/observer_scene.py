import pygame

def draw_observer_map(remaining_time,
        screen,
        height,
        map_size,
        start_pos,
        end_pos,
        dungeon_map,
        map_font,
        timer_font
):
    screen.fill((30, 30, 30)) # 深灰色背景
    
    grid_size = 75  
    # 稍微把左邊的地圖往左挪一點，留更多空間給右邊的文字
    start_draw_x = 80 
    start_draw_y = (height - (map_size * grid_size)) // 2
    
    # ─── 繪製 5x5 地圖 ───
    for y in range(map_size):
        for x in range(map_size):
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
    screen.blit(title_surface, (text_start_x, height // 2 - 110))
    screen.blit(hint1_surface, (text_start_x, height // 2 - 50))
    screen.blit(hint2_surface, (text_start_x, height // 2 - 10))
    screen.blit(time_surface, (text_start_x, height // 2 + 50))