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

        self.speed_values = [20, 40, 70]
        self.speed_names = ["Fast", "Normal", "Slow"]

        self.title_font = pygame.font.SysFont(
            "Times New Roman",
            60,
            bold=True
        )

        self.label_font = pygame.font.SysFont(
            "Times New Roman",
            32
        )

        self.value_font = pygame.font.SysFont(
            "Times New Roman",
            30
        )

        self.small_font = pygame.font.SysFont(
            "Times New Roman",
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


    def handle_event(self, event):

        if event.type != pygame.KEYDOWN:
            return "NONE"

        # ==========================
        # 輸入名字模式
        # ==========================

        if self.input_mode:

            if event.key == pygame.K_RETURN:
                self.input_mode = False

            elif event.key == pygame.K_BACKSPACE:
                player_data.PLAYER_NAME = (
                    player_data.PLAYER_NAME[:-1]
                )

            elif len(player_data.PLAYER_NAME) < 12:
                player_data.PLAYER_NAME += event.unicode

            return "NONE"

        # ==========================
        # 一般設定模式
        # ==========================

        if event.key == pygame.K_UP:

            self.selected = (
                self.selected - 1
            ) % len(self.items)

        elif event.key == pygame.K_DOWN:

            self.selected = (
                self.selected + 1
            ) % len(self.items)

        elif event.key == pygame.K_LEFT:

            if self.selected == 1:

                index = self.speed_values.index(
                    player_data.TEXT_SPEED
                )

                if index > 0:
                    player_data.TEXT_SPEED = (
                        self.speed_values[index - 1]
                    )

            elif self.selected == 2:

                player_data.BGM_VOLUME = max(
                    0,
                    player_data.BGM_VOLUME - 10
                )

        elif event.key == pygame.K_RIGHT:

            if self.selected == 1:

                index = self.speed_values.index(
                    player_data.TEXT_SPEED
                )

                if index < len(self.speed_values) - 1:
                    player_data.TEXT_SPEED = (
                        self.speed_values[index + 1]
                    )

            elif self.selected == 2:

                player_data.BGM_VOLUME = min(
                    100,
                    player_data.BGM_VOLUME + 10
                )

        elif event.key == pygame.K_RETURN:

            if self.selected == 0:
                self.input_mode = True

            elif self.selected == 3:
                return "BACK"

        return "NONE"


    def draw_label(self, screen, text, y, selected):

        color = (
            self.dark_red
            if selected
            else self.white
        )

        label = self.label_font.render(
            text,
            True,
            color
        )

        screen.blit(
            label,
            (
                self.width // 2 - label.get_width() // 2,
                y
            )
        )


    def draw(self, screen):

        label_x = 220
        value_x = 500

        screen.blit(
            self.background,
            (0,0)
        )

        title = self.title_font.render(
            "SETTINGS",
            True,
            self.white
        )

        screen.blit(
            title,
            (
                self.width // 2 - title.get_width() // 2 ,
                45
            )
        )

        # ==========================
        # Name
        # ==========================

        label_color = (
            self.dark_red
            if self.selected == 0
            else self.white
        )

        label = self.label_font.render(
            "Name",
            True,
            label_color
        )

        screen.blit(
            label,
            (
                label_x,
                150
            )
        )

        name_text = player_data.PLAYER_NAME

        if self.input_mode:
            name_text += "_"

        name_surface = self.value_font.render(
            name_text,
            True,
            self.white
        )

        screen.blit(
            name_surface,
            (
                value_x,
                150
            )
        )

        if self.selected == 0:

            if self.input_mode:

                hint_text = "Press Enter to finish"

            else:

                hint_text = "Press Enter to edit"

            hint = self.small_font.render(
                hint_text,
                True,
                self.gray
            )

            screen.blit(
                hint,
                (
                    value_x,
                    190
                )
            )

        # ==========================
        # Text Speed
        # ==========================

        label_color = (
            self.dark_red
            if self.selected == 1
            else self.white
        )

        label = self.label_font.render(
            "Text Speed",
            True,
            label_color
        )

        screen.blit(
            label,
            (
                label_x,
                260
            )
        )

        speed_y = 260
        speed_x_positions = [
            value_x,
            value_x + 80,
            value_x + 200
        ]

        for i in range(3):

            is_current = (
                player_data.TEXT_SPEED
                == self.speed_values[i]
            )

            color = (
                self.dark_red
                if is_current
                else self.gray
            )

            text = self.value_font.render(
                self.speed_names[i],
                True,
                color
            )

            screen.blit(
                text,
                (
                    speed_x_positions[i],
                    speed_y
                )
            )


        # ==========================
        # BGM Volume
        # ==========================

        label_color = (
            self.dark_red
            if self.selected == 2
            else self.white
        )

        label = self.label_font.render(
            "BGM Volume",
            True,
            label_color
        )

        screen.blit(
            label,
            (
                label_x,
                350
            )
        )

        line_x1 = value_x
        line_x2 = value_x + 200
        line_y = 370

        pygame.draw.line(
            screen,
            self.gray,
            (line_x1, line_y),
            (line_x2, line_y),
            4
        )

        knob_x = (
            line_x1
            + (line_x2 - line_x1)
            * player_data.BGM_VOLUME
            / 100
        )

        pygame.draw.circle(
            screen,
            self.dark_red,
            (
                int(knob_x),
                line_y
            ),
            10
        )

        volume_text = self.small_font.render(
            str(player_data.BGM_VOLUME),
            True,
            self.white
        )

        screen.blit(
            volume_text,
            (
                line_x2 + 30, 356
            )
        )

        # ==========================
        # Return
        # ==========================

        pygame.draw.line(
            screen,
            self.gray,
            (label_x, 430),
            (760, 430),
            1
        )

        return_color = (
            self.dark_red
            if self.selected == 3
            else self.white
        )

        return_surface = self.label_font.render(
            "Return",
            True,
            return_color
        )

        screen.blit(
            return_surface,
            (
                self.width // 2 - return_surface.get_width() // 2,
                450
            )
        )

        # ==========================
        # 操作提示
        # ==========================

        hint_text = "↑↓ Select    ←→ Change    Enter Confirm"

        if self.input_mode:
            hint_text = "Type name    Backspace Delete    Enter Done"

        hint = self.small_font.render(
            hint_text,
            True,
            self.gray
        )

        screen.blit(
            hint,
            (
                self.width // 2 - hint.get_width() // 2,
                self.height - 35
            )
        )


if __name__ == "__main__":

    pygame.init()

    WIDTH = 960
    HEIGHT = 540

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "Settings Test"
    )

    clock = pygame.time.Clock()

    setting = SettingScene(
        WIDTH,
        HEIGHT
    )

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

            result = setting.handle_event(
                event
            )

            if result == "BACK":

                pygame.quit()
                exit()

        setting.draw(
            screen
        )

        pygame.display.update()

        clock.tick(60)