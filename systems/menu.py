import pygame


class MenuScene:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.selected = 0

        self.options = [
            "PLAY",
            "SETTINGS",
            "HELP",
            "EXIT"
        ]

        self.title_font = pygame.font.SysFont(
            "Times New Roman",
            64,
            bold=True
        )

        self.option_font = pygame.font.SysFont(
            "Times New Roman",
            40
        )

        # 底圖
        self.background = pygame.image.load(
            "assets/room/gogo/001.jpg"
        )

        self.background = pygame.transform.scale(
            self.background,
            (width, height)
        )
        self.option_rects = []
        
    def draw(self, screen):

        screen.blit(
            self.background,
            (0, 0)
        )

        # 標題
        title = self.title_font.render(
            "Dead or Alive",
            True,
            (0,0,0)
        )

        screen.blit(
            title,
            (
                self.width//2 - title.get_width()//2,
                30
            )
        )

        # 選項
        self.option_rects = []
        for i, option in enumerate(self.options):

            color = (
                (140,0,32)
                if i == self.selected
                else (255,255,255)
            )

            text = self.option_font.render(
                option,
                True,
                color
            )

            x = self.width//2 - text.get_width()//2
            y = 190 + i*70
            screen.blit(
                text,
                (x, y)
            )

            rect = text.get_rect(topleft=(x, y))

            self.option_rects.append(rect)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:

                self.selected = (
                    self.selected - 1
                ) % len(self.options)

            elif event.key == pygame.K_DOWN:

                self.selected = (
                    self.selected + 1
                ) % len(self.options)

            elif event.key == pygame.K_RETURN:

                return self.options[self.selected]
        elif event.type == pygame.MOUSEMOTION:

            mouse_pos = event.pos

            for i, rect in enumerate(self.option_rects):

                if rect.collidepoint(mouse_pos):

                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_pos = event.pos

                for i, rect in enumerate(self.option_rects):

                    if rect.collidepoint(mouse_pos):

                        self.selected = i

                        return self.options[i]

        return None
    
if __name__ == "__main__":

    pygame.init()

    WIDTH = 960
    HEIGHT = 540

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    clock = pygame.time.Clock()

    menu = MenuScene(
        WIDTH,
        HEIGHT
    )

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

            result = menu.handle_event(
                event
            )

            if result:

                print(result)

        menu.draw(
            screen
        )

        pygame.display.update()

        clock.tick(60)