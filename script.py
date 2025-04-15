
"""
GALACTIC DEFENDER - JUEGO ARCADE 2D

Módulo principal que implementa un shooter espacial con:
- Sistema de oleadas progresivas
- Gestión de colisiones eficiente
- Menús interactivos
- Sonido espacial
- Escalado adaptable de resolución

Autor: [Tu nombre]
Versión: 1.2.0
Última actualización: [Fecha]
"""
import pygame
import random
import sys

# =============================================================================
# CONFIGURACIÓN INICIAL Y CONSTANTES
# =============================================================================

# Inicialización de subsistemas principales
pygame.init()
pygame.mixer.init()

# Configuración de pantalla adaptable
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w )  # 90% del ancho de la pantalla
SCREEN_HEIGHT = int(info.current_h *0.95)  # 80% del alto de la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galactic Defender")

# Definición de colores RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Configuración de rendimiento
clock = pygame.time.Clock()
FPS = 60

# Cargar sonidos
try:
    shoot_sound = pygame.mixer.Sound("sound/space-battle-sounds-cm-37833 (mp3cut.net).mp3")
    explosion_sound = pygame.mixer.Sound("sound/explosion-312361.mp3")
    shoot_sound.set_volume(0.2)
except:
    shoot_sound = None
    explosion_sound = None

# Cargar imágenes
try:
    player_img = pygame.image.load("images/player.png").convert_alpha()
    enemy_images = [
        pygame.image.load("images/enemy1.png").convert_alpha(),
        pygame.image.load("images/enemy2.png").convert_alpha(),
        pygame.image.load("images/enemy3.png").convert_alpha()
    ]
except:
    # Si no hay imágenes, crear formas básicas
    player_img = pygame.Surface((40, 30))
    player_img.fill(GREEN)
    enemy_images = [
        pygame.Surface((30, 30)).convert_alpha(),
        pygame.Surface((40, 20)).convert_alpha(),
        pygame.Surface((25, 35)).convert_alpha()
    ]
    enemy_images[0].fill(RED)
    enemy_images[1].fill(ORANGE)
    enemy_images[2].fill(BLUE)


# Función para dibujar texto con fondo
def draw_text(text, size, x, y, text_color=WHITE, bg_color=None, border_radius=0):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x, y))

    if bg_color:
        button_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(screen, bg_color, button_rect, border_radius=border_radius)

    screen.blit(text_surface, text_rect)
    return text_rect.inflate(40, 20) if bg_color else text_rect


# Clase del jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = 8
        self.lives = 3
        self.bullets = pygame.sprite.Group()
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if shoot_sound:
                shoot_sound.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.bullets.add(bullet)
            self.last_shot = now


# Clase de balas
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


# Clase de enemigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.image = enemy_images[type]
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), -50))
        self.speed = random.randint(1, 3) + type
        self.health = type + 1

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# Clase principal del juego
class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.spawn_wave()

    def spawn_wave(self):
        for _ in range(5 + self.wave * 2):
            enemy_type = random.randint(0, 2)
            enemy = Enemy(enemy_type)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def check_collisions(self):
        hits = pygame.sprite.groupcollide(self.enemies, self.player.bullets, False, True)
        for enemy, bullets in hits.items():
            enemy.health -= len(bullets)
            if enemy.health <= 0:
                if explosion_sound:
                    explosion_sound.play()
                enemy.kill()
                self.score += 10 * (enemy.type + 1)

        if pygame.sprite.spritecollide(self.player, self.enemies, True):
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over = True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pause_game()

            if self.game_over:
                show_game_over(self.score)
                return

            self.all_sprites.update()
            self.player.bullets.update()
            self.check_collisions()

            if not self.enemies:
                self.wave += 1
                self.spawn_wave()

            screen.fill(BLACK)
            self.all_sprites.draw(screen)
            self.player.bullets.draw(screen)

            # Interfaz de usuario
            draw_text(f"Score: {self.score}", 24, 100, 20, YELLOW)
            draw_text(f"Lives: {self.player.lives}", 24, SCREEN_WIDTH - 100, 20, GREEN)
            draw_text(f"Wave: {self.wave}", 24, SCREEN_WIDTH // 2, 20, ORANGE)

            pygame.display.flip()
            clock.tick(FPS)

    def pause_game(self):
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    paused = False

            screen.fill(BLACK)
            draw_text("PAUSED", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
            draw_text("Press ESC to continue", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, WHITE)
            pygame.display.update()
            clock.tick(5)


# Menús
def show_main_menu():
    menu = True
    while menu:
        screen.fill(BLACK)
        draw_text("GALACTIC DEFENDER", 60, SCREEN_WIDTH // 2, 150, YELLOW)

        play_btn = draw_text("Play", 40, SCREEN_WIDTH // 2, 300, BLACK, GREEN, 15)
        quit_btn = draw_text("Quit", 40, SCREEN_WIDTH // 2, 400, BLACK, RED, 15)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    menu = False
                if quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def show_game_over(score):
    while True:
        screen.fill(BLACK)
        draw_text("GAME OVER", 60, SCREEN_WIDTH // 2, 150, RED)
        draw_text(f"Final Score: {score}", 40, SCREEN_WIDTH // 2, 250, WHITE)

        retry_btn = draw_text("Retry", 40, SCREEN_WIDTH // 2, 350, BLACK, GREEN, 15)
        menu_btn = draw_text("Main Menu", 40, SCREEN_WIDTH // 2, 450, BLACK, BLUE, 15)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    main()
                if menu_btn.collidepoint(event.pos):
                    show_main_menu()
                    return

        pygame.display.update()


def main():
    while True:
        show_main_menu()
        game = Game()
        game.run()


if __name__ == "__main__":
    main()