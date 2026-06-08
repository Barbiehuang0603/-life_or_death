import pygame

WIDTH = 960
HEIGHT = 540

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
def draw_room(screen,
    current_view,
    world_room,
    world_photos,
    wall_img,
    door_base_img,
    SIGN_X,
    SIGN_Y):
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

def fade_door(screen,
    selected_type,
    current_view,
    world_room,
    world_photos,
    wall_img,
    door_base_img,
    SIGN_X,
    SIGN_Y):
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
            




# =====================================
# 前進動畫
# =====================================
def play_gogo_animation(screen):
    for frame in gogo_frames:
        screen.blit(frame, (0, 0))
        pygame.display.update()
        pygame.time.delay(120)
    pygame.time.delay(300)