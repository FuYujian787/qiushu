/**
 * Surf Game - A canvas-based surfing game with physics and animations
 * This game features a surfer character that navigates through waves and obstacles
 * Game includes: physics engine, collision detection, scoring system, power-ups, and multiple levels
 */

// Game Constants
const GameConstants = {
    CANVAS_WIDTH: 800,
    CANVAS_HEIGHT: 600,
    GRAVITY: 0.4, // 降低重力，让跳跃更流畅
    WATER_LEVEL: 500,
    SURFER_WIDTH: 40,
    SURFER_HEIGHT: 60,
    JUMP_FORCE: -14, // 增加跳跃力
    MOVE_SPEED: 6, // 增加移动速度
    WAVE_SPEED: 2.5, // 降低波浪速度
    OBSTACLE_SPEED: 3.5, // 降低障碍物速度
    POWERUP_SPEED: 2,
    INITIAL_LIVES: 5, // 增加初始生命值
    SCORE_PER_WAVE: 10,
    SCORE_PER_OBSTACLE: 50,
    SCORE_PER_POWERUP: 100,
    LEVEL_THRESHOLDS: [20000, 50000, 90000, 140000, 200000], // 提高关卡阈值
    MAX_LEVEL: 5
};

// Game State
const GameState = {
    RUNNING: 'running',
    PAUSED: 'paused',
    GAME_OVER: 'game_over',
    LEVEL_COMPLETE: 'level_complete',
    TUTORIAL: 'tutorial'
};

// Main Game Class
class SurfGame {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = GameConstants.CANVAS_WIDTH;
        this.canvas.height = GameConstants.CANVAS_HEIGHT;
        
        this.state = GameState.RUNNING;
        this.score = 0;
        this.level = 1;
        this.lives = GameConstants.INITIAL_LIVES;
        this.gameTime = 0;
        
        // Game objects
        this.surfer = new Surfer();
        this.waves = [];
        this.obstacles = [];
        this.powerups = [];
        this.particles = [];
        this.scorePopups = [];
        
        // Game controls
        this.keys = {};
        this.mouse = { x: 0, y: 0 };
        
