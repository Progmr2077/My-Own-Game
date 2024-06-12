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
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
GRAVITY = 0.5
MAX_JUMP = 2  # Maximum number of jumps allowed
ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30
ENEMY_INITIAL_SPEED = 3  # Initial speed when spawned
ENEMY_SPEED = 3  # Constant speed after spawning
BULLET_WIDTH = 5
BULLET_HEIGHT = 5
BULLET_SPEED = 10
MAX_ENEMIES = 5  # Maximum number of enemies per level

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bulletstorm Blitz")

# Load background image
background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create a surface for the background
background_image.fill(WHITE)  # Fill it with white color (you can change this)

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
        self.jumps = 0  # Track the number of jumps performed
        self.score = 0  # Initialize the player's score
        self.high_score = 0  # Initialize the player's high score
        self.level = 1  # Initialize the player's level

    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Check for collisions with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.on_ground = True
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.jumps = 0  # Reset the number of jumps when touching the ground

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] and (self.on_ground or self.jumps > 0):
            self.vel_y = -15  # Increase the jump velocity
            self.jumps += 1  # Increment the number of jumps
        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        # Find the nearest enemy
        nearest_enemy = None
        min_distance = float('inf')
        for enemy in enemies_group:
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy

        # If there is an enemy, shoot at it
        if nearest_enemy:
            bullet = Bullet(self.rect.centerx, self.rect.centery, nearest_enemy)
            bullets_group.add(bullet)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)  # Start at a random position on the x-axis
        self.rect.y = random.randint(0, SCREEN_HEIGHT - ENEMY_HEIGHT)  # Start at a random position on the y-axis
        self.player = player
        self.speed = ENEMY_INITIAL_SPEED  # Initial speed

    def update(self):
        # Calculate vector from enemy to player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Move enemy towards the player
        if distance != 0:
            self.rect.x += dx / distance * self.speed
            self.rect.y += dy / distance * self.speed

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.target = target  # Store the enemy target

    def update(self):
        # Move towards the target
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            self.rect.x += dx / distance * BULLET_SPEED
            self.rect.y += dy / distance * BULLET_SPEED

        # Check for collision with target
        if self.rect.colliderect(self.target.rect):
            self.kill()  # Remove bullet
            self.target.kill()  # Remove target
            # Increment the score when an enemy is shot down
            self.target.player.score += 1

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

# Create player object
player = Player()

# Create enemies group
enemies_group = pygame.sprite.Group()

# Create bullets group
bullets_group = pygame.sprite.Group()

# Create platforms
platforms_group = pygame.sprite.Group()
platforms = [
    Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Ground
    Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, 100, 20),  # Middle platform
]
platforms_group.add(platforms)

# Function to start a new level
def new_level():
    # Clear bullets group
    bullets_group.empty()
    # Increment level
    player.level += 1
    # Create new enemies
    for _ in range(MAX_ENEMIES):
        enemy = Enemy(player)
        enemies_group.add(enemy)
    # Reset player's position
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Main game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    player.update(platforms_group)
    enemies_group.update()
    bullets_group.update()

    # Check for collisions between bullets and enemies
    for bullet in bullets_group:
        enemy_hit = pygame.sprite.spritecollideany(bullet, enemies_group)
        if enemy_hit:
            bullet.kill()  # Remove bullet
            enemy_hit.kill()  # Remove enemy
            # Increment the score when an enemy is shot down
            player.score += 1

    # Check for collisions between player and enemies
    if pygame.sprite.spritecollide(player, enemies_group, False):
        # Player touched by enemy, update high score if necessary
        player.high_score = max(player.high_score, player.score)
        player.score = 0  # Reset score when player dies

    # Check if all enemies are taken down
    if len(enemies_group) == 0:
        new_level()

    # Draw
    screen.blit(background_image, (0, 0))
    platforms_group.draw(screen)
    screen.blit(player.image, player.rect)  # Draw player directly onto the screen
    enemies_group.draw(screen)  # Draw enemies onto the screen
    bullets_group.draw(screen)  # Draw bullets onto the screen

    # Display score, level, and high score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {player.score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    level_text = font.render(f"Level: {player.level}", True, BLACK)
    screen.blit(level_text, (10, 50))
    high_score_text = font.render(f"High Score: {player.high_score}", True, BLACK)
    screen.blit(high_score_text, (10, 90))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()