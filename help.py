import pygame
import sys

def show_help_screen(screen, clock):
    
    WIDTH, HEIGHT = screen.get_size()

    try:
        frames = [
            pygame.image.load("assets/help/Help1.jpg"),
            pygame.image.load("assets/help/Help2.jpg"),
            pygame.image.load("assets/help/Help3.jpg")
        ]
        frames = [pygame.transform.scale(f, (WIDTH, HEIGHT)) for f in frames]
    except pygame.error as e:
        print(f"❌ Help 圖片載入失敗，請檢查檔名大小寫是否正確！錯誤資訊: {e}")
        return 

    current_page = 0
    total_pages = len(frames)
    btn_w, btn_h = 80, 80
    btn_y = HEIGHT - btn_h - 20 
    
    next_btn_rect = pygame.Rect(WIDTH - btn_w - 20, btn_y, btn_w, btn_h) # 右下角
    prev_btn_rect = pygame.Rect(20, btn_y, btn_w, btn_h)                 # 左下角

    # 3. 說明書專屬主迴圈
    showing_help = True
    while showing_help:
        # A. 繪製當前頁面的圖片
        screen.blit(frames[current_page], (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        hovering_btn = False

        # B. 事件監聽
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
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT]:
                    if current_page < total_pages - 1:
                        current_page += 1
                    else:
                        showing_help = False
                elif event.key == pygame.K_LEFT and current_page > 0:
                    current_page -= 1
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
    
