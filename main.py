import pygame
from pygame import mixer
import math
import random

pygame.init()

screenWidth = 1280
screenHeight = 720
screen = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()
fps = 60

mixer.init()
playerShotSound = mixer.Sound("./Sounds/170161__timgormly__8-bit-laser.mp3")
enemyShooterSound = mixer.Sound("./Sounds/49242__zerolagtime__tape_slow5 reverb wav.wav")

class EnemyGenerator():
    def __init__(self):
        self.maxNumberOfShooters = 1
        self.maxNumberOfKamikazes = 1
        self.timeForIncreaseMaxShooters = 19
        self.timeForIncreaseMaxKamikazes = 15
        self.currentNumberOfShooters = 0
        self.currentNumberOfKamikazes = 0
        self.numberOfAnyEnemiesKilled = 0
        self.numberOfShootersKilled = 0
        self.numberOfKamikazesKilled = 0
        self.lastShooterIncreaseTime = pygame.time.get_ticks()
        self.lastKamikazeIncreaseTime = pygame.time.get_ticks()

    def generateRandomPositionOffScreen(self):
        x = random.choice([int(random.uniform(-150, screenWidth - 10)), int(random.uniform(screenWidth + 10, screenWidth + 150))])
        y = random.choice([int(random.uniform(screenHeight - 150, screenHeight + 300)), int(random.uniform(300 - screenHeight, 100 - screenHeight)) ])
        print(x, y)
        return (x, y)
    def createShootPoint(self):
        x = int(random.uniform(40, screenWidth - 40))
        y = int(random.uniform(40, screenHeight - 40))
        return (x, y)
    def createShooter(self):
        creationPosition = self.generateRandomPositionOffScreen()
        shooter = EnemyShooter(creationPosition[0], creationPosition[1], self.createShootPoint())
        self.currentNumberOfShooters += 1
        allSpritesGroup.add(shooter)
        enemiesGroup.add(shooter)
    def createKamikaze(self):
        creationPosition = self.generateRandomPositionOffScreen()
        kamikaze = EnemyKamikaze(creationPosition[0], creationPosition[1])
        self.currentNumberOfKamikazes += 1
        allSpritesGroup.add(kamikaze)
        enemiesGroup.add(kamikaze)
    def createAsteroid(self):
        pass
    def increaseMaxEnemies(self):
        # Aumenta o número máximo de inimigos
        self.maxNumberOfShooters += 1
        self.maxNumberOfKamikazes += 1
        print(f"Max enemies increased: {self.maxNumberOfShooters} shooters, {self.maxNumberOfKamikazes} kamikazes")
    def update(self):
        currentTime = pygame.time.get_ticks()

        if(self.maxNumberOfKamikazes > self.currentNumberOfKamikazes):
            self.createKamikaze()
        if(self.maxNumberOfShooters > self.currentNumberOfShooters):
            self.createShooter()

        if (currentTime - self.lastShooterIncreaseTime) / 1000 >= self.timeForIncreaseMaxShooters:
            self.maxNumberOfShooters += 1
            print(f"Número máximo de shooters aumentado: {self.maxNumberOfShooters}")
            self.lastShooterIncreaseTime = currentTime

        # Verifica se passou tempo suficiente para aumentar o número de kamikazes
        if (currentTime - self.lastKamikazeIncreaseTime) / 1000 >= self.timeForIncreaseMaxKamikazes:
            self.maxNumberOfKamikazes += 1
            print(f"Número máximo de kamikazes aumentado: {self.maxNumberOfKamikazes}")
            self.lastKamikazeIncreaseTime = currentTime

        
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.playerSize = 0.1
        self.playerPosition = pygame.math.Vector2(screenWidth / 2, screenHeight / 2)
        self.image = pygame.transform.rotozoom(pygame.image.load("./Sprites/Nave Nova Girada Para Direita PNG.png").convert_alpha(), 0, self.playerSize)
        self.baseImage = self.image
        self.rect = self.image.get_rect(center=self.playerPosition)
        self.timeOfLastShot = 0
        self.shotCooldown = fps / 3.5
        self.speed = 5

    def userInput(self):
        self.velocityX = 0
        self.velocityY = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocityY -= self.speed
        if keys[pygame.K_s]:
            self.velocityY += self.speed
        if keys[pygame.K_a]:
            self.velocityX -= self.speed
        if keys[pygame.K_d]:
            self.velocityX += self.speed

        if self.velocityY != 0 and self.velocityX != 0:
            self.velocityX /= (2) ** (1/2)
            self.velocityY /= (2) ** (1/2)

        if pygame.mouse.get_pressed() == (1, 0, 0) and self.timeOfLastShot >= self.shotCooldown:
            self.shoot()
            self.timeOfLastShot = 0

    def move(self):
        self.playerPosition += pygame.math.Vector2(self.velocityX, self.velocityY)
        self.rect.center = self.playerPosition

    def playerRotation(self):
        self.mouseCoordinates = pygame.mouse.get_pos()
        self.deltaX = (self.mouseCoordinates[0] - self.rect.centerx)
        self.deltaY = (self.mouseCoordinates[1] - self.rect.centery)
        self.angle = math.degrees(math.atan2(-self.deltaY, self.deltaX))
        self.image = pygame.transform.rotate(self.baseImage, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def getRotatedPoint(self, relativePoint):
        rotatedVector = pygame.math.Vector2(relativePoint).rotate(-self.angle)
        return self.rect.center + rotatedVector

    def shoot(self):
        bulletStartPoint = self.getRotatedPoint((self.image.get_width() / 2, 0))  # Extremidade no meio do lado direito
        bullet = Bullet(bulletStartPoint.x, bulletStartPoint.y, -self.angle)
        bulletsGroup.add(bullet)
        allSpritesGroup.add(bullet)
        playerShotSound.play()

    def update(self):
        self.userInput()
        self.move()
        self.playerRotation()
        pygame.draw.rect(screen, "red", player.rect, width=2)
        self.timeOfLastShot += 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, startPositionX, startPositionY, angle):
        super().__init__()
        self.startPositionX, self.startPositionY, self.angle = startPositionX, startPositionY, angle
        self.x, self.y = self.startPositionX, self.startPositionY
        self.image = pygame.image.load("./Sprites/Bullet.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.03)
        self.transparencyColor = self.image.get_at((0,0))
        self.image.set_colorkey(self.transparencyColor)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.speed = 9
        self.velocityY = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.velocityX = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.lifetime = fps * 3.5 
        self.age = 0

    def move(self):
        self.x += self.velocityX
        self.y += self.velocityY

        self.rect.x, self.rect.y = self.x, self.y
    def getOld(self):
        self.age += 1
        if self.age >= self.lifetime: self.kill()
    def update(self):
        self.move()
        self.getOld()
class EnemyBullet(Bullet):
    def __init__(self, startPositionX, startPositionY, angle):
        super().__init__(startPositionX, startPositionY, angle)
        self.image = pygame.image.load("./Sprites/Enemy Bullet.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.03)
        self.transparencyColor = self.image.get_at((0,0))
        self.image.set_colorkey(self.transparencyColor)
    def die(self):
        self.kill()
  
class EnemyShooter(pygame.sprite.Sprite):
    def __init__(self, startX, startY, shootPoint):
        self.position = pygame.math.Vector2(startX, startY)
        self.shootPoint = shootPoint
        self.distanceToSPToShoot = 100
        self.size = 0.1
        self.image = pygame.transform.rotozoom(pygame.image.load("./Sprites/Nave-Inimiga-Shooter.png").convert_alpha(), 0, self.size)
        self.baseImage = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.speed = 3
        self.vX, self.vY = 0, 0
        self.timeOfLastShot = 0
        super().__init__()
    def rotateToPlayer(self):
        self.playerCoordinates = player.playerPosition
        self.deltaX = (self.playerCoordinates[0] - self.rect.centerx)
        self.deltaY = (self.playerCoordinates[1] - self.rect.centery)
        self.angle = math.degrees(math.atan2(-self.deltaY, self.deltaX))
        self.image = pygame.transform.rotate(self.baseImage, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        pass
    def tryToShoot(self):
        cooldown = int(random.randrange(fps * 1, 5 * fps))
        if self.timeOfLastShot >= cooldown:
            self.shoot()
            self.timeOfLastShot = 0
    def getRotatedPoint(self, relativePoint):
        rotatedVector = pygame.math.Vector2(relativePoint).rotate(-self.angle)
        return self.rect.center + rotatedVector

    def shoot(self):
        bulletStartPoint = self.getRotatedPoint((self.image.get_width() / 2, 0))  # Extremidade no meio do lado direito
        bullet = EnemyBullet(bulletStartPoint.x, bulletStartPoint.y, -self.angle)
        enemiesGroup.add(bullet)
        allSpritesGroup.add(bullet)
        enemyShooterSound.play()

    def moveToShootPoint(self):
        self.deltaXtoSP = (self.shootPoint[0] - self.position[0])
        self.deltaYtoSP = (self.shootPoint[1] - self.position[1])

        angleRadians = math.atan2(self.deltaYtoSP, self.deltaXtoSP)

        self.vX = self.speed * math.cos(angleRadians)
        self.vY = self.speed * math.sin(angleRadians)

        self.position[0] += self.vX 
        self.position[1] += self.vY

        self.rect = self.image.get_rect(center=self.position)
    def die(self):
        enemyGenerator.currentNumberOfShooters -= 1
        self.kill()
    def update(self):
        if int(self.position[0]) != int(self.shootPoint[0]) and  int(self.position[1]) != int(self.shootPoint[1]):
            self.moveToShootPoint()
        pygame.draw.rect(screen, "red", self.rect, width=2)
        self.rotateToPlayer()
        if abs(self.position[0] - self.shootPoint[0]) <= self.distanceToSPToShoot and abs(self.position[1] - self.shootPoint[1]) <= self.distanceToSPToShoot:
            print("C")
            self.tryToShoot()
        self.timeOfLastShot += 1

class EnemyKamikaze(pygame.sprite.Sprite):
    def __init__(self, startX, startY):
        super().__init__()
        self.position = pygame.math.Vector2(startX, startY)
        self.size = 0.15
        self.image = pygame.transform.rotozoom(pygame.image.load("./Sprites/Nave-Inimiga-Kamikaze.png").convert_alpha(), 0, self.size)
        self.baseImage = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.speed = 3

    def rotateAndMoveToPlayer(self):
        self.playerCoordinates = player.playerPosition
        self.deltaX = self.playerCoordinates[0] - self.rect.centerx
        self.deltaY = self.playerCoordinates[1] - self.rect.centery

        # Calcular o ângulo em radianos
        angleRadians = math.atan2(self.deltaY, self.deltaX)

        # Calcular o vetor de movimento
        self.vX = self.speed * math.cos(angleRadians)
        self.vY = self.speed * math.sin(angleRadians)

        # Atualizar a posição
        self.position[0] += self.vX 
        self.position[1] += self.vY

        # Atualizar a rotação
        self.angle = math.degrees(angleRadians)
        self.image = pygame.transform.rotate(self.baseImage, -self.angle)  # Corrigir a rotação
        self.rect = self.image.get_rect(center=self.position)
    def die(self):
        enemyGenerator.currentNumberOfKamikazes -= 1
        print("morri")
        self.kill()
    def update(self):
        self.rotateAndMoveToPlayer()
        pygame.draw.rect(screen, "red", self.rect, width=2)

def writeSomething(fontstyle, fontsize, textContent, color, x, y, screen):
     font = pygame.font.SysFont(f"{fontstyle}", fontsize)
     text = font.render(f"{textContent}", True, color)
     screen.blit(text, [x, y])

def checkIfPlayerGotHit(playerGroup, enemiesGroup):
    collisions = pygame.sprite.groupcollide(enemiesGroup, playerGroup, False, False)
    if collisions: return True
    else: return False

def checkIfEnemiesGotHit(enemiesGroup, bulletsGroup):
    collisions = pygame.sprite.groupcollide(enemiesGroup, bulletsGroup, False, True)
    if collisions: 
        for enemy, bullet in collisions.items():
            enemy.die()

player = Player()
enemyGenerator = EnemyGenerator()
# enemy = EnemyShooter(200,200, (500,500))
allSpritesGroup = pygame.sprite.Group()
playerGroup = pygame.sprite.Group()
playerGroup.add(player)
bulletsGroup = pygame.sprite.Group()
enemiesGroup = pygame.sprite.Group()
# enemiesGroup.add(enemy)
# allSpritesGroup.add(enemy)
allSpritesGroup.add(player)

background = pygame.transform.scale(pygame.image.load("./Sprites/pexels-instawalli-176851.jpg").convert(), (screenWidth, screenHeight))

endTheGame = False
while not endTheGame:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            endTheGame = True

    screen.blit(background, (0,0))
    allSpritesGroup.draw(screen)
    allSpritesGroup.update()
    enemyGenerator.update()
    if checkIfPlayerGotHit(playerGroup, enemiesGroup): endTheGame = True
    checkIfEnemiesGotHit(enemiesGroup, bulletsGroup)
    pygame.display.update()
    clock.tick(fps)

pygame.quit()
