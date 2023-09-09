import pygame
from math import *
import os
import time

os.chdir("der")

#게임 세팅
pygame.init()

#풀스크린 사이즈 미리 불러오기
fullscreen_width = pygame.display.Info().current_w
fullscreen_height = pygame.display.Info().current_h

debugMode = True

if debugMode:
    screen = pygame.display.set_mode((1200, 600))
else:
    screen = pygame.display.set_mode((1000, 1000))

pygame.display.set_caption("레이케스터 데모")

def convert1bit(image_path, threshold=128):
    # 이미지 로드
    image = pygame.image.load(image_path)

    wid, hei = image.get_size()

    alpaMap = [[0 for x in range(wid)] for y in range(hei)]

    # 알파 값을 기준으로 1비트로 변환
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            r, g, b, a = image.get_at((x, y))
            if a > threshold:
                image.set_at((x, y), pygame.Color(255, 255, 255, 255))
                alpaMap[y][x] = 1
            else:
                image.set_at((x, y), pygame.Color(0, 0, 0, 255))
                alpaMap[y][x] = 0

    return image, alpaMap  # 변환된 이미지 반환

def screenPos(pos, y_middle):
    return((pos[0], -(pos[1] -y_middle) +y_middle))

def clamp(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value

def screenText(content, font):
    screen.fill((255, 0, 0))
    wait = True

    text = font.render(content, True, (255, 255, 255))
    screen.blit(text, (screen.get_width()/2 - text.get_width()/2, screen.get_height()/2 - text.get_height()/2))
    pygame.display.update()
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                wait = False

screen.fill((255, 0, 0))

run = True

#상수 선언
RADIAN1 = 0.0174533

#게임 시스템 변수들
clk = pygame.time.Clock()
mouseShow = False

key_toggle = {
    "f11": False,
    "z": False,
    "t": False,

    "w": False,
    "s": False,
    "a": False,
    "d": False
}
trans_screen = False
fullscreen = False

#서페이스 옵션들
mainMapImg, mainMap = convert1bit("맵.png")
curser = pygame.transform.scale(pygame.image.load("커서.png"), (50, 50))
mainTexture = pygame.image.load("텍스쳐들/t.png")
debugScreen = pygame.Surface((600, 600))
inGameScreen = pygame.Surface((600, 600), pygame.SRCALPHA)

# 폰트
font = pygame.font.Font("8bitOperatorPlus-Bold.ttf", 20)

#위치 옵션들
beforePos = []
playerPos = [300, 300]
playerNowSpeed = [0, 0]
playerSpeed = 1

#각도 옵션들
playerAngle = 0
playerAngleSpeed = 0
playerAngleSen = 0.5

#렌더 옵션들
viewRadius = RADIAN1 * 100
renderAngleOffset = RADIAN1 * 0.5
randerHeight = [0 for i in range(int(viewRadius/renderAngleOffset))]
randerDis = [0 for i in range(int(viewRadius/renderAngleOffset))]
randerPosValue = [[0, 0] for i in range(int(viewRadius/renderAngleOffset))]
maxRanderLine = 200
randerLineOffset = 1

#기타 플레이어 옵션들
playerSize = 1
playerContect = False

#기타 화면 옵션들
maxHeight = 2000
print(mainMap)

#마우스 스크롤 측정
mouseScrollMod = 0
mousePos1 = (0, 0)
mousePos2 = (0, 0)

#시간 옵션
timer = time.time()
time1 = time.time() + 2
screen.fill((255, 0, 0))



if not debugMode:
    screenText("W, A, S, D 로 조종 | 벽에 접촉하는 행위는 권장하지 않습니다. (클릭)", font)
    screenText("인게임중 ESC 키를 눌러 커서를 표시할수 있습니다. (클릭)", font)
    screenText("ESC키를 다시 누르면 커서가 숨겨집니다. (클릭)", font)
    screenText("화면 우측 하단을 드래그하여 화면 크기를 조정할수 있습니다. (클릭)", font)
    screenText("F11 키로 전체화면을 할수 있습니다. (클릭)", font)
    screenText("아무일도 없습니다, 걱정하지 마세요. 기대하지 마세요. (클릭)", font)
    screenText("그리고 나좀 그냥 나둬 이 버그 메이커들아. (클릭)", font)

while run:
    clk.tick(30) #프레임 설정
    fps = clk.get_fps() #fps 구하기 ㅋㅋㄹㅃㅃ

    for event in pygame.event.get():

        mouse_pos = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0] and screen.get_width() - 10 < mouse_pos[0] and screen.get_height() - 10 < mouse_pos[1]:
            trans_screen = True
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_screen_width, new_screen_height = mouse_x, mouse_y
            screen = pygame.display.set_mode((clamp(new_screen_width, 200, 5000), clamp(new_screen_height, 200, 5000)))

        elif trans_screen and pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_screen_width, new_screen_height = mouse_x, mouse_y
            screen = pygame.display.set_mode((clamp(new_screen_width, 200, 5000), clamp(new_screen_height, 200, 5000)))

        elif trans_screen and not pygame.mouse.get_pressed()[0]:
            trans_screen = not trans_screen

        keyp = pygame.key.get_pressed()
        
        if keyp[pygame.K_F11] and not key_toggle["f11"]:
            key_toggle["f11"] = True

            if fullscreen:
                fullscreen = False
                screen = pygame.display.set_mode((1000, 1000))
            
            else:
                fullscreen = True
                screen = pygame.display.set_mode((fullscreen_width, fullscreen_height), pygame.FULLSCREEN)

        elif not keyp[pygame.K_F11] and key_toggle["f11"]: key_toggle["f11"] = False
        
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: playerNowSpeed[1] += playerSpeed
            if event.key == pygame.K_s: playerNowSpeed[1] -= playerSpeed
            if event.key == pygame.K_d: playerNowSpeed[0] += playerSpeed
            if event.key == pygame.K_a: playerNowSpeed[0] -= playerSpeed
            if event.key == pygame.K_ESCAPE:
                mouseShow = not mouseShow

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w: playerNowSpeed[1] += -playerSpeed
            if event.key == pygame.K_s: playerNowSpeed[1] -= -playerSpeed
            if event.key == pygame.K_d: playerNowSpeed[0] += -playerSpeed
            if event.key == pygame.K_a: playerNowSpeed[0] -= -playerSpeed

    inGameScreen.fill((0, 0, 0))

    if not mouseShow:
        if mouseScrollMod == 0:
            mousePos1 = pygame.mouse.get_pos()[0]
            mouseScrollMod = 1
        elif mouseScrollMod == 1:
            mousePos2 = pygame.mouse.get_pos()[0]
            playerAngleSpeed = RADIAN1 * (mousePos1 - mousePos2) * playerAngleSen
            pygame.mouse.set_pos((300, 300))
            mouseScrollMod = 0

    else:
        inGameScreen.blit(curser, (20, 20))
        playerAngleSpeed = 0

    pygame.mouse.set_visible(mouseShow)

    playerHit = [
        mainMap[len(mainMap) - (int(playerPos[1]) +playerSize)] [int(playerPos[0])],
        mainMap[len(mainMap) - (int(playerPos[1]) -playerSize)] [int(playerPos[0])],
        mainMap[len(mainMap) - (int(playerPos[1]))]             [int(playerPos[0]) +playerSize],
        mainMap[len(mainMap) - (int(playerPos[1]))]             [int(playerPos[0]) -playerSize]
    ]

    if 1 in playerHit:
        if playerHit[0] != 0: 
            playerPos[1] -= playerSpeed
        elif playerHit[1] != 0: 
            playerPos[1] += playerSpeed
        elif playerHit[2] != 0: 
            playerPos[0] -= playerSpeed
        elif playerHit[3] != 0: 
            playerPos[0] += playerSpeed
    
    moveAngle = atan2(playerNowSpeed[1], playerNowSpeed[0])
    moveDis = (playerNowSpeed[0]**2 + playerNowSpeed[1]**2) **0.5
    moveAngle += playerAngle - RADIAN1 * 90

    playerPos[0] += cos(moveAngle) * moveDis 
    playerPos[1] += sin(moveAngle) * moveDis

    beforePos = playerPos.copy() 

    playerAngle += playerAngleSpeed

    randerPos = screenPos(playerPos, 300)

    playerAnglePos = (
        playerPos[0] + cos(playerAngle)*10, 
        -((playerPos[1] + sin(playerAngle)*10) -300) +300)
    
    if debugMode:
        debugScreen.blit(mainMapImg, (0, 0))
        pygame.draw.circle(debugScreen, (0, 255, 255), screenPos(playerPos, 300), 4)
        pygame.draw.line(debugScreen, (255, 0, 0), randerPos, playerAnglePos, 3)

    for i in range(int(viewRadius / renderAngleOffset)):
        nowRanderAngle = (viewRadius*-0.5 + i*renderAngleOffset) +playerAngle
        nowRanderSelf = viewRadius*-0.5 + i*renderAngleOffset

        lineRander = True
        lineDis = 0
        
        while lineRander:
            lineDis += randerLineOffset

            editedDis = cos(nowRanderSelf) * lineDis # 매인 거리 연산부

            disPos = ( # 맵이미지 위치 인덱스 변수
                int(playerPos[0] + cos(nowRanderAngle) *lineDis), 
                int(playerPos[1] + sin(nowRanderAngle) *lineDis))
            
            editedDisPos = (
                int(playerPos[0] + cos(nowRanderAngle) *editedDis), 
                int(playerPos[1] + sin(nowRanderAngle) *editedDis))
            
            if mainMap[int(disPos[1] * -1)][int(disPos[0])] == 1:
                randerHeight[i] = editedDis
                randerDis[i] = lineDis
                randerPosValue[i] = disPos
                lineRander = False
                
                if debugMode:
                    pygame.draw.line(debugScreen, (255, 0, 0), screenPos(disPos, 300), screenPos(playerPos, 300))
                    pygame.draw.line(debugScreen, (255, 255, 0), screenPos(editedDisPos, 300), screenPos(playerPos, 300))

            elif lineDis >= maxRanderLine:
                randerHeight[i] = editedDis
                randerDis[i] = maxRanderLine
                randerPosValue[i] = disPos
                lineRander = False

                if debugMode:
                    pygame.draw.line(debugScreen, (0, 255, 0), screenPos(disPos, 300), screenPos(playerPos, 300))
                    pygame.draw.line(debugScreen, (255, 255, 0), screenPos(editedDisPos, 300), screenPos(playerPos, 300))

    for i in range(len(randerHeight)):
        x = 600 - (i * 600 / (viewRadius / renderAngleOffset))
        y = 6000 / randerHeight[i]
        
        light = 255 - (randerDis[i] * (255 / maxRanderLine)) if randerDis[i] > 0 else 255

        if 0 > light:
            light = 0

        textruePos = (randerPosValue[i][0] + randerPosValue[i][1]) % 16

        subTextureRect = pygame.Rect(textruePos, 0, 1, mainTexture.get_height())
        subTexture = mainTexture.subsurface(subTextureRect)

        subTexture = pygame.transform.scale(subTexture, (ceil(600 / (viewRadius / renderAngleOffset)), y)).convert_alpha()
        subTexture.fill((light, light, light), special_flags=pygame.BLEND_RGBA_MULT)

        inGameScreen.blit(subTexture, (x, 300 - y / 2))
        # pygame.draw.rect(inGameScreen, (255, 0, 0, 128), (x, 300 - y / 2, ceil(600 / (viewRadius / renderAngleOffset)), y))

    screen.fill((0, 0, 0))

    if debugMode:
        screen.blit(debugScreen, (0, 0))
        screen.blit(inGameScreen, (600, 0))
    else:
        ingame_screen_size = screen.get_width() if screen.get_width() < screen.get_height() else screen.get_height()

        if screen.get_width() > screen.get_height():
            ingame_screen_pos = (screen.get_width() / 2 - ingame_screen_size / 2, 0)

        else: ingame_screen_pos = (0, screen.get_height() / 2 - ingame_screen_size / 2)

        screen.blit(pygame.transform.scale(inGameScreen, (ingame_screen_size, ingame_screen_size)), ingame_screen_pos)
    
    pygame.display.update()