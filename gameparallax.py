import pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Background Example")

background = pygame.image.load("images/background.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

scroll_x = 0
scroll_speed = 2

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    scroll_x -= scroll_speed
    if scroll_x <= -WIDTH:
        scroll_x = 0

    # Draw two backgrounds side by side for seamless scrolling
    screen.blit(background, (scroll_x, 0))
    screen.blit(background, (scroll_x + WIDTH, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
