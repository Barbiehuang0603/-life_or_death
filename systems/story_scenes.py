# systems/intro.py

import pygame
import data.player_data as player_data

class StoryScene:

    def __init__(self, width, height, scenes):

        self.width = width
        self.height = height

        self.index = 0
        self.finished = False

        # 打字機效果
        self.displayed_text = ""

        self.char_index = 0

        
        self.char_delay = player_data.TEXT_SPEED

        self.last_char_time = pygame.time.get_ticks()

        self.last_change_time = pygame.time.get_ticks()
        self.name_font = pygame.font.SysFont(
            "Microsoft JhengHei",
            20
        )

        self.text_font = pygame.font.SysFont(
            "Microsoft JhengHei",
            28
        )

        self.hint_font = pygame.font.SysFont(
            "Microsoft JhengHei",
            16
        )

        self.scenes = scenes

        # 預先載入圖片
        self.images = []

        for scene in self.scenes:

            # 讀取原圖
            img = pygame.image.load(
                scene["image"]
            )

            # 原始尺寸
            img_width, img_height = img.get_size()

            # 等比例縮放倍率
            scale = min(
                width / img_width,
                height / img_height
            )

            new_width = int(
                img_width * scale
            )

            new_height = int(
                img_height * scale
            )

            # 高品質縮放
            img = pygame.transform.smoothscale(
                img,
                (new_width, new_height)
            )

            # 建立與螢幕一樣大的畫布
            surface = pygame.Surface(
                (width, height)
            )

            # 黑色背景
            surface.fill(
                (0, 0, 0)
            )

            # 置中
            x = (width - new_width) // 2

            y = (height - new_height) // 2

            surface.blit(
                img,
                (x, y)
            )

            self.images.append(
                surface
            )

    def reset(self):

        self.index = 0
        self.finished = False

        self.displayed_text = ""
        self.char_index = 0

        now = pygame.time.get_ticks()

        self.last_char_time = now
        self.last_change_time = now

    def next_scene(self):

        if self.index < len(self.scenes) - 1:

            self.index += 1

            self.displayed_text = ""
            self.char_index = 0

            now = pygame.time.get_ticks()

            self.last_char_time = now
            self.last_change_time = now

        else:

            self.finished = True

    def update_text(self):

        self.char_delay = player_data.TEXT_SPEED
        current_text = self.scenes[self.index]["text"]

        if self.char_index >= len(current_text):
            return

        now = pygame.time.get_ticks()

        if now - self.last_char_time < self.char_delay:
            return

        self.char_index += 1
        self.displayed_text = current_text[:self.char_index]

        last_char = current_text[self.char_index - 1]

        if (
            self.char_index >= 3
            and current_text[self.char_index - 3:self.char_index] == "..."
        ):
            self.last_char_time = now + 500

        elif last_char in [",", "，"]:
            self.last_char_time = now + 200

        elif last_char in [".", "。"]:
            self.last_char_time = now + 150

        elif last_char in ["?", "？", "!", "！"]:
            self.last_char_time = now + 300

        else:
            self.last_char_time = now

    def update(self):

        current_scene = self.scenes[self.index]

        if current_scene["auto"]:

            now = pygame.time.get_ticks()

            if (
                now - self.last_change_time
                >= current_scene["duration"]
            ):

                self.next_scene()

                self.last_change_time = now

        self.update_text()

    def draw(self, screen):

        # 顯示圖片
        screen.blit(
            self.images[self.index],
            (0, 0)
        )

        # 有文字時才顯示字幕框
        current_text = self.scenes[self.index]["text"]

        if current_text:

            # 對話框
            box_width = 500
            box_height = 100

            box_x = 120
            box_y = self.height - 130

            # 半透明黑底
            dialog_surface = pygame.Surface(
                (box_width, box_height)
            )

            dialog_surface.set_alpha(180)

            dialog_surface.fill(
                (20, 20, 20)
            )

            screen.blit(
                dialog_surface,
                (box_x, box_y)
            )

            # 白色邊框
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (
                    box_x,
                    box_y,
                    box_width,
                    box_height
                ),
                2
            )

            # 名字
            from data.player_data import PLAYER_NAME
            name_surface = self.name_font.render(
                PLAYER_NAME,
                True,
                (255,255,255)
            )

            screen.blit(
                name_surface,
                (
                    box_x + 22,
                    box_y + 15
                )
            )

            # 對話內容
            text_surface = self.text_font.render(
                self.displayed_text,
                True,
                (255,255,255)
            )

            screen.blit(
                text_surface,
                (
                    box_x + 20,
                    box_y + 50
                )
            )

            # 如果文字已經全部顯示完
            if self.char_index >= len(current_text):

                hint_surface = self.hint_font.render(
                    ">> SPACE",
                    True,
                    (180, 180, 180)
                )

                screen.blit(
                    hint_surface,
                    (
                        box_x + box_width - 100,
                        box_y + box_height - 80
                    )
                )

if __name__ == "__main__":

    pygame.init()

    WIDTH = 960
    HEIGHT = 540

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    clock = pygame.time.Clock()

    from data.intro_data import INTRO_SCENES
    from data.outro_data import OUTRO_SCENES

    TEST_MODE = "OUTRO"

    if TEST_MODE == "INTRO":
        scenes = INTRO_SCENES
    else:
        scenes = OUTRO_SCENES

    story = StoryScene(
        WIDTH,
        HEIGHT,
        scenes
    )

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    print("SPACE")

                    current_text = (
                        story.scenes[story.index]["text"]
                    )

                    if story.char_index < len(current_text):

                        story.displayed_text = current_text

                        story.char_index = len(current_text)

                    else:

                        story.next_scene()

        story.update() 

        story.draw(screen)

        pygame.display.update()

        clock.tick(60)