        // Initialize game
        this.init();
        this.setupEventListeners();
    }
    
    init() {
        // 预加载障碍物图片【核心修改：路径加image/】
        this.obstacleImgs = {
            rock: new Image(),
            buoy: new Image(),
            seagull: new Image(),
            boat: new Image()
        };
    // 路径格式：images/图片名.png （确保图片名和这里完全一致，区分大小写！）
    this.obstacleImgs.rock.src = 'images/rock.jpg';
    this.obstacleImgs.buoy.src = 'images/life buoy.png';
    this.obstacleImgs.seagull.src = 'images/seagull.png';
    this.obstacleImgs.boat.src = 'images/boat.png';
        // Create initial waves
        for (let i = 0; i < 5; i++) {
            this.waves.push(new Wave(i * 200));
        }
        
        // Create initial obstacles
        this.spawnObstacle();
        this.spawnObstacle();
        
        // Start game loop
        this.lastTime = performance.now();
        this.gameLoop();
    }
    
    setupEventListeners() {
        // Keyboard controls
        window.addEventListener('keydown', (e) => {
            this.keys[e.key.toLowerCase()] = true;
            
            // Space to jump
            if (e.key === ' ' && this.state === GameState.RUNNING) {
                this.surfer.jump();
                e.preventDefault();
            }
            
            // P to pause
            if (e.key === 'p' || e.key === 'P') {
                this.togglePause();
            }
            
            // R to restart
            if (e.key === 'r' || e.key === 'R') {
                this.restart();
            }
        });
        
        window.addEventListener('keyup', (e) => {
            this.keys[e.key.toLowerCase()] = false;
        });
        
        // Mouse controls
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mouse.x = e.clientX - rect.left;
            this.mouse.y = e.clientY - rect.top;
        });
        
        this.canvas.addEventListener('click', (e) => {
            if (this.state === GameState.GAME_OVER) {
                this.restart();
            }
        });
        
        // Touch controls for mobile
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (this.state === GameState.RUNNING) {
                this.surfer.jump();
            }
        });
        
        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const rect = this.canvas.getBoundingClientRect();
            const touch = e.touches[0];
            this.mouse.x = touch.clientX - rect.left;
            this.mouse.y = touch.clientY - rect.top;
        });
    }
    
    gameLoop(currentTime = performance.now()) {
        const deltaTime = Math.min(currentTime - this.lastTime, 100) / 16.67;
        this.lastTime = currentTime;
        
        if (this.state === GameState.RUNNING) {
            this.update(deltaTime);
            this.gameTime += deltaTime;
        }
        
        this.draw();
        
        requestAnimationFrame((time) => this.gameLoop(time));
    }
    
    update(deltaTime) {
        // Update surfer
        this.surfer.update(deltaTime, this.keys);
        
        // Update waves with manual loop for better performance
        for (let i = 0; i < this.waves.length; i++) {
            this.waves[i].update(deltaTime);
        }
        
        // Remove off-screen waves and add new ones
        let waveIndex = 0;
        while (waveIndex < this.waves.length) {
            if (this.waves[waveIndex].x <= -this.waves[waveIndex].width) {
                this.waves.splice(waveIndex, 1);
            } else {
                waveIndex++;
            }
        }
        
        if (this.waves.length < 5) {
            this.waves.push(new Wave(GameConstants.CANVAS_WIDTH));
        }
        
        // Update obstacles with manual loop
        for (let i = 0; i < this.obstacles.length; i++) {
            this.obstacles[i].update(deltaTime);
        }
        
        // Remove off-screen obstacles
        let obstacleIndex = 0;
        while (obstacleIndex < this.obstacles.length) {
            if (this.obstacles[obstacleIndex].x <= -this.obstacles[obstacleIndex].width) {
                this.obstacles.splice(obstacleIndex, 1);
            } else {
                obstacleIndex++;
            }
        }
        
        // Spawn new obstacles with improved logic
        if (Math.random() < 0.01 * deltaTime && this.obstacles.length < 3 + this.level) {
            this.spawnObstacle();
        }
        
        // Update powerups with manual loop
        for (let i = 0; i < this.powerups.length; i++) {
            this.powerups[i].update(deltaTime);
        }
        
        // Remove off-screen powerups
        let powerupIndex = 0;
        while (powerupIndex < this.powerups.length) {
            if (this.powerups[powerupIndex].x <= -this.powerups[powerupIndex].width) {
                this.powerups.splice(powerupIndex, 1);
            } else {
                powerupIndex++;
            }
        }
        
        // Spawn powerups
        if (Math.random() < 0.005 * deltaTime && this.powerups.length < 2) {
            this.spawnPowerup();
        }
        
        // Update particles with manual loop
        let particleIndex = 0;
        while (particleIndex < this.particles.length) {
            this.particles[particleIndex].update(deltaTime);
            if (this.particles[particleIndex].life <= 0) {
                this.particles.splice(particleIndex, 1);
            } else {
                particleIndex++;
            }
        }
        
        // Check collisions
        this.checkCollisions();
        
        // Check level progression
        this.checkLevel();
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#87CEEB';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw sky gradient
        const skyGradient = this.ctx.createLinearGradient(0, 0, 0, GameConstants.WATER_LEVEL);
        skyGradient.addColorStop(0, '#87CEEB');
        skyGradient.addColorStop(1, '#E0F7FF');
        this.ctx.fillStyle = skyGradient;
        this.ctx.fillRect(0, 0, this.canvas.width, GameConstants.WATER_LEVEL);
        
        // Draw sun
        this.ctx.fillStyle = '#FFD700';
        this.ctx.beginPath();
        this.ctx.arc(700, 80, 40, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw clouds
        this.drawClouds();
        
        // Draw water
        this.ctx.fillStyle = '#1E90FF';
        this.ctx.fillRect(0, GameConstants.WATER_LEVEL, this.canvas.width, 
                         this.canvas.height - GameConstants.WATER_LEVEL);
        
        // Draw waves with manual loop for better performance
        for (let i = 0; i < this.waves.length; i++) {
            this.waves[i].draw(this.ctx);
        }
        
        // Draw obstacles with manual loop
        for (let i = 0; i < this.obstacles.length; i++) {
            this.obstacles[i].draw(this.ctx);
        }
        
        // Draw powerups with manual loop
        for (let i = 0; i < this.powerups.length; i++) {
            this.powerups[i].draw(this.ctx);
        }
        
        // Draw particles with manual loop
        for (let i = 0; i < this.particles.length; i++) {
            this.particles[i].draw(this.ctx);
        }
        
        // Draw surfer
        this.surfer.draw(this.ctx);
        
        // Draw UI
        this.drawUI();
        
        // Draw game state messages
        if (this.state === GameState.PAUSED) {
            this.drawMessage('游戏暂停', '按 P 继续', '#FFA500');
        } else if (this.state === GameState.GAME_OVER) {
            this.drawMessage('游戏结束', `得分: ${this.score} - 点击或按 R 重新开始`, '#FF0000');
        } else if (this.state === GameState.LEVEL_COMPLETE) {
            this.drawMessage(`第 ${this.level} 关完成!`, '准备进入下一关...', '#00FF00');
        }
    }
    
    drawClouds() {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        
        // Cloud 1
        this.ctx.beginPath();
        this.ctx.arc(100 + Math.sin(this.gameTime * 0.001) * 20, 100, 30, 0, Math.PI * 2);
        this.ctx.arc(140 + Math.sin(this.gameTime * 0.001) * 20, 90, 40, 0, Math.PI * 2);
        this.ctx.arc(180 + Math.sin(this.gameTime * 0.001) * 20, 100, 30, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Cloud 2
        this.ctx.beginPath();
        this.ctx.arc(400 + Math.cos(this.gameTime * 0.0015) * 30, 150, 25, 0, Math.PI * 2);
        this.ctx.arc(440 + Math.cos(this.gameTime * 0.0015) * 30, 140, 35, 0, Math.PI * 2);
        this.ctx.arc(480 + Math.cos(this.gameTime * 0.0015) * 30, 150, 25, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    drawUI() {
        // Score
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = 'bold 24px Arial';
        this.ctx.fillText(`得分: ${this.score}`, 20, 40);
        
        // Level
        this.ctx.fillText(`关卡: ${this.level}/${GameConstants.MAX_LEVEL}`, 20, 80);
        
        // Lives
        this.ctx.fillText(`生命: ${this.lives}`, 20, 120);
        
        // Time
        const minutes = Math.floor(this.gameTime / 60);
        const seconds = Math.floor(this.gameTime % 60);
        this.ctx.fillText(`时间: ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`, 20, 160);
        
        // Controls help
        this.ctx.font = '14px Arial';
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        this.ctx.fillText('控制: 空格/点击跳跃, P暂停, R重新开始', 20, this.canvas.height - 20);
        
        // Next level progress
        if (this.level < GameConstants.MAX_LEVEL) {
            const nextLevelScore = GameConstants.LEVEL_THRESHOLDS[this.level - 1];
            const progress = Math.min(this.score / nextLevelScore, 1);
            
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            this.ctx.fillRect(20, this.canvas.height - 60, 200, 20);
            
            this.ctx.fillStyle = '#00FF00';
            this.ctx.fillRect(20, this.canvas.height - 60, 200 * progress, 20);
            
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.font = '12px Arial';
            this.ctx.fillText(`下一关: ${this.score}/${nextLevelScore}`, 25, this.canvas.height - 45);
        }
    }
    
    drawMessage(title, subtitle, color) {
        // Dark overlay
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Message box
        const boxWidth = 400;
        const boxHeight = 200;
        const boxX = (this.canvas.width - boxWidth) / 2;
        const boxY = (this.canvas.height - boxHeight) / 2;
        
        this.ctx.fillStyle = '#2C3E50';
        this.ctx.fillRect(boxX, boxY, boxWidth, boxHeight);
        
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);
        
        // Title
        this.ctx.fillStyle = color;
        this.ctx.font = 'bold 36px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(title, this.canvas.width / 2, boxY + 70);
        
        // Subtitle
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = '20px Arial';
        this.ctx.fillText(subtitle, this.canvas.width / 2, boxY + 120);
        
        this.ctx.textAlign = 'left';
    }
    
    spawnObstacle() {
        const types = ['rock', 'buoy', 'seagull', 'boat'];
        const type = types[Math.floor(Math.random() * types.length)];
        const y = GameConstants.WATER_LEVEL - 30 - Math.random() * 100;
        this.obstacles.push(new Obstacle(type, y));
    }
    
    spawnPowerup() {
        const types = ['speed', 'shield', 'doubleScore', 'extraLife'];
        const type = types[Math.floor(Math.random() * types.length)];
        const y = GameConstants.WATER_LEVEL - 50 - Math.random() * 150;
        this.powerups.push(new PowerUp(type, y));
    }
    
    checkCollisions() {
        // Check obstacle collisions
        for (let i = this.obstacles.length - 1; i >= 0; i--) {
            const obstacle = this.obstacles[i];
            if (this.surfer.collidesWith(obstacle)) {
                if (this.surfer.hasShield) {
                    this.surfer.hasShield = false;
                    this.createParticles(obstacle.x + obstacle.width / 2, 
                                       obstacle.y + obstacle.height / 2, 20, '#00FFFF');
                    this.score += GameConstants.SCORE_PER_OBSTACLE;
                } else {
                    this.lives--;
                    this.createParticles(this.surfer.x + this.surfer.width / 2,
                                       this.surfer.y + this.surfer.height / 2, 30, '#FF0000');
                    
                    if (this.lives <= 0) {
                        this.state = GameState.GAME_OVER;
                    }
                }
                
                // Remove obstacle immediately
                this.obstacles.splice(i, 1);
            }
        }
        
        // Check powerup collisions
        for (let i = this.powerups.length - 1; i >= 0; i--) {
            const powerup = this.powerups[i];
            if (this.surfer.collidesWith(powerup)) {
                this.applyPowerup(powerup.type);
                this.createParticles(powerup.x + powerup.width / 2,
                                   powerup.y + powerup.height / 2, 25, '#FFFF00');
                
                // Remove powerup immediately
                this.powerups.splice(i, 1);
            }
        }
        
        // Check wave riding (score points)
        for (let i = 0; i < this.waves.length; i++) {
            const wave = this.waves[i];
            if (this.surfer.isRidingWave(wave)) {
                this.score += GameConstants.SCORE_PER_WAVE * (this.surfer.doubleScore ? 2 : 1);
            }
        }
    }
    
    applyPowerup(type) {
        this.score += GameConstants.SCORE_PER_POWERUP;
        
        switch (type) {
            case 'speed':
                this.surfer.speedBoost = true;
                setTimeout(() => {
                    this.surfer.speedBoost = false;
                }, 5000);
                break;
                
            case 'shield':
                this.surfer.hasShield = true;
                setTimeout(() => {
                    this.surfer.hasShield = false;
                }, 8000);
                break;
                
            case 'doubleScore':
                this.surfer.doubleScore = true;
                setTimeout(() => {
                    this.surfer.doubleScore = false;
                }, 10000);
                break;
                
            case 'extraLife':
                this.lives = Math.min(this.lives + 1, 5);
                break;
        }
    }
    
    createParticles(x, y, count, color) {
        for (let i = 0; i < count; i++) {
            this.particles.push(new Particle(x, y, color));
        }
    }
    
    checkLevel() {
        if (this.level < GameConstants.MAX_LEVEL) {
            const nextLevelScore = GameConstants.LEVEL_THRESHOLDS[this.level - 1];
            
            if (this.score >= nextLevelScore) {
                this.state = GameState.LEVEL_COMPLETE;
                
                setTimeout(() => {
                    this.level++;
                    this.state = GameState.RUNNING;
                    
                    // Increase difficulty
                    GameConstants.OBSTACLE_SPEED += 0.5;
                    GameConstants.WAVE_SPEED += 0.2;
                    
                    // Reset surfer position
                    this.surfer.x = 100;
                    this.surfer.y = GameConstants.WATER_LEVEL - GameConstants.SURFER_HEIGHT;
                    this.surfer.velocityY = 0;
                    
                    // Clear obstacles and powerups
                    this.obstacles = [];
                    this.powerups = [];
                    
                    // Add some initial obstacles
                    this.spawnObstacle();
                    this.spawnObstacle();
                    
                }, 2000);
            }
        }
    }
    
    togglePause() {
        if (this.state === GameState.RUNNING) {
            this.state = GameState.PAUSED;
        } else if (this.state === GameState.PAUSED) {
            this.state = GameState.RUNNING;
        }
    }
    
    restart() {
        this.state = GameState.RUNNING;
        this.score = 0;
        this.level = 1;
        this.lives = GameConstants.INITIAL_LIVES;
        this.gameTime = 0;
        
        // Reset game constants
        GameConstants.OBSTACLE_SPEED = 4;
        GameConstants.WAVE_SPEED = 3;
        
        // Reset game objects
        this.surfer = new Surfer();
        this.waves = [];
        this.obstacles = [];
        this.powerups = [];
        this.particles = [];
        
        // Reinitialize
        this.init();
    }
}

// Surfer Class
class Surfer {
    constructor() {
        this.width = GameConstants.SURFER_WIDTH;
        this.height = GameConstants.SURFER_HEIGHT;
        this.x = 100;
        this.y = GameConstants.WATER_LEVEL - this.height;
        this.velocityY = 0;
        this.isJumping = false;
        this.speedBoost = false;
        this.hasShield = false;
        this.doubleScore = false;
        this.animationFrame = 0;
        this.animationTimer = 0;
    }
    
    update(deltaTime, keys) {
        // Apply gravity
        this.velocityY += GameConstants.GRAVITY;
        this.y += this.velocityY;
        
        // Keep surfer above water
        if (this.y > GameConstants.WATER_LEVEL - this.height) {
            this.y = GameConstants.WATER_LEVEL - this.height;
            this.velocityY = 0;
            this.isJumping = false;
        }
        
        // Horizontal movement
        const moveSpeed = this.speedBoost ? GameConstants.MOVE_SPEED * 1.5 : GameConstants.MOVE_SPEED;
        
        if (keys['arrowleft'] || keys['a']) {
            this.x -= moveSpeed;
        }
        if (keys['arrowright'] || keys['d']) {
            this.x += moveSpeed;
        }
        
        // Keep surfer in bounds
        this.x = Math.max(0, Math.min(this.x, GameConstants.CANVAS_WIDTH - this.width));
        
        // Update animation
        this.animationTimer += deltaTime;
        if (this.animationTimer > 0.1) {
            this.animationFrame = (this.animationFrame + 1) % 4;
            this.animationTimer = 0;
        }
    }
    
    jump() {
        if (!this.isJumping) {
            this.velocityY = GameConstants.JUMP_FORCE;
            this.isJumping = true;
        }
    }
    
    draw(ctx) {
        // Draw surfer body
        ctx.fillStyle = this.hasShield ? '#00FFFF' : '#FF6B6B';
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // Draw surfer head
        ctx.fillStyle = '#FFDAB9';
        ctx.beginPath();
        ctx.arc(this.x + this.width / 2, this.y - 10, 15, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw surfboard
        ctx.fillStyle = this.speedBoost ? '#FF4500' : '#32CD32';
        ctx.fillRect(this.x - 5, this.y + this.height - 10, this.width + 10, 10);
        
        // Draw animation effect
        if (this.isJumping) {
            ctx.strokeStyle = '#FFFF00';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(this.x + this.width / 2, this.y + this.height, 20, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        // Draw powerup effects
        if (this.doubleScore) {
            ctx.fillStyle = 'rgba(255, 215, 0, 0.3)';
            ctx.beginPath();
            ctx.arc(this.x + this.width / 2, this.y + this.height / 2, 30, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    collidesWith(object) {
        return this.x < object.x + object.width &&
               this.x + this.width > object.x &&
               this.y < object.y + object.height &&
               this.y + this.height > object.y;
    }
    
    isRidingWave(wave) {
        return this.x + this.width > wave.x &&
               this.x < wave.x + wave.width &&
               Math.abs(this.y + this.height - wave.y) < 10;
    }
}

// Wave Class
class Wave {
    constructor(x) {
        this.x = x;
        this.y = GameConstants.WATER_LEVEL;
        this.width = 200;
        this.height = 40;
        this.speed = GameConstants.WAVE_SPEED;
        this.amplitude = 15;
        this.frequency = 0.02;
        this.phase = Math.random() * Math.PI * 2;
    }
    
    update(deltaTime) {
        this.x -= this.speed * deltaTime;
        this.phase += 0.05 * deltaTime;
    }
    
    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        
        // Draw wave shape
        ctx.beginPath();
        ctx.moveTo(0, 0);
        
        for (let i = 0; i <= this.width; i += 5) {
            const y = Math.sin(i * this.frequency + this.phase) * this.amplitude;
            ctx.lineTo(i, y);
        }
        
        ctx.lineTo(this.width, this.height);
        ctx.lineTo(0, this.height);
        ctx.closePath();
        
        // Fill wave
        const waveGradient = ctx.createLinearGradient(0, -this.amplitude, 0, this.height);
        waveGradient.addColorStop(0, 'rgba(30, 144, 255, 0.8)');
        waveGradient.addColorStop(1, 'rgba(30, 144, 255, 0.3)');
        ctx.fillStyle = waveGradient;
        ctx.fill();
        
        // Draw wave foam
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.beginPath();
        ctx.moveTo(0, 0);
        
        for (let i = 0; i <= this.width; i += 3) {
            const y = Math.sin(i * this.frequency + this.phase) * this.amplitude * 0.7;
            ctx.lineTo(i, y);
        }
        
        ctx.lineTo(this.width, 0);
        ctx.closePath();
        ctx.fill();
        
        ctx.restore();
    }
}

// Obstacle Class
class Obstacle {
    constructor(type, y) {
        this.type = type;
        this.x = GameConstants.CANVAS_WIDTH;
        this.y = y;
        this.width = this.getWidth();
        this.height = this.getHeight();
        this.speed = GameConstants.OBSTACLE_SPEED;
        this.animation = 0;
    }
    
    getWidth() {
        switch (this.type) {
            case 'rock': return 40;
            case 'buoy': return 30;
            case 'seagull': return 50;
            case 'boat': return 80;
            default: return 40;
        }
    }
    
    getHeight() {
        switch (this.type) {
            case 'rock': return 40;
            case 'buoy': return 50;
            case 'seagull': return 30;
            case 'boat': return 60;
            default: return 40;
        }
    }
    
    update(deltaTime) {
        this.x -= this.speed * deltaTime;
        this.animation += deltaTime;
        
        // Animate certain obstacles
        if (this.type === 'seagull') {
            this.y += Math.sin(this.animation * 3) * 2;
        } else if (this.type === 'buoy') {
            this.y += Math.sin(this.animation * 2) * 3;
        }
    }
    
    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        const game = window.surfGame;
    if (game && game.obstacleImgs[this.type] && game.obstacleImgs[this.type].complete) {
        // 绘制图片：适配障碍物宽高，0,0对应translate后的相对坐标，不偏移
        ctx.drawImage(
            game.obstacleImgs[this.type], // 对应类型的图片
            0, 0, // 图片绘制的起始坐标（相对障碍物自身，无需修改）
            this.width, this.height // 适配原有宽高，不拉伸
        );
    }
    ctx.restore(); // 原有坐标逻辑，保留！
}
}
    
// PowerUp Class
class PowerUp {
    constructor(type, y) {
        this.type = type;
        this.x = GameConstants.CANVAS_WIDTH;
        this.y = y;
        this.width = 30;
        this.height = 30;
        this.speed = GameConstants.POWERUP_SPEED;
        this.rotation = 0;
        this.pulse = 0;
    }
    
    update(deltaTime) {
        this.x -= this.speed * deltaTime;
        this.rotation += 0.05 * deltaTime;
        this.pulse += 0.1 * deltaTime;
    }
    
    draw(ctx) {
        ctx.save();
        ctx.translate(this.x + this.width / 2, this.y + this.height / 2);
        ctx.rotate(this.rotation);
        
        const pulseSize = 1 + Math.sin(this.pulse) * 0.2;
        ctx.scale(pulseSize, pulseSize);
        
        // Draw glow effect
        const glowRadius = this.width * 1.5;
        const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, glowRadius);
        gradient.addColorStop(0, this.getColor());
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(0, 0, glowRadius, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw powerup icon
        ctx.fillStyle = '#FFFFFF';
        
        switch (this.type) {
            case 'speed':
                // Lightning bolt
                ctx.beginPath();
                ctx.moveTo(-5, -10);
                ctx.lineTo(5, 0);
                ctx.lineTo(-5, 0);
                ctx.lineTo(5, 10);
                ctx.closePath();
                ctx.fill();
                break;
                
            case 'shield':
                // Shield
                ctx.beginPath();
                ctx.arc(0, 0, 10, 0, Math.PI * 2);
                ctx.strokeStyle = '#FFFFFF';
                ctx.lineWidth = 3;
                ctx.stroke();
                break;
                
            case 'doubleScore':
                // 2x symbol
                ctx.font = 'bold 16px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('2x', 0, 0);
                break;
                
            case 'extraLife':
                // Heart
                ctx.beginPath();
                ctx.moveTo(0, -5);
                ctx.bezierCurveTo(5, -10, 10, -5, 0, 5);
                ctx.bezierCurveTo(-10, -5, -5, -10, 0, -5);
                ctx.fill();
                break;
        }
        
        ctx.restore();
    }
    
    getColor() {
        switch (this.type) {
            case 'speed': return '#FF4500';
            case 'shield': return '#00FFFF';
            case 'doubleScore': return '#FFFF00';
            case 'extraLife': return '#FF69B4';
            default: return '#FFFFFF';
        }
    }
}

// Particle Class
class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.size = Math.random() * 5 + 2;
        this.speedX = Math.random() * 6 - 3;
        this.speedY = Math.random() * 6 - 3;
        this.life = 1.0;
        this.decay = Math.random() * 0.02 + 0.01;
    }
    
    update(deltaTime) {
        this.x += this.speedX * deltaTime;
        this.y += this.speedY * deltaTime;
        this.life -= this.decay * deltaTime;
        this.size *= 0.99;
    }
    
    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
}

// Initialize game when page loads - Commented out because we use ImprovedSurfGame below
// window.addEventListener('DOMContentLoaded', () => {
//     const game = new SurfGame('surf-game-canvas');
//     window.surfGame = game; // Make game accessible from console
// });

// Sound Manager Class
class SoundManager {
    constructor() {
        this.sounds = {};
        this.muted = false;
        this.volume = 0.5;
    }
    
    loadSound(name, url) {
        // In a real implementation, this would load audio files
        // For this demo, we'll simulate sounds with Web Audio API or console logs
        this.sounds[name] = { name, url, loaded: true };
        console.log(`Sound loaded: ${name}`);
    }
    
    play(name, volume = 1.0) {
        if (this.muted || !this.sounds[name]) return;
        
        const effectiveVolume = this.volume * volume;
        console.log(`Playing sound: ${name} at volume ${effectiveVolume}`);
        
        // In a real implementation, this would play the actual sound
        // For now, we'll just log it
        return { name, volume: effectiveVolume };
    }
    
    stop(name) {
        console.log(`Stopping sound: ${name}`);
    }
    
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        console.log(`Volume set to: ${this.volume}`);
    }
    
    toggleMute() {
        this.muted = !this.muted;
        console.log(`Sound ${this.muted ? 'muted' : 'unmuted'}`);
        return this.muted;
    }
}

// High Score Manager Class
class HighScoreManager {
    constructor() {
        this.storageKey = 'surfGameHighScores';
        this.maxScores = 10;
        this.scores = this.loadScores();
    }
    
    loadScores() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            console.error('Failed to load high scores:', e);
            return [];
        }
    }
    
    saveScores() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.scores));
        } catch (e) {
            console.error('Failed to save high scores:', e);
        }
    }
    
    addScore(name, score, level, time) {
        const newScore = {
            name,
            score,
            level,
            time,
            date: new Date().toISOString()
        };
        
        this.scores.push(newScore);
        this.scores.sort((a, b) => b.score - a.score);
        this.scores = this.scores.slice(0, this.maxScores);
        this.saveScores();
        
        return this.getRank(score);
    }
    
    getRank(score) {
        for (let i = 0; i < this.scores.length; i++) {
            if (score > this.scores[i].score) {
                return i + 1;
            }
        }
        return this.scores.length + 1;
    }
    
    getTopScores(count = 5) {
        return this.scores.slice(0, count);
    }
    
    clearScores() {
        this.scores = [];
        this.saveScores();
    }
}

