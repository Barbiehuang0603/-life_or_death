import pygame
import sys

def show_help_screen(screen, clock):
    
    WIDTH, HEIGHT = screen.get_size()

    # 1. 載入 assets/help/ 資料夾路徑下的三張說明照片
    try:
        frames = [
            pygame.image.load("assets/help/Help1.jpg"),
            pygame.image.load("assets/help/Help2.jpg"),
            pygame.image.load("assets/help/Help3.jpg")
        ]
        frames = [pygame.transform.scale(f, (WIDTH, HEIGHT)) for f in frames]
    except pygame.error as e:
        print(f"❌ assets/help/ 底下的圖片載入失敗！錯誤資訊: {e}")
        return 

    current_page = 0
    total_pages = len(frames)
    
    # 2. 定義左右下角黃色按鈕的點擊感應範圍 (與你圖片上的按鈕對齊)
    btn_w, btn_h = 80, 80
    btn_y = HEIGHT - btn_h - 20 
    next_btn_rect = pygame.Rect(WIDTH - btn_w - 20, btn_y, btn_w, btn_h) 
    prev_btn_rect = pygame.Rect(20, btn_y, btn_w, btn_h)                 

    # 🌟 3. 新增：初始化提示字的像素字體與內容
    # 延用你們專案的字型，字體大小設為 24 級字，看起來精緻不突兀
    try:
        hint_font = pygame.font.Font("assets/font/PixelOperator-Bold.ttf", 24)
    except pygame.error:
        # 防呆：如果抓不到該字型，就用系統預設像素風字體
        hint_font = pygame.font.SysFont("Courier New", 20, bold=True)
        
    # 渲染出提示字串：亮灰色 (200, 200, 200)，帶有黑色半透明底框增加辨識度
    hint_surface = hint_font.render("[Return / ESC] Return to Menu", True, (200, 200, 200))
    
    # 計算提示字的位置：讓它完美水平置中，並且貼在畫面最底部（安全區）
    hint_x = WIDTH // 2 - hint_surface.get_width() // 2
    hint_y = HEIGHT - hint_surface.get_height() - 25

    # 4. 說明書專屬主迴圈
    showing_help = True
    while showing_help:
        # A. 繪製當前頁面的底圖
        screen.blit(frames[current_page], (0, 0))
        
        # 🌟 B. 新增：在畫面上疊加「Return 提示字」與微黑底框（手感與細節拉滿！）
        # 先畫一個細長的黑色半透明背景條，確保提示字在任何暗色或亮色牆壁上都看得清
        bg_rect = pygame.Rect(hint_x - 10, hint_y - 5, hint_surface.get_width() + 20, hint_surface.get_height() + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150) # 透明度
        bg_surface.fill((0, 0, 0)) # 純黑底
        screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
        
        # 把提示文字印上去
        screen.blit(hint_surface, (hint_x, hint_y))

        mouse_pos = pygame.mouse.get_pos()
        hovering_btn = False

        # C. 事件監聽
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if next_btn_rect.collidepoint(event.pos):
                    if current_page < total_pages - 1:
                        current_page += 1
                    else:
                        showing_help = False 
                elif prev_btn_rect.collidepoint(event.pos) and current_page > 0:
                    current_page -= 1

            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RIGHT]:
                    if current_page < total_pages - 1:
                        current_page += 1
                    else:
                        showing_help = False
                elif event.key == pygame.K_LEFT and current_page > 0:
                    current_page -= 1
                
                # 鍵盤監聽：按 Return 或 ESC 直接退出
                elif event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                    showing_help = False

        # 滑鼠懸停變小手手
        if next_btn_rect.collidepoint(mouse_pos):
            hovering_btn = True
        elif prev_btn_rect.collidepoint(mouse_pos) and current_page > 0:
            hovering_btn = True

        if hovering_btn:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.update()
        clock.tick(30)

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

# 🌟 獨立測試開關（單獨執行 python help.py 時可用）
if __name__ == "__main__":
    pygame.init()
    test_screen = pygame.display.set_mode((960, 540))
    pygame.display.set_caption("Help 畫面文字測試中...")
    test_clock = pygame.time.Clock()
    show_help_screen(test_screen, test_clock)
    pygame.quit()