// Constants
const SCREEN_WIDTH = 800;
const SCREEN_HEIGHT = 600;
const PLAYER_WIDTH = 50;
const PLAYER_HEIGHT = 50;
const PLAYER_SPEED = 6;
const GRAVITY = 0.5;
const MAX_JUMP = 2;
const ENEMY_WIDTH = 30;
const ENEMY_HEIGHT = 30;
const ENEMY_SPEED = 3;
const BULLET_WIDTH = 8;
const BULLET_HEIGHT = 8;
const BULLET_SPEED = 12;
const MAX_ENEMIES = 5;
const POWERUP_SIZE = 20;
const POWERUP_DURATION = 5000;

// Colors
const COLORS = {
    WHITE: '#FFFFFF',
    BLACK: '#000000',
    RED: '#FF0000',
    BLUE: '#0000FF',
    GREEN: '#00FF00',
    GOLD: '#FFD700',
    PURPLE: '#800080'
};

// Game state
let player;
let enemies = [];
let bullets = [];
let platforms = [];
let powerups = [];
let lastTime = 0;
let lastShotTime = 0;

// Canvas setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

class Player {
    constructor() {
        this.width = PLAYER_WIDTH;
        this.height = PLAYER_HEIGHT;
        this.x = SCREEN_WIDTH / 2 - this.width / 2;
        this.y = SCREEN_HEIGHT / 2 - this.height / 2;
        this.velY = 0;
        this.onGround = false;
        this.jumps = 0;
        this.score = 0;
        this.highScore = 0;
        this.level = 1;
        this.rapidFire = false;
        this.rapidFireTimer = 0;
        this.shield = false;
        this.shieldTimer = 0;
        this.multiplier = 1;
        this.comboTimer = 0;
    }

    update() {
        // Apply gravity
        this.velY += GRAVITY;
        this.y += this.velY;

        // Platform collision
        this.onGround = false;
        for (const platform of platforms) {
            if (this.collidesWith(platform)) {
                if (this.velY > 0) {
                    this.onGround = true;
                    this.y = platform.y - this.height;
                    this.velY = 0;
                    this.jumps = 0;
                } else if (this.velY < 0) {
                    this.y = platform.y + platform.height;
                    this.velY = 0;
                }
            }
        }

        // Movement
        if (keys.ArrowLeft && this.x > 0) {
            this.x -= PLAYER_SPEED;
        }
        if (keys.ArrowRight && this.x < SCREEN_WIDTH - this.width) {
            this.x += PLAYER_SPEED;
        }
        if (keys.ArrowUp && (this.onGround || this.jumps < MAX_JUMP)) {
            this.velY = -12;
            this.jumps++;
        }

        // Update power-up timers
        const currentTime = Date.now();
        if (this.rapidFire && currentTime > this.rapidFireTimer) {
            this.rapidFire = false;
        }
        if (this.shield && currentTime > this.shieldTimer) {
            this.shield = false;
        }
        if (currentTime > this.comboTimer) {
            this.multiplier = 1;
        }
    }

    shoot() {
        const currentTime = Date.now();
        if (currentTime - lastShotTime < (this.rapidFire ? 125 : 250)) return;

        const bulletCount = this.rapidFire ? 3 : 1;
        const spread = this.rapidFire ? 15 : 0;

        for (let i = 0; i < bulletCount; i++) {
            const angleOffset = (i - (bulletCount - 1) / 2) * spread;
            bullets.push(new Bullet(
                this.x + this.width / 2,
                this.y + this.height / 2,
                angleOffset
            ));
        }

        lastShotTime = currentTime;
    }

    collidesWith(obj) {
        return this.x < obj.x + obj.width &&
               this.x + this.width > obj.x &&
               this.y < obj.y + obj.height &&
               this.y + this.height > obj.y;
    }

    draw() {
        ctx.fillStyle = COLORS.RED;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        if (this.shield) {
            ctx.strokeStyle = COLORS.BLUE;
            ctx.beginPath();
            ctx.arc(
                this.x + this.width / 2,
                this.y + this.height / 2,
                Math.max(this.width, this.height) / 2 + 5,
                0,
                Math.PI * 2
            );
            ctx.stroke();
        }
    }
}

class Enemy {
    constructor() {
        this.width = ENEMY_WIDTH;
        this.height = ENEMY_HEIGHT;
        this.speed = ENEMY_SPEED;
        this.spawnPosition();
        this.behaviorTimer = Date.now();
        this.behavior = "chase";
    }

