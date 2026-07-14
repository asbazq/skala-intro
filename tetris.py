import pygame
import random

# 초기화
pygame.init()

# 상수로 화면 크기 및 격자 크기 정의
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
BLOCK_SIZE = 30  # 격자 한 칸의 크기 (픽셀)
GRID_WIDTH = 10  # 가로 격자 개수
GRID_HEIGHT = 15 # 세로 격자 개수

# 게임판 위치 설정 (화면 오른쪽 영역으로 배치)
X_OFFSET = 170
Y_OFFSET = SCREEN_HEIGHT - GRID_HEIGHT * BLOCK_SIZE - 20

# 색상 정의 (RGB)
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
YELLOW = (255, 215, 0)  # 점수 강조용 노란색

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

# 테트리미노 블록 모양 패턴
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
        self.next_piece = Piece(GRID_WIDTH // 2 - 1, 0)
        self.game_over = False
        self.score = 0

    def check_collision(self, piece, offset_x=0, offset_y=0):
        for r, c in piece.image:
            target_x = piece.x + c + offset_x
            target_y = piece.y + r + offset_y
            
            if target_x < 0 or target_x >= GRID_WIDTH or target_y >= GRID_HEIGHT:
                return True
            if target_y >= 0 and self.grid[target_y][target_x] != (0, 0, 0):
                return True
        return False

    def lock_piece(self):
        for r, c in self.current_piece.image:
            target_y = self.current_piece.y + r
            target_x = self.current_piece.x + c
            if target_y >= 0:
                self.grid[target_y][target_x] = self.current_piece.color
        
        self.clear_lines()
        
        self.current_piece = self.next_piece
        self.next_piece = Piece(GRID_WIDTH // 2 - 1, 0)
        
        if self.check_collision(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for r in range(GRID_HEIGHT):
            if all(self.grid[r][c] != (0, 0, 0) for c in range(GRID_WIDTH)):
                lines_to_clear.append(r)
        
        for r in lines_to_clear:
            del self.grid[r]
            self.grid.insert(0, [(0, 0, 0) for _ in range(GRID_WIDTH)])
            self.score += 100

    def drop(self):
        if not self.check_collision(self.current_piece, offset_y=1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

    def hard_drop(self):
        while not self.check_collision(self.current_piece, offset_y=1):
            self.current_piece.y += 1
        self.lock_piece()

    def move(self, dx):
        if not self.check_collision(self.current_piece, offset_x=dx):
            self.current_piece.x += dx

    def rotate_piece(self):
        old_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        if self.check_collision(self.current_piece):
            self.current_piece.rotation = old_rotation


def draw_grid(screen, grid):
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            rect = pygame.Rect(X_OFFSET + c * BLOCK_SIZE, Y_OFFSET + r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            if grid[r][c] != (0, 0, 0):
                pygame.draw.rect(screen, grid[r][c], rect)
                pygame.draw.rect(screen, GRAY, rect, 1)
            else:
                pygame.draw.rect(screen, GRAY, rect, 1)


def draw_piece(screen, piece):
    for r, c in piece.image:
        target_y = piece.y + r
        target_x = piece.x + c
        if target_y >= 0:
            rect = pygame.Rect(X_OFFSET + target_x * BLOCK_SIZE, Y_OFFSET + target_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, piece.color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)


def draw_preview(screen, piece, font):
    next_label = font.render("NEXT", True, WHITE)
    screen.blit(next_label, (25, 120))
    
    preview_box = pygame.Rect(20, 150, 120, 120)
    pygame.draw.rect(screen, GRAY, preview_box, 2)
    
    offset_x = 30 if piece.type in [0, 3] else 40
    offset_y = 165 if piece.type == 0 else 180

    for r, c in piece.image:
        rect = pygame.Rect(
            20 + c * 25 + offset_x,
            offset_y + r * 25, 
            25, 25
        )
        pygame.draw.rect(screen, piece.color, rect)
        pygame.draw.rect(screen, WHITE, rect, 1)


# 우측 상단에 점수판을 그리는 함수 추가
def draw_score(screen, score, font):
    # 점수판 상자 영역 (화면 우측 상단 X: 350~470 영역)
    score_box = pygame.Rect(355, 30, 120, 75)
    pygame.draw.rect(screen, GRAY, score_box, 2)  # 테두리 상자 그리기
    
    # "SCORE" 텍스트 (상자 안 위쪽 중앙 정렬)
    score_label = font.render("SCORE", True, WHITE)
    screen.blit(score_label, (score_box.centerx - score_label.get_width() // 2, 40))
    
    # 실제 점수 수치 (상자 안 아래쪽 중앙 정렬 및 노란색 강조)
    score_val = font.render(f"{score}", True, YELLOW)
    screen.blit(score_val, (score_box.centerx - score_val.get_width() // 2, 68))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("테트리스 (Tetris)")
    clock = pygame.time.Clock()
    game = Tetris()
    
    fall_time = 0
    fall_speed = 500

    running = True
    while running:
        screen.fill(BLACK)
        dt = clock.tick(60)
        fall_time += dt

        if fall_time >= fall_speed:
            if not game.game_over:
                game.drop()
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game.game_over:
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

        font = pygame.font.SysFont("malgungothic", 20)
        
        # 1. 게임 메인 판 그리기
        draw_grid(screen, game.grid)
        
        # 2. 현재 조작중인 블록 그리기
        if not game.game_over:
            draw_piece(screen, game.current_piece)

        # 3. 왼쪽 상단 다음 블록 미리보기 그리기
        draw_preview(screen, game.next_piece, font)

        # 4. 오른쪽 상단에 점수판 그리기 (신규 추가)
        draw_score(screen, game.score, font)

        # 게임 오버 메시지
        if game.game_over:
            over_text = font.render("GAME OVER", True, (255, 0, 0))
            restart_text = font.render("Press Any Key", True, WHITE)
            screen.blit(over_text, (X_OFFSET + 35, SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (X_OFFSET + 30, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()