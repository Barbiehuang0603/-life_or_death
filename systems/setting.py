import pygame
import data.player_data as player_data


class SettingScene:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.selected = 0
        self.input_mode = False

        self.items = [
            "Name",
            "Text Speed",
            "BGM Volume",
            "Return"
        ]
        
        pixel_font_path = "assets/font/PixelOperator-Bold.ttf"

        self.speed_values = [20, 40, 70]
        self.speed_names = ["Fast", "Normal", "Slow"]

        self.title_font = pygame.font.Font(
            pixel_font_path,
            64 
        )

        self.label_font = pygame.font.Font(
            pixel_font_path,
            32
        )

        self.value_font = pygame.font.Font(
            pixel_font_path,
            30
        )

        self.small_font = pygame.font.Font(
            pixel_font_path,
            24
        )

        self.white = (230, 230, 230)
        self.gray = (150, 150, 150)
        self.dark_red = (139, 0, 0)

        self.background = pygame.image.load(
            "assets/room/gogo/004.jpg"
        )

        self.background = pygame.transform.scale(
            self.background,
            (width, height)
        )
        self.volume_x1 = 500
        self.volume_x2 = 700
        self.volume_y = 370
        
        self.item_rects = []
        self.speed_rects = []
        self.speed_label_rect = pygame.Rect(0,0,0,0)
        self.volume_label_rect = pygame.Rect(0,0,0,0)
        self.return_rect = pygame.Rect(0,0,0,0)
        self.dragging_volume = False

    def handle_event(self, event):
        # 🌟 核心修改 1：移除一刀切的 KEYDOWN 限制，全面擁抱滑鼠事件！
        
        # ==========================
        # 1. 滑鼠移動懸停事件 (MOUSEMOTION)
        # ==========================
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # 拖曳音量條中
            if self.dragging_volume:
                x = max(self.volume_x1, min(mouse_pos[0], self.volume_x2))
                player_data.BGM_VOLUME = int((x - self.volume_x1) / (self.volume_x2 - self.volume_x1) * 100)
                return "NONE"

            # 偵測選取 Name
            if self.item_rects and (self.item_rects[0].collidepoint(mouse_pos) or self.item_rects[1].collidepoint(mouse_pos)):
                self.selected = 0
            
            # 偵測選取 Text Speed
            if self.speed_label_rect.collidepoint(mouse_pos):
                self.selected = 1
            for rect in self.speed_rects:
                if rect.collidepoint(mouse_pos):
                    self.selected = 1

            # 偵測選取 BGM Volume
            if self.volume_label_rect.collidepoint(mouse_pos):
                self.selected = 2
            if self.volume_x1 <= mouse_pos[0] <= self.volume_x2 and abs(mouse_pos[1] - self.volume_y) <= 15:
                self.selected = 2
            
            # 偵測選取 Return
            if self.return_rect and self.return_rect.collidepoint(mouse_pos):
                self.selected = 3

        # ==========================
        # 2. 滑鼠點擊事件 (MOUSEBUTTONDOWN)
        # ==========================
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                
                # 點擊 Name 進入輸入模式
                if self.item_rects and (self.item_rects[0].collidepoint(mouse_pos) or self.item_rects[1].collidepoint(mouse_pos)):
                    self.selected = 0
                    self.input_mode = True
                    return "NONE"
                
                # 點擊 Text Speed 切換速度
                for i, rect in enumerate(self.speed_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected = 1
                        player_data.TEXT_SPEED = self.speed_values[i]
                        return "NONE"
                
                # 點擊音量條本體
                if (self.volume_x1 <= mouse_pos[0] <= self.volume_x2 and abs(mouse_pos[1] - self.volume_y) <= 15) or self.volume_label_rect.collidepoint(mouse_pos):
                    self.selected = 2
                    if self.volume_x1 <= mouse_pos[0] <= self.volume_x2:
                        player_data.BGM_VOLUME = int((mouse_pos[0] - self.volume_x1) / (self.volume_x2 - self.volume_x1) * 100)
                
                # 點擊音量滑鈕開始拖曳
                knob_x = self.volume_x1 + (self.volume_x2 - self.volume_x1) * player_data.BGM_VOLUME / 100
                if abs(mouse_pos[0] - knob_x) <= 15 and abs(mouse_pos[1] - self.volume_y) <= 15:
                    self.dragging_volume = True
                
                # 點擊 Return 退回選單
                if self.return_rect and self.return_rect.collidepoint(mouse_pos):
                    self.selected = 3
                    return "BACK"

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_volume = False

        # ==========================
        # 3. 鍵盤事件分流 (原本的打字與設定機制)
        # ==========================
        elif event.type == pygame.KEYDOWN:
            if self.input_mode:
                if event.key == pygame.K_RETURN:
                    self.input_mode = False
                elif event.key == pygame.K_BACKSPACE:
                    player_data.PLAYER_NAME = player_data.PLAYER_NAME[:-1]
                elif len(player_data.PLAYER_NAME) < 12:
                    player_data.PLAYER_NAME += event.unicode
                return "NONE"

            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key == pygame.K_LEFT:
                if self.selected == 1:
                    index = self.speed_values.index(player_data.TEXT_SPEED)
                    if index > 0:
                        player_data.TEXT_SPEED = self.speed_values[index - 1]
                elif self.selected == 2:
                    player_data.BGM_VOLUME = max(0, player_data.BGM_VOLUME - 10)
            elif event.key == pygame.K_RIGHT:
                if self.selected == 1:
                    index = self.speed_values.index(player_data.TEXT_SPEED)
                    if index < len(self.speed_values) - 1:
                        player_data.TEXT_SPEED = self.speed_values[index + 1]
                elif self.selected == 2:
                    player_data.BGM_VOLUME = min(100, player_data.BGM_VOLUME + 10)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:
                    self.input_mode = True
                elif self.selected == 3:
                    return "BACK"

        return "NONE"

    def draw(self, screen):
        label_x = 220
        value_x = 500

        screen.blit(self.background, (0,0))

        title = self.title_font.render("SETTINGS", True, self.white)
        screen.blit(title, (self.width // 2 - title.get_width() // 2 , 45))

        # ==========================
        # Name
        # ==========================
        label_color = self.dark_red if self.selected == 0 else self.white
        label = self.label_font.render("Name", True, label_color)
        screen.blit(label, (label_x, 150))
        name_label_rect = label.get_rect(topleft=(label_x, 150))

        name_text = player_data.PLAYER_NAME
        if self.input_mode:
            name_text += "_"

        name_surface = self.value_font.render(name_text, True, self.white)
        screen.blit(name_surface, (value_x, 150))
        name_rect = name_surface.get_rect(topleft=(value_x, 150))
        self.item_rects = [name_label_rect, name_rect]

        if self.selected == 0:
            hint_text = "Press Enter to finish" if self.input_mode else "Press Enter to edit"
            hint = self.small_font.render(hint_text, True, self.gray)
            screen.blit(hint, (value_x, 190))

        # ==========================
        # Text Speed
        # ==========================
        label_color = self.dark_red if self.selected == 1 else self.white
        label = self.label_font.render("Text Speed", True, label_color)
        screen.blit(label, (label_x, 260))
        self.speed_label_rect = label.get_rect(topleft=(label_x, 260))

        speed_y = 260
        speed_x_positions = [value_x, value_x + 80, value_x + 200]
        
        # 🌟 核心修改 2：修正變數名稱污染，清空重新記錄速度按鈕的範圍
        self.speed_rects = []
        for i in range(3):
            is_current = (player_data.TEXT_SPEED == self.speed_values[i])
            color = self.dark_red if is_current else self.gray
            text = self.value_font.render(self.speed_names[i], True, color)
            screen.blit(text, (speed_x_positions[i], speed_y))
            
            text_rect = text.get_rect(topleft=(speed_x_positions[i], speed_y))
            self.speed_rects.append(text_rect)

        # ==========================
        # BGM Volume
        # ==========================
        label_color = self.dark_red if self.selected == 2 else self.white
        label = self.label_font.render("BGM Volume", True, label_color)
        screen.blit(label, (label_x, 350))
        self.volume_label_rect = label.get_rect(topleft=(label_x, 350))

        pygame.draw.line(screen, self.gray, (self.volume_x1, self.volume_y), (self.volume_x2, self.volume_y), 4)

        knob_x = self.volume_x1 + (self.volume_x2 - self.volume_x1) * player_data.BGM_VOLUME / 100
        pygame.draw.circle(screen, self.dark_red, (int(knob_x), self.volume_y), 10)

        volume_text = self.small_font.render(str(player_data.BGM_VOLUME), True, self.white)
        screen.blit(volume_text, (self.volume_x2 + 30, 356))

        # ==========================
        # Return
        # ==========================
        pygame.draw.line(screen, self.gray, (label_x, 430), (760, 430), 1)

        return_color = self.dark_red if self.selected == 3 else self.white
        return_surface = self.label_font.render("Return", True, return_color)
        return_x = self.width // 2 - return_surface.get_width() // 2
        return_y = 450
        screen.blit(return_surface, (return_x, return_y))
        
        # 🌟 核心修改 3：精準計算 Return 按鈕的碰撞箱
        self.return_rect = return_surface.get_rect(topleft=(return_x, return_y))

        # ==========================
        # 操作提示
        # ==========================
        hint_text = "UP/DN Select    L/R Change    Enter Confirm"
        if self.input_mode:
            hint_text = "Type name    Backspace Delete    Enter Done"
        hint = self.small_font.render(hint_text, True, self.gray)
        screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 38))


if __name__ == "__main__":
    pygame.init()
    WIDTH = 960
    HEIGHT = 540
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Settings Test")
    clock = pygame.time.Clock()
    setting = SettingScene(WIDTH, HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            result = setting.handle_event(event)
            if result == "BACK":
                pygame.quit()
                exit()
        setting.draw(screen)
        pygame.display.update()
        clock.tick(60)