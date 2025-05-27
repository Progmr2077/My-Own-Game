import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 6
GRAVITY = 0.5
MAX_JUMP = 2
ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30
ENEMY_INITIAL_SPEED = 3
ENEMY_SPEED = 3
BULLET_WIDTH = 8
BULLET_HEIGHT = 8
BULLET_SPEED = 12
MAX_ENEMIES = 5
POWERUP_SIZE = 20
POWERUP_DURATION = 5000  # 5 seconds in milliseconds

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bulletstorm Blitz")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.vel_y = 0
        self.on_ground = False
        self.jumps = 0
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shield = False
        self.shield_timer = 0
        self.multiplier = 1
        self.combo_timer = 0

    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Check for collisions with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.on_ground = True
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.jumps = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] and (self.on_ground or self.jumps < MAX_JUMP):
            self.vel_y = -12
            self.jumps += 1

        # Update power-up timers
        current_time = pygame.time.get_ticks()
        if self.rapid_fire and current_time > self.rapid_fire_timer:
            self.rapid_fire = False
        if self.shield and current_time > self.shield_timer:
            self.shield = False
        
        # Update combo multiplier
        if current_time > self.combo_timer:
            self.multiplier = 1

    def shoot(self):
        if self.rapid_fire:
            bullet_count = 3
            spread = 15
        else:
            bullet_count = 1
            spread = 0

        bullets = []
        for i in range(bullet_count):
            angle_offset = (i - (bullet_count-1)/2) * spread
            bullet = Bullet(self.rect.centerx, self.rect.centery, angle_offset)
            bullets.append(bullet)
        
        return bullets

# Enemy class with improved AI
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.spawn_position()
        self.player = player
        self.speed = ENEMY_INITIAL_SPEED
        self.behavior_timer = pygame.time.get_ticks()
        self.behavior = "chase"

    def spawn_position(self):
        side = random.choice(["top", "right", "bottom", "left"])
        if side == "top":
            self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
            self.rect.y = -ENEMY_HEIGHT
        elif side == "right":
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(0, SCREEN_HEIGHT - ENEMY_HEIGHT)
        elif side == "bottom":
            self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
            self.rect.y = SCREEN_HEIGHT
        else:
            self.rect.x = -ENEMY_WIDTH
            self.rect.y = random.randint(0, SCREEN_HEIGHT - ENEMY_HEIGHT)

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Change behavior every 3 seconds
        if current_time - self.behavior_timer > 3000:
            self.behavior = random.choice(["chase", "circle", "zigzag"])
            self.behavior_timer = current_time

        if self.behavior == "chase":
            self.chase_player()
        elif self.behavior == "circle":
            self.circle_player()
        elif self.behavior == "zigzag":
            self.zigzag_movement()

    def chase_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

    def circle_player(self):
        angle = pygame.time.get_ticks() / 500  # Rotation speed
        radius = 100  # Circle radius
        self.rect.x = self.player.rect.centerx + math.cos(angle) * radius - ENEMY_WIDTH/2
        self.rect.y = self.player.rect.centery + math.sin(angle) * radius - ENEMY_HEIGHT/2

    def zigzag_movement(self):
        self.chase_player()
        self.rect.x += math.sin(pygame.time.get_ticks() / 200) * 5

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_offset=0):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Find nearest enemy
        nearest_enemy = None
        min_distance = float('inf')
        for enemy in enemies_group:
            dx = enemy.rect.centerx - x
            dy = enemy.rect.centery - y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy

        if nearest_enemy:
            dx = nearest_enemy.rect.centerx - x
            dy = nearest_enemy.rect.centery - y
            angle = math.atan2(dy, dx)
            angle += math.radians(angle_offset)  # Add spread angle
            self.velocity_x = math.cos(angle) * BULLET_SPEED
            self.velocity_y = math.sin(angle) * BULLET_SPEED
        else:
            self.velocity_x = 0
            self.velocity_y = -BULLET_SPEED

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Remove if off screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

# PowerUp class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["rapid_fire", "shield", "multiplier"])
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        if self.type == "rapid_fire":
            self.image.fill(GOLD)
        elif self.type == "shield":
            self.image.fill(BLUE)
        else:
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - POWERUP_SIZE)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - POWERUP_SIZE)