// Achievement System
class AchievementSystem {
    constructor() {
        this.achievements = [
            { id: 'first_game', name: '初次冲浪', description: '完成第一次游戏', unlocked: false },
            { id: 'score_1000', name: '千分达人', description: '单局得分超过1000', unlocked: false },
            { id: 'level_5', name: '冲浪大师', description: '达到第5关', unlocked: false },
            { id: 'no_damage', name: '完美闪避', description: '一局游戏中不受任何伤害', unlocked: false },
            { id: 'collect_10', name: '道具收集者', description: '单局收集10个能量道具', unlocked: false },
            { id: 'time_300', name: '持久战', description: '单局游戏时间超过5分钟', unlocked: false },
            { id: 'combo_10', name: '连击高手', description: '连续躲避10个障碍物', unlocked: false },
            { id: 'all_powerups', name: '全能选手', description: '在一局中收集所有类型的能量道具', unlocked: false }
        ];
        
        this.storageKey = 'surfGameAchievements';
        this.loadAchievements();
    }
    
    loadAchievements() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                const savedAchievements = JSON.parse(saved);
                this.achievements = this.achievements.map(ach => {
                    const saved = savedAchievements.find(s => s.id === ach.id);
                    return saved ? { ...ach, unlocked: saved.unlocked } : ach;
                });
            }
        } catch (e) {
            console.error('Failed to load achievements:', e);
        }
    }
    
    saveAchievements() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.achievements));
        } catch (e) {
            console.error('Failed to save achievements:', e);
        }
    }
    
    unlockAchievement(id) {
        const achievement = this.achievements.find(a => a.id === id);
        if (achievement && !achievement.unlocked) {
            achievement.unlocked = true;
            this.saveAchievements();
            console.log(`成就解锁: ${achievement.name} - ${achievement.description}`);
            return achievement;
        }
        return null;
    }
    
    checkAchievements(gameStats) {
        const unlocked = [];
        
        if (gameStats.gamesPlayed >= 1) {
            const ach = this.unlockAchievement('first_game');
            if (ach) unlocked.push(ach);
        }
        
        if (gameStats.highestScore >= 1000) {
            const ach = this.unlockAchievement('score_1000');
            if (ach) unlocked.push(ach);
        }
        
        if (gameStats.highestLevel >= 5) {
            const ach = this.unlockAchievement('level_5');
            if (ach) unlocked.push(ach);
        }
        
        if (gameStats.noDamageGames > 0) {
            const ach = this.unlockAchievement('no_damage');
            if (ach) unlocked.push(ach);
        }
        
        if (gameStats.maxPowerupsCollected >= 10) {
            const ach = this.unlockAchievement('collect_10');
            if (ach) unlocked.push(ach);
        }
        
        if (gameStats.maxGameTime >= 300) {
            const ach = this.unlockAchievement('time_300');
            if (ach) unlocked.push(ach);
        }
        
        if (gameStats.maxCombo >= 10) {
            const ach = this.unlockAchievement('combo_10');
            if (ach) unlocked.push(ach);
        }
        
        if (gameStats.allPowerupTypes) {
            const ach = this.unlockAchievement('all_powerups');
            if (ach) unlocked.push(ach);
        }
        
        return unlocked;
    }
    
    getUnlockedAchievements() {
        return this.achievements.filter(a => a.unlocked);
    }
    
    getLockedAchievements() {
        return this.achievements.filter(a => !a.unlocked);
    }
}