    spawnPosition() {
        const side = Math.floor(Math.random() * 4);
        switch(side) {
            case 0: // top
                this.x = Math.random() * (SCREEN_WIDTH - this.width);
                this.y = -this.height;
                break;
            case 1: // right
                this.x = SCREEN_WIDTH;
                this.y = Math.random() * (SCREEN_HEIGHT - this.height);
                break;
            case 2: // bottom
                this.x = Math.random() * (SCREEN_WIDTH - this.width);
                this.y = SCREEN_HEIGHT;
                break;
            case 3: // left
                this.x = -this.width;
                this.y = Math.random() * (SCREEN_HEIGHT - this.height);
                break;
        }
    }

    update() {
        const currentTime = Date.now();
        
        if (currentTime - this.behaviorTimer > 3000) {
            this.behavior = ["chase", "circle", "zigzag"][Math.floor(Math.random() * 3)];
            this.behaviorTimer = currentTime;
        }

        switch(this.behavior) {
            case "chase":
                this.chasePlayer();
                break;
            case "circle":
                this.circlePlayer();
                break;
            case "zigzag":
                this.zigzagMovement();
                break;
        }
    }

    chasePlayer() {
        const dx = player.x - this.x;
        const dy = player.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist !== 0) {
            this.x += (dx / dist) * this.speed;
            this.y += (dy / dist) * this.speed;
        }
    }

    circlePlayer() {
        const angle = Date.now() / 500;
        const radius = 100;
        this.x = player.x + Math.cos(angle) * radius - this.width / 2;
        this.y = player.y + Math.sin(angle) * radius - this.height / 2;
    }

    zigzagMovement() {
        this.chasePlayer();
        this.x += Math.sin(Date.now() / 200) * 5;
    }

    draw() {
        ctx.fillStyle = COLORS.BLACK;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

class Bullet {
    constructor(x, y, angleOffset = 0) {
        this.width = BULLET_WIDTH;
        this.height = BULLET_HEIGHT;
        this.x = x;
        this.y = y;

        let nearestEnemy = null;
        let minDistance = Infinity;
        
        for (const enemy of enemies) {
            const dx = enemy.x - x;
            const dy = enemy.y - y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < minDistance) {
                minDistance = distance;
                nearestEnemy = enemy;
            }
        }

        if (nearestEnemy) {
            const dx = nearestEnemy.x - x;
            const dy = nearestEnemy.y - y;
            const angle = Math.atan2(dy, dx) + (angleOffset * Math.PI / 180);
            this.velocityX = Math.cos(angle) * BULLET_SPEED;
            this.velocityY = Math.sin(angle) * BULLET_SPEED;
        } else {
            this.velocityX = 0;
            this.velocityY = -BULLET_SPEED;
        }
    }

    update() {
        this.x += this.velocityX;
        this.y += this.velocityY;
    }

    isOffScreen() {
        return this.x < 0 || this.x > SCREEN_WIDTH ||
               this.y < 0 || this.y > SCREEN_HEIGHT;
    }

    draw() {
        ctx.fillStyle = COLORS.BLUE;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

class PowerUp {
    constructor() {
        this.size = POWERUP_SIZE;
        this.type = ["rapid_fire", "shield", "multiplier"][Math.floor(Math.random() * 3)];
        this.x = Math.random() * (SCREEN_WIDTH - this.size);
        this.y = Math.random() * (SCREEN_HEIGHT - this.size);
    }

    draw() {
        ctx.fillStyle = this.type === "rapid_fire" ? COLORS.GOLD :
                       this.type === "shield" ? COLORS.BLUE :
                       COLORS.GREEN;
        ctx.fillRect(this.x, this.y, this.size, this.size);
    }
}

// Input handling
const keys = {};
document.addEventListener('keydown', (e) => {
    keys[e.code] = true;
    if (e.code === 'Space') {
        player.shoot();
    }
});
document.addEventListener('keyup', (e) => {
    keys[e.code] = false;
});

function spawnPowerup() {
    if (Math.random() < 0.02 && powerups.length < 3) {
        powerups.push(new PowerUp());
    }
}

function newLevel() {
    bullets = [];
    powerups = [];
    player.level++;
    enemies = [];
    const enemyCount = Math.min(MAX_ENEMIES + player.level - 1, 10);
    for (let i = 0; i < enemyCount; i++) {
        const enemy = new Enemy();
        enemy.speed = Math.min(ENEMY_SPEED + (player.level - 1) * 0.5, 7);
        enemies.push(enemy);
    }
    player.x = SCREEN_WIDTH / 2 - player.width / 2;
    player.y = SCREEN_HEIGHT / 2 - player.height / 2;
}

function init() {
    player = new Player();
    
    // Create platforms
    platforms = [
        { x: 0, y: SCREEN_HEIGHT - 50, width: SCREEN_WIDTH, height: 50 },
        { x: SCREEN_WIDTH / 4, y: SCREEN_HEIGHT / 2, width: 200, height: 20 },
        { x: SCREEN_WIDTH * 3/4 - 200, y: SCREEN_HEIGHT / 2, width: 200, height: 20 },
        { x: SCREEN_WIDTH / 2 - 100, y: SCREEN_HEIGHT * 3/4, width: 200, height: 20 }
    ];
    
    newLevel();
}

function update() {
    player.update();
    
    // Update enemies
    enemies.forEach(enemy => enemy.update());
    
    // Update bullets
    bullets = bullets.filter(bullet => {
        bullet.update();
        return !bullet.isOffScreen();
    });
    
    // Spawn power-ups
    spawnPowerup();
    
    // Check bullet-enemy collisions
    bullets = bullets.filter(bullet => {
        let hit = false;
        enemies = enemies.filter(enemy => {
            if (!hit && bullet.x < enemy.x + enemy.width &&
                bullet.x + bullet.width > enemy.x &&
                bullet.y < enemy.y + enemy.height &&
                bullet.y + bullet.height > enemy.y) {
                hit = true;
                player.score += 100 * player.multiplier;
                player.comboTimer = Date.now() + 2000;
                player.multiplier = Math.min(player.multiplier + 0.5, 4);
                return false;
            }
            return true;
        });
        return !hit;
    });
    
    // Check player-powerup collisions
    powerups = powerups.filter(powerup => {
        if (player.x < powerup.x + powerup.size &&
            player.x + player.width > powerup.x &&
            player.y < powerup.y + powerup.size &&
            player.y + player.height > powerup.y) {
            const currentTime = Date.now();
            switch(powerup.type) {
                case "rapid_fire":
                    player.rapidFire = true;
                    player.rapidFireTimer = currentTime + POWERUP_DURATION;
                    break;
                case "shield":
                    player.shield = true;
                    player.shieldTimer = currentTime + POWERUP_DURATION;
                    break;
                case "multiplier":
                    player.multiplier *= 2;
                    break;
            }
            return false;
        }
        return true;
    });
    
    // Check player-enemy collisions
    if (!player.shield && enemies.some(enemy => player.collidesWith(enemy))) {
        player.highScore = Math.max(player.highScore, player.score);
        player.score = 0;
        player.level = 1;
        player.multiplier = 1;
        enemies = [];
        newLevel();
    }
    
    // Check if level completed
    if (enemies.length === 0) {
        newLevel();
    }
}

function draw() {
    // Clear canvas
    ctx.fillStyle = COLORS.WHITE;
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
    
    // Draw platforms
    ctx.fillStyle = COLORS.BLACK;
    platforms.forEach(platform => {
        ctx.fillRect(platform.x, platform.y, platform.width, platform.height);
    });
    
    // Draw power-ups
    powerups.forEach(powerup => powerup.draw());
    
    // Draw player
    player.draw();
    
    // Draw enemies
    enemies.forEach(enemy => enemy.draw());
    
    // Draw bullets
    bullets.forEach(bullet => bullet.draw());
    
    // Draw UI
    ctx.fillStyle = COLORS.BLACK;
    ctx.font = '36px Arial';
    ctx.fillText(`Score: ${player.score}`, 10, 40);
    ctx.fillText(`Level: ${player.level}`, 10, 80);
    ctx.fillText(`High Score: ${player.highScore}`, 10, 120);
    ctx.fillText(`Multiplier: ${player.multiplier.toFixed(1)}x`, 10, 160);
    
    if (player.rapidFire) {
        ctx.fillStyle = COLORS.GOLD;
        ctx.fillText('Rapid Fire!', SCREEN_WIDTH - 150, 40);
    }
    if (player.shield) {
        ctx.fillStyle = COLORS.BLUE;
        ctx.fillText('Shield!', SCREEN_WIDTH - 150, 80);
    }
}

function gameLoop(timestamp) {
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    update();
    draw();
    
    requestAnimationFrame(gameLoop);
}

// Start the game
init();
requestAnimationFrame(gameLoop);