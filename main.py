import pygame
import random
import sys
import os
import asyncio

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("Food Ninja")

def load_and_scale_image(filename, size=(80, 80)):
    path = os.path.join("images", filename)
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(image, size)

def make_circle_surface(image_surf):
    size = image_surf.get_size()
    mask_surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(mask_surf, (255, 255, 255, 255), mask_surf.get_rect())
    circular_surf = pygame.Surface(size, pygame.SRCALPHA)
    circular_surf.blit(image_surf, (0, 0))
    circular_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return circular_surf

# Load images (ensure these files exist in an 'images' folder)
burger_img = make_circle_surface(load_and_scale_image("g1.jpg"))
pizza_img = make_circle_surface(load_and_scale_image("g2.jpg"))
veg_img = make_circle_surface(load_and_scale_image("g3.jpg"))
carrot_img = make_circle_surface(load_and_scale_image("g4.jpg"))

bg_image_raw = pygame.image.load(os.path.join("images", "background.jpg")).convert()
bg_scale_factor = HEIGHT / bg_image_raw.get_height()
bg_width = int(bg_image_raw.get_width() * bg_scale_factor)
bg_height = HEIGHT
bg_image = pygame.transform.smoothscale(bg_image_raw, (bg_width, bg_height))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)

class Food:
    BASE_SPEED = 2
    SPEED_INCREMENT = 0.1
    MAX_SPEED = 10

    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.sliced = False

        if kind == 'burger':
            self.image = burger_img
        elif kind == 'pizza':
            self.image = pizza_img
        elif kind == 'carrot':
            self.image = carrot_img
        else:
            self.image = veg_img

        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self, current_score):
        speed = min(self.BASE_SPEED + self.SPEED_INCREMENT * current_score, self.MAX_SPEED)
        self.y += speed
        self.rect.centery = self.y

    def draw(self, surface):
        min_scale = 0.5
        max_scale = 1.2
        scale = min_scale + (max_scale - min_scale) * (self.y / HEIGHT)
        scaled_width = max(1, int(self.image.get_width() * scale))
        scaled_height = max(1, int(self.image.get_height() * scale))
        scaled_image = pygame.transform.smoothscale(self.image, (scaled_width, scaled_height))

        min_alpha = 100
        max_alpha = 255
        alpha = min_alpha + int((max_alpha - min_alpha) * (self.y / HEIGHT))
        scaled_image.set_alpha(alpha)

        rect = scaled_image.get_rect(center=(self.x, self.y))
        surface.blit(scaled_image, rect)

class Button:
    def __init__(self, text, pos, size, elevation=6):
        self.text = text
        self.pos = pos
        self.size = size
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.pressed = False

        self.top_rect = pygame.Rect(pos, size)
        self.bottom_rect = pygame.Rect(pos, (size[0], size[1] + elevation))
        self.top_color = (70, 95, 119)
        self.bottom_color = (53, 75, 94)
        self.hover_color = (100, 130, 160)
        self.pressed_color = (40, 60, 80)

        self.text_surf = small_font.render(self.text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        if self.top_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.top_color = self.pressed_color
                self.dynamic_elevation = 0
                self.pressed = True
            else:
                self.top_color = self.hover_color
                if self.pressed:
                    clicked = True
                    self.pressed = False
                self.dynamic_elevation = self.elevation
        else:
            self.top_color = (70, 95, 119)
            self.dynamic_elevation = self.elevation
            self.pressed = False

        self.bottom_rect.topleft = (self.pos[0], self.pos[1] + self.dynamic_elevation)
        pygame.draw.rect(surface, self.bottom_color, self.bottom_rect, border_radius=12)

        self.top_rect.topleft = (self.pos[0], self.pos[1] + self.dynamic_elevation - self.elevation)
        pygame.draw.rect(surface, self.top_color, self.top_rect, border_radius=12)

        self.text_rect.center = self.top_rect.center
        surface.blit(self.text_surf, self.text_rect)

        return clicked

def generate_food():
    kind = random.choices(['burger', 'pizza', 'veg', 'carrot'], weights=[0.4, 0.4, 0.1, 0.1])[0]
    x = random.randint(50, WIDTH - 50)
    y = -50
    return Food(x, y, kind)

def draw_lifelines(surface, count):
    for i in range(count):
        pygame.draw.rect(surface, RED, (20 + i*40, 20, 30, 30))

def draw_score(surface, score):
    text = font.render(f"Score: {score}", True, BLACK)
    surface.blit(text, (WIDTH - 150, 20))

async def main():
    lifelines = 3
    score = 0
    clock = pygame.time.Clock()
    foods = []
    spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_event, 1000)

    slicing = False
    slice_positions = []

    bg_x1 = 0
    bg_x2 = bg_width
    bg_scroll_speed = 1

    game_over = False

    restart_button = Button("Restart", (WIDTH // 2 - 110, HEIGHT // 2), (100, 50))
    quit_button = Button("Quit", (WIDTH // 2 + 10, HEIGHT // 2), (100, 50))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Touch events for mobile
            elif event.type == pygame.FINGERDOWN and not game_over:
                x = event.x * WIDTH
                y = event.y * HEIGHT
                slicing = True
                slice_positions = [(x, y)]

            elif event.type == pygame.FINGERUP:
                slicing = False
                slice_positions = []

            elif event.type == pygame.FINGERMOTION and slicing and not game_over:
                x = event.x * WIDTH
                y = event.y * HEIGHT
                slice_positions.append((x, y))

            # Mouse events for desktop
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                slicing = True
                slice_positions = [event.pos]

            elif event.type == pygame.MOUSEBUTTONUP:
                slicing = False
                slice_positions = []

            elif event.type == pygame.MOUSEMOTION and slicing and not game_over:
                slice_positions.append(event.pos)

            elif event.type == spawn_event and not game_over:
                foods.append(generate_food())

        if not game_over:
            bg_x1 -= bg_scroll_speed
            bg_x2 -= bg_scroll_speed

            if bg_x1 <= -bg_width:
                bg_x1 = bg_x2 + bg_width
            if bg_x2 <= -bg_width:
                bg_x2 = bg_x1 + bg_width

            screen.blit(bg_image, (bg_x1, 0))
            screen.blit(bg_image, (bg_x2, 0))

            for food in foods[:]:
                food.move(score)
                food.draw(screen)
                if food.y > HEIGHT + 50:
                    foods.remove(food)

            if slicing and len(slice_positions) > 1:
                for food in foods[:]:
                    if any(food.rect.collidepoint(pos) for pos in slice_positions) and not food.sliced:
                        food.sliced = True
                        foods.remove(food)
                        if food.kind in ['veg', 'carrot']:
                            lifelines -= 1
                        else:
                            score += 1

            if len(slice_positions) > 1:
                pygame.draw.lines(screen, RED, False, slice_positions, 3)

            draw_lifelines(screen, lifelines)
            draw_score(screen, score)

            if lifelines <= 0:
                game_over = True

        else:
            screen.blit(bg_image, (bg_x1, 0))
            screen.blit(bg_image, (bg_x2, 0))

            game_over_text = font.render("Game Over!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))

            if restart_button.draw(screen):
                lifelines = 3
                score = 0
                foods.clear()
                slicing = False
                slice_positions.clear()
                bg_x1 = 0
                bg_x2 = bg_width
                game_over = False

            if quit_button.draw(screen):
                running = False

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # Required for pygbag

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