// Game Statistics Tracker
class GameStatistics {
    constructor() {
        this.storageKey = 'surfGameStatistics';
        this.stats = this.loadStats();
    }
    
    loadStats() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            return saved ? JSON.parse(saved) : {
                gamesPlayed: 0,
                totalScore: 0,
                highestScore: 0,
                totalTime: 0,
                highestLevel: 0,
                obstaclesAvoided: 0,
                powerupsCollected: 0,
                wavesRidden: 0,
                noDamageGames: 0,
                maxCombo: 0,
                maxPowerupsCollected: 0,
                maxGameTime: 0,
                allPowerupTypes: false
            };
        } catch (e) {
            console.error('Failed to load statistics:', e);
            return this.getDefaultStats();
        }
    }
    
    getDefaultStats() {
        return {
            gamesPlayed: 0,
            totalScore: 0,
            highestScore: 0,
            totalTime: 0,
            highestLevel: 0,
            obstaclesAvoided: 0,
            powerupsCollected: 0,
            wavesRidden: 0,
            noDamageGames: 0,
            maxCombo: 0,
            maxPowerupsCollected: 0,
            maxGameTime: 0,
            allPowerupTypes: false
        };
    }
    
    saveStats() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.stats));
        } catch (e) {
            console.error('Failed to save statistics:', e);
        }
    }
    
    recordGame(gameData) {
        this.stats.gamesPlayed++;
        this.stats.totalScore += gameData.score;
        this.stats.totalTime += gameData.time;
        
        if (gameData.score > this.stats.highestScore) {
            this.stats.highestScore = gameData.score;
        }
        
        if (gameData.level > this.stats.highestLevel) {
            this.stats.highestLevel = gameData.level;
        }
        
        if (gameData.time > this.stats.maxGameTime) {
            this.stats.maxGameTime = gameData.time;
        }
        
        if (gameData.powerupsCollected > this.stats.maxPowerupsCollected) {
            this.stats.maxPowerupsCollected = gameData.powerupsCollected;
        }
        
        if (gameData.combo > this.stats.maxCombo) {
            this.stats.maxCombo = gameData.combo;
        }
        
        if (gameData.noDamage) {
            this.stats.noDamageGames++;
        }
        
        if (gameData.allPowerupTypes) {
            this.stats.allPowerupTypes = true;
        }
        
        this.saveStats();
        return this.stats;
    }
    
    resetStats() {
        this.stats = this.getDefaultStats();
        this.saveStats();
    }
    
    getStats() {
        return { ...this.stats };
    }
}

