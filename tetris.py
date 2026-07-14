import pygame
import random

# 초기화
pygame.init()

# 상수로 화면 크기 및 격자 크기 정의
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
BLOCK_SIZE = 30  # 격자 한 칸의 크기 (픽셀)
GRID_WIDTH = 10  # 가로 격자 개수
GRID_HEIGHT = 15 # 세로 격자 개수

# 게임판 위치 설정 (화면 중앙 부근)
X_OFFSET = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
Y_OFFSET = SCREEN_HEIGHT - GRID_HEIGHT * BLOCK_SIZE - 20

# 색상 정의 (RGB)
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)

# 테트리미노 블록 색상들
SHAPE_COLORS = [
    (0, 255, 255),   # 하늘색 (I)
    (255, 165, 0),   # 주황색 (L)
    (0, 0, 255),     # 파란색 (J)
    (255, 255, 0),   # 노란색 (O)
    (0, 255, 0),     # 초록색 (S)
    (128, 0, 128),   # 보라색 (T)
    (255, 0, 0)      # 빨간색 (Z)
]

# 테트리미노 블록 모양 패턴 (각 회전 상태 정의)
# 4x4 격자 기준 좌표로 표현
SHAPES = [
    # I 블록
    [[[1, 0], [1, 1], [1, 2], [1, 3]], [[0, 2], [1, 2], [2, 2], [3, 2]]],
    # L 블록
    [[[1, 0], [1, 1], [1, 2], [2, 2]], [[0, 1], [1, 1], [2, 1], [2, 0]], [[0, 0], [1, 0], [1, 1], [1, 2]], [[0, 1], [0, 2], [1, 1], [2, 1]]],
    # J 블록
    [[[1, 0], [1, 1], [1, 2], [2, 0]], [[0, 1], [1, 1], [2, 1], [2, 2]], [[0, 2], [1, 0], [1, 1], [1, 2]], [[0, 0], [0, 1], [1, 1], [2, 1]]],
    # O 블록
    [[[0, 0], [0, 1], [1, 0], [1, 1]]],
    # S 블록
    [[[1, 1], [1, 2], [2, 0], [2, 1]], [[0, 1], [1, 1], [1, 2], [2, 2]]],
    # T 블록
    [[[1, 0], [1, 1], [1, 2], [2, 1]], [[0, 1], [1, 0], [1, 1], [2, 1]], [[0, 1], [1, 0], [1, 1], [1, 2]], [[0, 1], [1, 1], [1, 2], [2, 1]]],
    # Z 블록
    [[[1, 0], [1, 1], [2, 1], [2, 2]], [[0, 2], [1, 1], [1, 2], [2, 1]]]
]


class Piece:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(SHAPES) - 1)
        self.color = SHAPE_COLORS[self.type]
        self.rotation = 0

    @property
    def image(self):
        return SHAPES[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(SHAPES[self.type])


class Tetris:
    def __init__(self):
        self.grid = [[(0, 0, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Piece(GRID_WIDTH // 2 - 1, 0)
        self.game_over = False
        self.score = 0

    # 블록이 충돌하는지 체크 (벽, 바닥, 혹은 기존에 쌓인 블록)
    def check_collision(self, piece, offset_x=0, offset_y=0):
        for r, c in piece.image:
            target_x = piece.x + c + offset_x
            target_y = piece.y + r + offset_y
            
            # 경계선 체크
            if target_x < 0 or target_x >= GRID_WIDTH or target_y >= GRID_HEIGHT:
                return True
            # 쌓여있는 블록과의 충돌 체크 (화면 위는 예외)
            if target_y >= 0 and self.grid[target_y][target_x] != (0, 0, 0):
                return True
        return False

    # 블록을 고정시키고 줄이 꽉 찼는지 확인
    def lock_piece(self):
        for r, c in self.current_piece.image:
            target_y = self.current_piece.y + r
            target_x = self.current_piece.x + c
            if target_y >= 0:
                self.grid[target_y][target_x] = self.current_piece.color
        
        self.clear_lines()
        
        # 새로운 블록 생성
        self.current_piece = Piece(GRID_WIDTH // 2 - 1, 0)
        
        # 새 블록이 나오자마자 충돌하면 게임 오버
        if self.check_collision(self.current_piece):
            self.game_over = True

    # 가득 찬 줄 제거 및 점수 획득
    def clear_lines(self):
        lines_to_clear = []
        for r in range(GRID_HEIGHT):
            if all(self.grid[r][c] != (0, 0, 0) for c in range(GRID_WIDTH)):
                lines_to_clear.append(r)
        
        for r in lines_to_clear:
            del self.grid[r]
            # 맨 위에 빈 줄 추가
            self.grid.insert(0, [(0, 0, 0) for _ in range(GRID_WIDTH)])
            self.score += 100

    # 한 칸 아래로 떨어뜨리기
    def drop(self):
        if not self.check_collision(self.current_piece, offset_y=1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

    # 스페이스바: 즉시 하강 (Hard Drop)
    def hard_drop(self):
        while not self.check_collision(self.current_piece, offset_y=1):
            self.current_piece.y += 1
        self.lock_piece()

    # 좌우 이동
    def move(self, dx):
        if not self.check_collision(self.current_piece, offset_x=dx):
            self.current_piece.x += dx

    # 회전 시도 (벽에 부딪히면 회전 불가하도록 방지)
    def rotate_piece(self):
        old_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        if self.check_collision(self.current_piece):
            self.current_piece.rotation = old_rotation  # 충돌 시 원래대로 롤백


def draw_grid(screen, grid):
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            rect = pygame.Rect(X_OFFSET + c * BLOCK_SIZE, Y_OFFSET + r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            if grid[r][c] != (0, 0, 0):
                pygame.draw.rect(screen, grid[r][c], rect)
                pygame.draw.rect(screen, GRAY, rect, 1)  # 블록 테두리
            else:
                # 배경 빈 격자선 그리기
                pygame.draw.rect(screen, GRAY, rect, 1)


def draw_piece(screen, piece):
    for r, c in piece.image:
        target_y = piece.y + r
        target_x = piece.x + c
        if target_y >= 0:
            rect = pygame.Rect(X_OFFSET + target_x * BLOCK_SIZE, Y_OFFSET + target_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, piece.color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)  # 움직이는 블록 테두리


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("테트리스 (Tetris)")
    clock = pygame.time.Clock()
    game = Tetris()
    
    # 떨어지는 속도 조절 타이머 (밀리초 단위)
    fall_time = 0
    fall_speed = 500  # 0.5초마다 한 칸씩 하강

    running = True
    while running:
        screen.fill(BLACK)
        dt = clock.tick(60)  # 60 FPS 기준 프레임 타이머
        fall_time += dt

        # 자동 하강 로직
        if fall_time >= fall_speed:
            if not game.game_over:
                game.drop()
            fall_time = 0

        # 키보드 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    # 게임 오버 상태에서 아무 키나 누르면 재시작
                    game = Tetris()
                else:
                    if event.key == pygame.K_LEFT:
                        game.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1)
                    elif event.key == pygame.K_DOWN:
                        game.drop()
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

        # 화면 그리기
        draw_grid(screen, game.grid)
        if not game.game_over:
            draw_piece(screen, game.current_piece)

        # 점수 및 게임 상태 텍스트 표시
        font = pygame.font.SysFont("malgungothic", 24)  # 윈도우 한글 폰트 기준
        score_text = font.render(f"SCORE: {game.score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        if game.game_over:
            over_text = font.render("GAME OVER - Press Any Key", True, (255, 0, 0))
            screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()