# Create sprite groups
player = Player()
enemies_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
platforms_group = pygame.sprite.Group()
powerups_group = pygame.sprite.Group()

# Create platforms
platforms = [
    Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Ground
    Platform(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, 200, 20),  # Left platform
    Platform(SCREEN_WIDTH * 3 // 4 - 200, SCREEN_HEIGHT // 2, 200, 20),  # Right platform
    Platform(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT * 3 // 4, 200, 20),  # Bottom middle platform
]
platforms_group.add(platforms)

def spawn_powerup():
    if random.random() < 0.02 and len(powerups_group) < 3:  # 2% chance per frame, max 3 powerups
        powerups_group.add(PowerUp())

def new_level():
    bullets_group.empty()
    powerups_group.empty()
    player.level += 1
    for _ in range(min(MAX_ENEMIES + player.level - 1, 10)):  # Increase enemies with level, max 10
        enemy = Enemy(player)
        enemy.speed = min(ENEMY_SPEED + (player.level - 1) * 0.5, 7)  # Increase speed with level, max 7
        enemies_group.add(enemy)
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Main game loop
clock = pygame.time.Clock()
last_shot_time = 0
shot_delay = 250  # Milliseconds between shots
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if current_time - last_shot_time > (shot_delay / 2 if player.rapid_fire else shot_delay):
                    bullets = player.shoot()
                    bullets_group.add(bullets)
                    last_shot_time = current_time

    # Update
    player.update(platforms_group)
    enemies_group.update()
    bullets_group.update()

    # Spawn power-ups
    spawn_powerup()

    # Check for collisions between bullets and enemies
    for bullet in bullets_group:
        enemy_hit = pygame.sprite.spritecollideany(bullet, enemies_group)
        if enemy_hit:
            bullet.kill()
            enemy_hit.kill()
            player.score += 100 * player.multiplier
            player.combo_timer = current_time + 2000  # 2 second combo window
            player.multiplier = min(player.multiplier + 0.5, 4)  # Max 4x multiplier

    # Check for collisions between player and power-ups
    powerup_hit = pygame.sprite.spritecollideany(player, powerups_group)
    if powerup_hit:
        if powerup_hit.type == "rapid_fire":
            player.rapid_fire = True
            player.rapid_fire_timer = current_time + POWERUP_DURATION
        elif powerup_hit.type == "shield":
            player.shield = True
            player.shield_timer = current_time + POWERUP_DURATION
        else:  # multiplier
            player.multiplier *= 2
        powerup_hit.kill()

    # Check for collisions between player and enemies
    if not player.shield and pygame.sprite.spritecollideany(player, enemies_group):
        player.high_score = max(player.high_score, player.score)
        player.score = 0
        player.level = 1
        player.multiplier = 1
        enemies_group.empty()
        new_level()

    # Check if all enemies are defeated
    if len(enemies_group) == 0:
        new_level()

    # Draw
    screen.fill(WHITE)
    
    # Draw platforms
    platforms_group.draw(screen)
    
    # Draw power-ups
    powerups_group.draw(screen)
    
    # Draw player with shield effect
    if player.shield:
        pygame.draw.circle(screen, BLUE, player.rect.center, max(PLAYER_WIDTH, PLAYER_HEIGHT) // 2 + 5, 2)
    screen.blit(player.image, player.rect)
    
    # Draw enemies and bullets
    enemies_group.draw(screen)
    bullets_group.draw(screen)

    # Display score, level, and high score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {player.score}", True, BLACK)
    level_text = font.render(f"Level: {player.level}", True, BLACK)
    high_score_text = font.render(f"High Score: {player.high_score}", True, BLACK)
    multiplier_text = font.render(f"Multiplier: {player.multiplier:.1f}x", True, BLACK)
    
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(high_score_text, (10, 90))
    screen.blit(multiplier_text, (10, 130))

    # Display active power-ups
    if player.rapid_fire:
        rapid_fire_text = font.render("Rapid Fire!", True, GOLD)
        screen.blit(rapid_fire_text, (SCREEN_WIDTH - 150, 10))
    if player.shield:
        shield_text = font.render("Shield!", True, BLUE)
        screen.blit(shield_text, (SCREEN_WIDTH - 150, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()