// Enhanced SurfGame with new features
class EnhancedSurfGame extends SurfGame {
    constructor(canvasId) {
        super(canvasId);
        
        // Add new systems
        this.soundManager = new SoundManager();
        this.highScoreManager = new HighScoreManager();
        this.achievementSystem = new AchievementSystem();
        this.gameStatistics = new GameStatistics();
        
        // Enhanced game state
        this.combo = 0;
        this.maxCombo = 0;
        this.powerupsCollected = 0;
        this.obstaclesAvoided = 0;
        this.wavesRidden = 0;
        this.currentGameData = {};
        this.collectedPowerupTypes = new Set();
        
        // Load sounds
        this.loadSounds();
    }
    
    loadSounds() {
        // Simulate loading sounds
        this.soundManager.loadSound('jump', 'sounds/jump.mp3');
        this.soundManager.loadSound('collect', 'sounds/collect.mp3');
        this.soundManager.loadSound('crash', 'sounds/crash.mp3');
        this.soundManager.loadSound('level_up', 'sounds/level_up.mp3');
        this.soundManager.loadSound('game_over', 'sounds/game_over.mp3');
        this.soundManager.loadSound('powerup', 'sounds/powerup.mp3');
    }
    
    update(deltaTime) {
        super.update(deltaTime);
        
        // Update combo system
        if (this.combo > 0) {
            this.combo -= deltaTime * 0.1;
            if (this.combo < 0) this.combo = 0;
        }
    }
    
    checkCollisions() {
        const previousLives = this.lives;
        
        super.checkCollisions();
        
        // Track obstacles avoided
        if (this.lives === previousLives && this.obstacles.length > 0) {
            this.obstaclesAvoided++;
            this.combo += 1;
            if (this.combo > this.maxCombo) {
                this.maxCombo = Math.floor(this.combo);
            }
        }
        
        // Track powerups collected
        this.powerups.forEach(powerup => {
            if (powerup.x < -1000) { // Was collected
                this.powerupsCollected++;
                this.collectedPowerupTypes.add(powerup.type);
                this.soundManager.play('collect');
            }
        });
        
        // Track waves ridden
        this.waves.forEach(wave => {
            if (this.surfer.isRidingWave(wave)) {
                this.wavesRidden++;
            }
        });
    }
    
    restart() {
        // Record previous game data
        if (this.state === GameState.GAME_OVER) {
            this.recordGameData();
        }
        
        // Reset enhanced stats
        this.combo = 0;
        this.maxCombo = 0;
        this.powerupsCollected = 0;
        this.obstaclesAvoided = 0;
        this.wavesRidden = 0;
        this.collectedPowerupTypes.clear();
        
        super.restart();
    }
    
    recordGameData() {
        this.currentGameData = {
            score: this.score,
            level: this.level,
            time: this.gameTime,
            lives: this.lives,
            combo: this.maxCombo,
            powerupsCollected: this.powerupsCollected,
            obstaclesAvoided: this.obstaclesAvoided,
            wavesRidden: this.wavesRidden,
            noDamage: this.lives === GameConstants.INITIAL_LIVES,
            allPowerupTypes: this.collectedPowerupTypes.size >= 4
        };
        
        // Update statistics
        this.gameStatistics.recordGame(this.currentGameData);
        
        // Check achievements
        this.achievementSystem.checkAchievements(this.gameStatistics.getStats());
        
        // Check high score
        const rank = this.highScoreManager.addScore(
            'Player',
            this.score,
            this.level,
            this.gameTime
        );
        
        if (rank <= 3) {
            console.log(`🎉 新纪录！排名第 ${rank} 名！`);
        }
    }
    
    drawUI() {
        super.drawUI();
        
        // Draw enhanced UI
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = 'bold 18px Arial';
        
        // Draw combo
        if (this.combo > 1) {
            this.ctx.fillStyle = this.getComboColor();
            this.ctx.fillText(`连击: x${this.combo.toFixed(1)}`, GameConstants.CANVAS_WIDTH - 150, 40);
        }
        
        // Draw collected powerups
        let powerupX = GameConstants.CANVAS_WIDTH - 200;
        this.ctx.font = '14px Arial';
        
        if (this.surfer.speedBoost) {
            this.ctx.fillStyle = '#FF4500';
            this.ctx.fillText('⚡', powerupX, 80);
            powerupX += 25;
        }
        
        if (this.surfer.hasShield) {
            this.ctx.fillStyle = '#00FFFF';
            this.ctx.fillText('🛡️', powerupX, 80);
            powerupX += 25;
        }
        
        if (this.surfer.doubleScore) {
            this.ctx.fillStyle = '#FFFF00';
            this.ctx.fillText('2×', powerupX, 80);
            powerupX += 25;
        }
    }
    
    getComboColor() {
        if (this.combo >= 10) return '#FF0000';
        if (this.combo >= 7) return '#FFA500';
        if (this.combo >= 4) return '#FFFF00';
        return '#00FF00';
    }
    
    drawMessage(title, subtitle, color) {
        super.drawMessage(title, subtitle, color);
        
        // Add high score display on game over
        if (this.state === GameState.GAME_OVER) {
            const topScores = this.highScoreManager.getTopScores(3);
            
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.font = '18px Arial';
            this.ctx.textAlign = 'center';
            
            let y = 350;
            this.ctx.fillText('🏆 高分榜 🏆', GameConstants.CANVAS_WIDTH / 2, y);
            
            topScores.forEach((score, index) => {
                y += 30;
                const minutes = Math.floor(score.time / 60);
                const seconds = Math.floor(score.time % 60);
                this.ctx.fillText(
                    `${index + 1}. ${score.name}: ${score.score}分 (第${score.level}关, ${minutes}:${seconds.toString().padStart(2, '0')})`,
                    GameConstants.CANVAS_WIDTH / 2,
                    y
                );
            });
            
            this.ctx.textAlign = 'left';
        }
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        SurfGame, 
        EnhancedSurfGame,
        Surfer, 
        Wave, 
        Obstacle, 
        PowerUp, 
        Particle,
        SoundManager,
        HighScoreManager,
        AchievementSystem,
        GameStatistics,
        GameConstants, 
        GameState 
    };
}

// Improved Enhanced SurfGame with better UX
class ImprovedSurfGame extends EnhancedSurfGame {
    constructor(canvasId) {
        super(canvasId);
        
        // Tutorial state
        this.tutorialStep = 0;
        this.tutorialMessages = [
            "欢迎来到冲浪游戏！使用 ←→ 或 A/D 键左右移动",
            "按空格键或点击屏幕跳跃躲避障碍物",
            "收集能量道具获得特殊能力",
            "尽可能获得高分，祝你好运！"
        ];
        
        // Show tutorial on first play
        const hasPlayedBefore = localStorage.getItem('surfGameHasPlayed');
        if (!hasPlayedBefore) {
            this.state = GameState.TUTORIAL;
            localStorage.setItem('surfGameHasPlayed', 'true');
        }
        
        // Visual effects
        this.screenShake = 0;
        this.flashEffect = 0;
        this.scorePopups = [];
        
        // Game balance improvements
        this.obstacleSpawnRate = 0.008;
        this.powerupSpawnRate = 0.004;
    }
    
    update(deltaTime) {
        // Update visual effects
        if (this.screenShake > 0) {
            this.screenShake -= deltaTime * 2;
            if (this.screenShake < 0) this.screenShake = 0;
        }
        
        if (this.flashEffect > 0) {
            this.flashEffect -= deltaTime * 3;
            if (this.flashEffect < 0) this.flashEffect = 0;
        }
        
        // Update score popups
        if (this.scorePopups && Array.isArray(this.scorePopups)) {
            this.scorePopups.forEach(popup => {
                popup.y -= deltaTime * 30;
                popup.life -= deltaTime * 0.5;
            });
            this.scorePopups = this.scorePopups.filter(p => p.life > 0);
        }
        
        // Skip tutorial if player presses any key
        if (this.state === GameState.TUTORIAL) {
            if (Object.keys(this.keys).length > 0) {
                this.state = GameState.RUNNING;
            }
            return;
        }
        
        super.update(deltaTime);
        
        // Adjust spawn rates based on performance
        if (this.lives < 3) {
            this.obstacleSpawnRate = 0.006; // Easier when struggling
            this.powerupSpawnRate = 0.005; // More powerups to help
        } else {
            this.obstacleSpawnRate = 0.008 + (this.level * 0.001);
            this.powerupSpawnRate = 0.004;
        }
    }
    
    spawnObstacle() {
        const types = ['rock', 'buoy', 'seagull', 'boat'];
        const type = types[Math.floor(Math.random() * types.length)];
        const y = GameConstants.WATER_LEVEL - 30 - Math.random() * 100;
        this.obstacles.push(new Obstacle(type, y));
    }
    
    spawnPowerup() {
        const types = ['speed', 'shield', 'doubleScore', 'extraLife'];
        const type = types[Math.floor(Math.random() * types.length)];
        const y = GameConstants.WATER_LEVEL - 50 - Math.random() * 150;
        this.powerups.push(new PowerUp(type, y));
    }
    
    checkCollisions() {
        const previousLives = this.lives;
        const previousScore = this.score;
        
        super.checkCollisions();
        
        // Add visual feedback for score changes
        if (this.score > previousScore) {
            const scoreDiff = this.score - previousScore;
            if (scoreDiff > 0) {
                this.createScorePopup(scoreDiff, this.surfer.x + this.surfer.width / 2, this.surfer.y);
            }
        }
        
        // Add screen shake when hit
        if (this.lives < previousLives) {
            this.screenShake = 1.0;
            this.flashEffect = 0.5;
        }
    }
    
    createScorePopup(score, x, y) {
        // this.scorePopups.push({
        //     score: `+${score}`,
        //     x: x,
        //     y: y,
        //     life: 1.0,
        //     color: score >= 100 ? '#FFFF00' : '#FFFFFF'
        // });
    }
    
    draw() {
        // Apply screen shake
        if (this.screenShake > 0) {
            const shakeX = (Math.random() - 0.5) * this.screenShake * 10;
            const shakeY = (Math.random() - 0.5) * this.screenShake * 10;
            this.ctx.translate(shakeX, shakeY);
        }
        
        super.draw();
        
        // Draw score popups
        this.scorePopups.forEach(popup => {
            this.ctx.save();
            this.ctx.globalAlpha = popup.life;
            this.ctx.fillStyle = popup.color;
            this.ctx.font = `bold ${20 + (1 - popup.life) * 10}px Arial`;
            this.ctx.textAlign = 'center';
            this.ctx.fillText(popup.score, popup.x, popup.y);
            this.ctx.restore();
        });
        
        // Draw flash effect
        if (this.flashEffect > 0) {
            this.ctx.fillStyle = `rgba(255, 0, 0, ${this.flashEffect * 0.3})`;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        }
        
        // Draw tutorial
        if (this.state === GameState.TUTORIAL) {
            this.drawTutorial();
        }
        
        // Reset transform if screen shake was applied
        if (this.screenShake > 0) {
            this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        }
    }
    
    drawTutorial() {
        // Dark overlay
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Tutorial box
        const boxWidth = 500;
        const boxHeight = 300;
        const boxX = (this.canvas.width - boxWidth) / 2;
        const boxY = (this.canvas.height - boxHeight) / 2;
        
        this.ctx.fillStyle = '#2C3E50';
        this.ctx.fillRect(boxX, boxY, boxWidth, boxHeight);
        
        this.ctx.strokeStyle = '#00FFFF';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);
        
        // Title
        this.ctx.fillStyle = '#00FFFF';
        this.ctx.font = 'bold 32px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('冲浪游戏教程', this.canvas.width / 2, boxY + 50);
        
        // Current tutorial message
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = '20px Arial';
        const message = this.tutorialMessages[this.tutorialStep];
        this.ctx.fillText(message, this.canvas.width / 2, boxY + 120);
        
        // Progress indicator
        this.ctx.font = '16px Arial';
        this.ctx.fillText(`(${this.tutorialStep + 1}/${this.tutorialMessages.length})`, this.canvas.width / 2, boxY + 160);
        
        // Instructions
        this.ctx.fillStyle = '#AAAAAA';
        this.ctx.font = '14px Arial';
        this.ctx.fillText('按任意键继续教程，按ESC跳过', this.canvas.width / 2, boxY + 200);
        
        // Draw controls visualization
        this.drawControlsVisualization(boxX + 50, boxY + 220);
        
        this.ctx.textAlign = 'left';
    }
    
    drawControlsVisualization(x, y) {
        this.ctx.save();
        this.ctx.translate(x, y);
        
        // Left/Right arrows
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = '20px Arial';
        this.ctx.fillText('← →', 0, 0);
        this.ctx.fillText('或 A D', 60, 0);
        
        // Space bar
        this.ctx.fillStyle = '#FFFF00';
        this.ctx.fillRect(150, -15, 100, 30);
        this.ctx.fillStyle = '#000000';
        this.ctx.font = '14px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('空格键', 200, 5);
        
        this.ctx.restore();
    }
    
    drawUI() {
        super.drawUI();
        
        // Draw improved UI elements
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = 'bold 16px Arial';
        
        // Draw performance indicator
        const performanceColor = this.getPerformanceColor();
        this.ctx.fillStyle = performanceColor;
        this.ctx.fillText('表现', GameConstants.CANVAS_WIDTH - 100, 120);
        
        // Draw performance bar
        const performance = Math.min(this.combo / 10, 1);
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        this.ctx.fillRect(GameConstants.CANVAS_WIDTH - 100, 130, 80, 10);
        this.ctx.fillStyle = performanceColor;
        this.ctx.fillRect(GameConstants.CANVAS_WIDTH - 100, 130, 80 * performance, 10);
        
        // Draw helpful tips
        if (this.gameTime < 10 && this.state === GameState.RUNNING) {
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
            this.ctx.font = '12px Arial';
            this.ctx.fillText('提示: 保持在波浪上可以获得额外分数', 20, this.canvas.height - 50);
        }
    }
    
    getPerformanceColor() {
        if (this.combo >= 8) return '#00FF00';
        if (this.combo >= 5) return '#FFFF00';
        if (this.combo >= 2) return '#FFA500';
        return '#FF0000';
    }
    
    setupEventListeners() {
        super.setupEventListeners();
        
        // Add tutorial navigation
        window.addEventListener('keydown', (e) => {
            if (this.state === GameState.TUTORIAL) {
                if (e.key === 'Escape') {
                    this.state = GameState.RUNNING;
                } else if (e.key === ' ' || e.key === 'Enter') {
                    this.tutorialStep = (this.tutorialStep + 1) % this.tutorialMessages.length;
                    if (this.tutorialStep === 0) {
                        this.state = GameState.RUNNING;
                    }
                }
            }
        });
        
        // Add click to advance tutorial
        this.canvas.addEventListener('click', (e) => {
            if (this.state === GameState.TUTORIAL) {
                this.tutorialStep = (this.tutorialStep + 1) % this.tutorialMessages.length;
                if (this.tutorialStep === 0) {
                    this.state = GameState.RUNNING;
                }
            }
        });
    }
    
    restart() {
        super.restart();
        this.tutorialStep = 0;
        this.screenShake = 0;
        this.flashEffect = 0;
        this.scorePopups = [];
        this.obstacleSpawnRate = 0.008;
        this.powerupSpawnRate = 0.004;
    }
}

// Initialize improved game when page loads
window.addEventListener('DOMContentLoaded', () => {
    const game = new ImprovedSurfGame('surf-game-canvas');
    window.surfGame = game; // Make game accessible from console
    
    // Add game info to console
    console.log('%c🎮 冲浪游戏已加载！', 'color: #00FFFF; font-size: 16px; font-weight: bold;');
    console.log('%c控制说明:', 'color: #FFFF00; font-weight: bold;');
    console.log('← → 或 A/D: 左右移动');
    console.log('空格键: 跳跃');
    console.log('P: 暂停游戏');
    console.log('R: 重新开始');
    console.log('在控制台输入 surfGame 可以访问游戏对象');
});
