import pygame
import sys
from enum import Enum
import random
from typing import Optional, List, Tuple

# Import AI module
from AI_Player import Player, Difficulty, AIFactory, BaseAI

# Constants
WINDOW_SIZE = 800
BOARD_HEIGHT = 630
UI_HEIGHT = 120
TOTAL_HEIGHT = 750
DEFAULT_GRID_SIZE = 15
CELL_SIZE = BOARD_HEIGHT // DEFAULT_GRID_SIZE
radius = CELL_SIZE // 3
WIN_LENGTH = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
DARK_GRAY = (100, 100, 100)
PURPLE = (128, 0, 128)
GREEN = (105, 227, 23)


class GameMode(Enum):
    PK_MODE = 1
    AI_MODE = 2


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    CONFIRM_EXIT = 4


class GomokuGame:
    def __init__(self, grid_size: int = DEFAULT_GRID_SIZE, ai_difficulty: Difficulty = Difficulty.MEDIUM):
        self.grid_size = grid_size
        self.board: List[List[Player]] = [[Player.EMPTY for _ in range(
            self.grid_size)] for _ in range(self.grid_size)]
        self.current_player: Player = Player.X
        self.ai_player: Player = Player.X
        self.ai_difficulty: Difficulty = ai_difficulty
        self.ai_instance: Optional[BaseAI] = None
        self.game_over: bool = False
        self.winner: Optional[Player] = None
        self.winning_line: List[Tuple[int, int]] = []
        self.win_found: bool = False

    def make_move(self, row: int, col: int) -> bool:
        """Place a move at the given position. Returns True if move was valid."""
        if self.board[row][col] == Player.EMPTY and not self.game_over and not self.win_found:
            self.board[row][col] = self.current_player

            # Check for winner
            if self.check_winner(row, col):
                self.win_found = True
                self.winner = self.current_player
            elif self.is_board_full():
                # Check for tie
                self.game_over = True
                self.winner = None  # None indicates a tie
            else:
                # Switch player
                self.current_player = Player.O if self.current_player == Player.X else Player.X
            return True
        return False

    def check_winner(self, row: int, col: int) -> bool:
        """Check if the last move at (row, col) resulted in a win."""
        player = self.board[row][col]

        # Check horizontal
        if self._check_line(row, col, 0, 1, player):
            return True

        # Check vertical
        if self._check_line(row, col, 1, 0, player):
            return True

        # Check diagonal (top-left to bottom-right)
        if self._check_line(row, col, 1, 1, player):
            return True

        # Check diagonal (top-right to bottom-left)
        if self._check_line(row, col, 1, -1, player):
            return True

        return False

    @staticmethod
    def count_line(board: List[List[Player]], row: int, col: int,
                   delta_row: int, delta_col: int, player: Player) -> Tuple[int, List[Tuple[int, int]]]:
        grid_size = len(board)
        count = 1
        line_cells = [(row, col)]

        # Check in positive direction
        r, c = row + delta_row, col + delta_col
        while 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == player:
            count += 1
            line_cells.append((r, c))
            r += delta_row
            c += delta_col

        # Check in negative direction
        r, c = row - delta_row, col - delta_col
        while 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == player:
            count += 1
            line_cells.append((r, c))
            r -= delta_row
            c -= delta_col

        return count, line_cells

    def _check_line(self, row: int, col: int, delta_row: int, delta_col: int, player: Player) -> bool:
        """Check if there's a line of WIN_LENGTH in the given direction."""
        board = self.board
        res = self.count_line(board, row, col, delta_row, delta_col, player)
        count = res[0]
        line_cells = res[1]

        if count >= WIN_LENGTH:
            self.winning_line = line_cells[:WIN_LENGTH]
            return True

        return False

    def is_board_full(self) -> bool:
        """Check if all cells on the board are occupied."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.board[row][col] == Player.EMPTY:
                    return False
        return True

    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.board = [[Player.EMPTY for _ in range(
            self.grid_size)] for _ in range(self.grid_size)]
        self.current_player = Player.X
        self.game_over = False
        self.winner = None
        self.winning_line = []
        self.win_found = False

    def get_position_from_mouse(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Convert mouse coordinates to board position."""
        board_left = (WINDOW_SIZE - self.grid_size * CELL_SIZE) // 2
        board_top = 70
        board_height = self.grid_size * CELL_SIZE

        if x < board_left or x > board_left + self.grid_size * CELL_SIZE or y < board_top or y > board_top + board_height:
            return None

        col = (x - board_left) // CELL_SIZE
        row = (y - board_top) // CELL_SIZE

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return row, col
        return None


class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, TOTAL_HEIGHT))
        pygame.display.set_caption("Gomoku Game - Advanced AI")
        self.clock = pygame.time.Clock()

        # Font size
        self.font_title = pygame.font.Font(None, size=100)
        self.font_large = pygame.font.Font(None, size=60)
        self.font_medium = pygame.font.Font(None, size=40)
        self.font_small = pygame.font.Font(None, size=30)

        # Initialize
        self.grid_size = DEFAULT_GRID_SIZE
        self.current_difficulty = Difficulty.MEDIUM
        self.game = GomokuGame(self.grid_size, self.current_difficulty)
        self.game_state = GameState.MENU
        self.win_highlight_start_time: Optional[int] = None
        self.game_mode: Optional[GameMode] = None
        self.next_ai_move_time: Optional[int] = None
        self.ai_mode_selection_active: bool = False

        # Update global variables
        self.update_grid_dependent_vars()

        # Create UI elements
        self.create_ui_elements()
        self.create_difficulty_buttons()

    def update_grid_dependent_vars(self):
        """Update variables that depend on grid_size."""
        global CELL_SIZE, radius
        CELL_SIZE = BOARD_HEIGHT // self.grid_size
        radius = CELL_SIZE // 3

    def create_ui_elements(self):
        """Create all UI button rectangles."""
        # Menu buttons
        self.ai_mode_button_rect = pygame.Rect(
            WINDOW_SIZE // 2 - 160, TOTAL_HEIGHT // 2 + 50, 140, 60)
        self.pk_mode_button_rect = pygame.Rect(
            WINDOW_SIZE // 2 + 20, TOTAL_HEIGHT // 2 + 50, 140, 60)

        # Game over buttons
        self.restart_button_rect = pygame.Rect(
            WINDOW_SIZE // 2 - 100, 400, 200, 50)
        self.exit_button_rect = pygame.Rect(
            WINDOW_SIZE // 2 - 100, 470, 200, 50)

        # Exit button for playing state
        self.playing_exit_button_rect = pygame.Rect(
            WINDOW_SIZE - 120, 10, 100, 40)

        # Confirm exit buttons
        self.confirm_exit_button_rect = pygame.Rect(
            WINDOW_SIZE // 2 - 160, TOTAL_HEIGHT // 2 + 20, 120, 50)
        self.cancel_exit_button_rect = pygame.Rect(
            WINDOW_SIZE // 2 + 40, TOTAL_HEIGHT // 2 + 20, 120, 50)

        # Input box for grid size
        self.input_box_rect = pygame.Rect(
            WINDOW_SIZE // 2 - 50, TOTAL_HEIGHT // 2 - 50, 100, 40)
        self.input_text = str(self.grid_size)
        self.input_active = False
        self.invalid_message = ""

    def create_difficulty_buttons(self):
        """Create buttons for AI difficulty selection."""
        difficulties = AIFactory.get_available_difficulties()
        button_width = 130
        button_height = 40
        total_width = len(difficulties) * button_width + \
            (len(difficulties) - 1) * 10
        start_x = WINDOW_SIZE // 2 - total_width // 2

        self.difficulty_buttons = []
        for i, (difficulty, description) in enumerate(difficulties):
            button_rect = pygame.Rect(
                start_x + i * (button_width + 10),
                TOTAL_HEIGHT // 2 + 120,
                button_width,
                button_height
            )
            self.difficulty_buttons.append({
                'rect': button_rect,
                'difficulty': difficulty,
                'description': description,
                'selected': difficulty == self.current_difficulty
            })

    def draw_menu(self):
        """Draw the main menu screen with mode selection."""
        self.screen.fill(WHITE)

        # Draw title
        title_surface = self.font_title.render("Gomoku Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(WINDOW_SIZE // 2, 120))
        self.screen.blit(title_surface, title_rect)

        # Draw subtitle
        subtitle_surface = self.font_small.render(
            "Connect 5 to Win", True, GRAY)
        subtitle_rect = subtitle_surface.get_rect(
            center=(WINDOW_SIZE // 2, 200))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # Draw grid size label
        label_surface = self.font_small.render(
            "Grid Size (8-21):", True, BLACK)
        label_rect = label_surface.get_rect(
            center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 - 100))
        self.screen.blit(label_surface, label_rect)

        # Draw input box
        pygame.draw.rect(
            self.screen, LIGHT_GRAY if self.input_active else GRAY, self.input_box_rect)
        pygame.draw.rect(self.screen, BLACK, self.input_box_rect, 2)
        text_surface = self.font_medium.render(self.input_text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.input_box_rect.center)
        self.screen.blit(text_surface, text_rect)

        # Draw blinking cursor if active
        if self.input_active:
            text_width = text_surface.get_width()
            cursor_x = self.input_box_rect.centerx + text_width // 2 + 2
            cursor_y = self.input_box_rect.centery
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.line(self.screen, BLACK, (cursor_x,
                                 cursor_y - 10), (cursor_x, cursor_y + 10), 2)

        # Draw invalid message if any
        if self.invalid_message:
            error_surface = self.font_small.render(
                self.invalid_message, True, RED)
            error_rect = error_surface.get_rect(
                center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 - 70))
            self.screen.blit(error_surface, error_rect)

        if self.ai_mode_selection_active:
            # Draw AI selection screen
            pygame.draw.rect(self.screen, PURPLE, self.ai_mode_button_rect)
            pygame.draw.rect(self.screen, BLACK, self.ai_mode_button_rect, 3)
            ai_text = self.font_medium.render("AI Mode", True, WHITE)
            ai_text_rect = ai_text.get_rect(center=self.ai_mode_button_rect.center)
            self.screen.blit(ai_text, ai_text_rect)

            diff_label = self.font_small.render("Select AI Difficulty:", True, BLACK)
            diff_label_rect = diff_label.get_rect(
                center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 + 20))
            self.screen.blit(diff_label, diff_label_rect)

            for button in self.difficulty_buttons:
                color = GREEN if button['selected'] else GRAY
                pygame.draw.rect(self.screen, color, button['rect'])
                pygame.draw.rect(self.screen, BLACK, button['rect'], 2)

                text = self.font_small.render(
                    button['difficulty'].value.upper(), True, BLACK)
                text_rect = text.get_rect(center=button['rect'].center)
                self.screen.blit(text, text_rect)

            pygame.draw.rect(self.screen, BLUE, self.pk_mode_button_rect)
            pygame.draw.rect(self.screen, BLACK, self.pk_mode_button_rect, 3)
            back_text = self.font_medium.render("Back", True, WHITE)
            back_text_rect = back_text.get_rect(
                center=self.pk_mode_button_rect.center)
            self.screen.blit(back_text, back_text_rect)

            inst_surface = self.font_small.render(
                "Pick a difficulty to start", True, DARK_GRAY)
            inst_rect = inst_surface.get_rect(
                center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 + 200))
            self.screen.blit(inst_surface, inst_rect)
        else:
            # Draw AI Mode button
            pygame.draw.rect(self.screen, PURPLE, self.ai_mode_button_rect)
            pygame.draw.rect(self.screen, BLACK, self.ai_mode_button_rect, 3)
            ai_text = self.font_medium.render("AI Mode", True, WHITE)
            ai_text_rect = ai_text.get_rect(center=self.ai_mode_button_rect.center)
            self.screen.blit(ai_text, ai_text_rect)

            # Draw AI Mode description
            ai_desc_surface = self.font_small.render(
                "vs Computer", True, DARK_GRAY)
            ai_desc_rect = ai_desc_surface.get_rect(center=(self.ai_mode_button_rect.centerx,
                                                            self.ai_mode_button_rect.bottom + 15))
            self.screen.blit(ai_desc_surface, ai_desc_rect)

            # Draw PK Mode button
            pygame.draw.rect(self.screen, BLUE, self.pk_mode_button_rect)
            pygame.draw.rect(self.screen, BLACK, self.pk_mode_button_rect, 3)
            pk_text = self.font_medium.render("PK Mode", True, WHITE)
            pk_text_rect = pk_text.get_rect(center=self.pk_mode_button_rect.center)
            self.screen.blit(pk_text, pk_text_rect)

            # Draw PK Mode description
            pk_desc_surface = self.font_small.render(
                "2 Players Local", True, DARK_GRAY)
            pk_desc_rect = pk_desc_surface.get_rect(center=(self.pk_mode_button_rect.centerx,
                                                            self.pk_mode_button_rect.bottom + 15))
            self.screen.blit(pk_desc_surface, pk_desc_rect)

            # Draw instructions
            inst_surface = self.font_small.render(
                "Select game mode to begin", True, DARK_GRAY)
            inst_rect = inst_surface.get_rect(
                center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 + 200))
            self.screen.blit(inst_surface, inst_rect)

    def start_ai_mode(self):
        """Start AI mode with selected difficulty."""
        self.ai_mode_selection_active = False
        self.game_mode = GameMode.AI_MODE
        self.game = GomokuGame(self.grid_size, self.current_difficulty)

        # Randomly decide who goes first
        ai_first = random.choice([True, False])

        if ai_first:
            # AI goes first as X
            self.game.ai_player = Player.X
            self.game.ai_instance = AIFactory.create_ai(
                self.current_difficulty, Player.X)
            self.game.current_player = Player.X  # AI's turn
            self.ai_order_text = f"Order: AI ({self.current_difficulty.value}) (X) -> You (O)"
            self.next_ai_move_time = max(pygame.time.get_ticks(), 600)
            print(f"AI ({self.current_difficulty.value}) goes first (X)")
        else:
            # Human goes first as X, AI is O
            self.game.ai_player = Player.O
            self.game.ai_instance = AIFactory.create_ai(
                self.current_difficulty, Player.O)
            self.game.current_player = Player.X  # Human's turn
            self.ai_order_text = f"Order: You (X) -> AI ({self.current_difficulty.value}) (O)"
            self.next_ai_move_time = None
            print(
                f"Human goes first (X), AI ({self.current_difficulty.value}) is O")

        self.game_state = GameState.PLAYING

    def start_pk_mode(self):
        """Start PK mode (Human vs Human)."""
        self.game_mode = GameMode.PK_MODE
        self.game = GomokuGame(self.grid_size, self.current_difficulty)
        self.game.ai_player = Player.EMPTY
        self.game.ai_instance = None
        self.game.current_player = Player.X  # X goes first
        self.game_state = GameState.PLAYING
        self.ai_order_text = ""
        self.next_ai_move_time = None

    def transition_to_game_over(self):
        """Set state to GAME_OVER when transition conditions are met."""
        self.game.game_over = True
        self.game_state = GameState.GAME_OVER

    def draw_game_over(self):
        """Draw the game over screen with result and buttons."""
        self.screen.fill(WHITE)

        # Draw outer box border
        box_x = 50
        box_y = 80
        box_width = WINDOW_SIZE - 100
        box_height = 580
        pygame.draw.rect(self.screen, BLACK,
                         (box_x, box_y, box_width, box_height), 3)

        # Draw result text
        if self.game.winner is None:
            result_text = "IT'S A TIE!"
            result_color = DARK_GRAY
        elif self.game.winner == Player.X:
            if self.game_mode == GameMode.AI_MODE and self.game.ai_player == Player.X:
                result_text = "YOU LOSE!"
                result_color = RED
            elif self.game_mode == GameMode.AI_MODE and self.game.ai_player == Player.O:
                result_text = "YOU WIN!"
                result_color = GREEN
            else:
                result_text = "X WINS!"
                result_color = BLUE
        else:  # Player.O wins
            if self.game_mode == GameMode.AI_MODE and self.game.ai_player == Player.X:
                result_text = "YOU WIN!"
                result_color = GREEN
            elif self.game_mode == GameMode.AI_MODE and self.game.ai_player == Player.O:
                result_text = "YOU LOSE!"
                result_color = RED
            else:
                result_text = "O WINS!"
                result_color = RED

        result_surface = self.font_large.render(
            result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(WINDOW_SIZE // 2, 150))
        self.screen.blit(result_surface, result_rect)

        # Draw AI difficulty info if in AI mode
        if self.game_mode == GameMode.AI_MODE:
            diff_text = f"AI Difficulty: {self.current_difficulty.value.upper()}"
            diff_surface = self.font_small.render(diff_text, True, DARK_GRAY)
            diff_rect = diff_surface.get_rect(center=(WINDOW_SIZE // 2, 220))
            self.screen.blit(diff_surface, diff_rect)

        # Draw separator line
        pygame.draw.line(self.screen, GRAY, (80, 260),
                         (WINDOW_SIZE - 80, 260), 2)

        # Draw restart button
        pygame.draw.rect(self.screen, BLUE, self.restart_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.restart_button_rect, 2)
        restart_text = self.font_medium.render("Main Menu", True, WHITE)
        restart_text_rect = restart_text.get_rect(
            center=self.restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)

        # Draw exit button
        pygame.draw.rect(self.screen, RED, self.exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.exit_button_rect, 2)
        exit_text = self.font_medium.render("Exit Game", True, WHITE)
        exit_text_rect = exit_text.get_rect(
            center=self.exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

    def draw_confirm_exit(self):
        """Draw the confirm exit dialog."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, TOTAL_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Draw dialog box
        dialog_x = WINDOW_SIZE // 2 - 200
        dialog_y = TOTAL_HEIGHT // 2 - 100
        dialog_width = 400
        dialog_height = 200
        pygame.draw.rect(self.screen, WHITE, (dialog_x,
                         dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, BLACK, (dialog_x,
                         dialog_y, dialog_width, dialog_height), 3)

        # Draw title
        title_surface = self.font_large.render("Exit Game?", True, BLACK)
        title_rect = title_surface.get_rect(
            center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 - 40))
        self.screen.blit(title_surface, title_rect)

        # Draw exit button
        pygame.draw.rect(self.screen, RED, self.confirm_exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.confirm_exit_button_rect, 2)
        exit_text = self.font_medium.render("Exit", True, WHITE)
        exit_text_rect = exit_text.get_rect(
            center=self.confirm_exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

        # Draw cancel button
        pygame.draw.rect(self.screen, GRAY, self.cancel_exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.cancel_exit_button_rect, 2)
        cancel_text = self.font_medium.render("Cancel", True, BLACK)
        cancel_text_rect = cancel_text.get_rect(
            center=self.cancel_exit_button_rect.center)
        self.screen.blit(cancel_text, cancel_text_rect)

    def draw_board(self):
        """Draw the game board with title at top."""
        self.screen.fill(WHITE)

        # Draw title at top
        title_surface = self.font_large.render("Gomoku Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(WINDOW_SIZE // 2, 30))
        self.screen.blit(title_surface, title_rect)

        # Draw exit button
        pygame.draw.rect(self.screen, RED, self.playing_exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.playing_exit_button_rect, 2)
        exit_text = self.font_small.render("Exit", True, WHITE)
        exit_text_rect = exit_text.get_rect(
            center=self.playing_exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

        # Draw separator line
        pygame.draw.line(self.screen, GRAY, (0, 70), (WINDOW_SIZE, 70), 2)

        # Board position (centered)
        board_left = (WINDOW_SIZE - self.grid_size * CELL_SIZE) // 2
        board_top = 70
        board_width = self.grid_size * CELL_SIZE
        board_height = self.grid_size * CELL_SIZE

        # Draw grid lines (centered)
        for i in range(self.grid_size + 1):
            # Horizontal lines
            pygame.draw.line(self.screen, BLACK, (board_left, board_top + i * CELL_SIZE),
                             (board_left + board_width, board_top + i * CELL_SIZE), 2)
            # Vertical lines
            pygame.draw.line(self.screen, BLACK, (board_left + i * CELL_SIZE, board_top),
                             (board_left + i * CELL_SIZE, board_top + board_height), 2)

        # Draw pieces
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.game.board[row][col] != Player.EMPTY:
                    self.draw_piece(row, col, board_left, board_top)

        # Highlight winning line if win is detected (transition period)
        if self.game.win_found and self.game.winning_line:
            self.highlight_winning_line(
                board_left, board_top, GREEN)

    def draw_piece(self, row: int, col: int, board_left: int, board_top: int = 70):
        """Draw a piece (X or O) at the given position."""
        global radius
        x = board_left + col * CELL_SIZE + CELL_SIZE // 2
        y = board_top + row * CELL_SIZE + CELL_SIZE // 2

        if self.game.board[row][col] == Player.X:
            # Draw X
            offset = radius
            pygame.draw.line(self.screen, BLUE, (x - offset,
                             y - offset), (x + offset, y + offset), 5)
            pygame.draw.line(self.screen, BLUE, (x + offset,
                             y - offset), (x - offset, y + offset), 5)
        elif self.game.board[row][col] == Player.O:
            # Draw O
            pygame.draw.circle(self.screen, RED, (x, y), radius, 5)

    def highlight_winning_line(self, board_left: int, board_top: int = 70, highlight_color: Tuple[int, int, int] = GREEN):
        """Highlight the winning line."""
        global radius
        if len(self.game.winning_line) >= WIN_LENGTH:
            for i in range(len(self.game.winning_line)):
                row, col = self.game.winning_line[i]
                x = board_left + col * CELL_SIZE + CELL_SIZE // 2
                y = board_top + row * CELL_SIZE + CELL_SIZE // 2

                if self.game.winner == Player.X:
                    offset = radius
                    pygame.draw.line(
                        self.screen, highlight_color, (x - offset, y - offset), (x + offset, y + offset), 5)
                    pygame.draw.line(
                        self.screen, highlight_color, (x + offset, y - offset), (x - offset, y + offset), 5)
                else:
                    pygame.draw.circle(
                        self.screen, highlight_color, (x, y), radius, 5)

    def draw_info(self):
        """Draw game information at the bottom."""
        board_top = 70
        board_height = self.grid_size * CELL_SIZE
        info_y = board_top + board_height + 10

        if self.game.game_over:
            if self.game.winner is None:
                text = "It's a Tie! Click Main Menu to play again"
                color = DARK_GRAY
            elif self.game.winner == Player.X:
                text = "Player X Wins! Click Main Menu to play again"
                color = BLUE
            else:
                text = "Player O Wins! Click Main Menu to play again"
                color = RED

            text_surface = self.font_small.render(text, True, color)
            text_rect = text_surface.get_rect(
                center=(WINDOW_SIZE // 2, info_y))
            self.screen.blit(text_surface, text_rect)
            return

        if self.game_mode == GameMode.AI_MODE and self.game.current_player == self.game.ai_player:
            text = f"AI ({self.game.ai_player.get_display_name()}) is thinking..."
            color = PURPLE
        else:
            current = "X" if self.game.current_player == Player.X else "O"
            color = BLUE if self.game.current_player == Player.X else RED

            if self.game_mode == GameMode.AI_MODE:
                if self.game.ai_player == Player.X:
                    text = f"Your Turn (O) - Click to place"
                else:
                    text = f"Your Turn (X) - Click to place"
            else:
                text = f"Player {current}'s Turn (Click to place)"

        text_surface = self.font_small.render(text, True, color)

        if self.game_mode == GameMode.AI_MODE and self.ai_order_text:
            text_rect = text_surface.get_rect(
                center=(WINDOW_SIZE // 2, info_y + 10))
        else:
            text_rect = text_surface.get_rect(
                center=(WINDOW_SIZE // 2, info_y))

        self.screen.blit(text_surface, text_rect)

    def validate_and_set_grid_size(self) -> bool:
        """Validate and set the grid size from input text."""
        try:
            size = int(self.input_text)
            if 8 <= size <= 21:
                self.grid_size = size
                self.update_grid_dependent_vars()
                self.invalid_message = ""
                return True
            else:
                self.invalid_message = "Grid size must be between 8 and 21"
                return False
        except ValueError:
            self.invalid_message = "Please enter a valid number"
            return False

    def handle_click(self, x: int, y: int):
        """Handle mouse click."""
        if self.game_state == GameState.MENU:
            # Check if input box is clicked
            if self.input_box_rect.collidepoint(x, y):
                self.input_active = True
                self.invalid_message = ""
            else:
                self.input_active = False
                if self.invalid_message:
                    self.validate_and_set_grid_size()

            if self.ai_mode_selection_active:
                # Selecting AI difficulty or going back from AI selection
                for button in self.difficulty_buttons:
                    if button['rect'].collidepoint(x, y):
                        self.current_difficulty = button['difficulty']
                        for btn in self.difficulty_buttons:
                            btn['selected'] = (btn['difficulty'] == self.current_difficulty)
                        self.start_ai_mode()
                        return

                if self.pk_mode_button_rect.collidepoint(x, y):
                    self.ai_mode_selection_active = False
                    return

                return

            # Check if AI Mode button is clicked
            if self.ai_mode_button_rect.collidepoint(x, y):
                if self.validate_and_set_grid_size():
                    self.ai_mode_selection_active = True
                    return

            # Check if PK Mode button is clicked
            if self.pk_mode_button_rect.collidepoint(x, y):
                if self.validate_and_set_grid_size():
                    self.ai_mode_selection_active = False
                    self.start_pk_mode()

        elif self.game_state == GameState.PLAYING:
            # Check if exit button is clicked
            if self.playing_exit_button_rect.collidepoint(x, y):
                self.game_state = GameState.CONFIRM_EXIT
                return

            # If a win was found, a click triggers GAME_OVER screen
            if self.game.win_found:
                self.transition_to_game_over()
                return

            # Handle moves based on game mode
            if self.game_mode == GameMode.PK_MODE:
                # Human vs Human - both players click
                pos = self.game.get_position_from_mouse(x, y)
                if pos:
                    row, col = pos
                    self.game.make_move(row, col)
                    if self.game.win_found:
                        self.win_highlight_start_time = pygame.time.get_ticks()
                    elif self.game.game_over:
                        self.game_state = GameState.GAME_OVER

            elif self.game_mode == GameMode.AI_MODE:
                # Only human player clicks (AI moves automatically)
                if self.game.current_player != self.game.ai_player:
                    pos = self.game.get_position_from_mouse(x, y)
                    if pos:
                        row, col = pos
                        if self.game.make_move(row, col):
                            if self.game.win_found:
                                self.win_highlight_start_time = pygame.time.get_ticks()
                            elif self.game.game_over:
                                self.game_state = GameState.GAME_OVER
                            elif self.game.current_player == self.game.ai_player:
                                self.next_ai_move_time = pygame.time.get_ticks() + 600

        elif self.game_state == GameState.CONFIRM_EXIT:
            if self.confirm_exit_button_rect.collidepoint(x, y):
                self.game_state = GameState.MENU
            elif self.cancel_exit_button_rect.collidepoint(x, y):
                self.game_state = GameState.PLAYING

        elif self.game_state == GameState.GAME_OVER:
            if self.restart_button_rect.collidepoint(x, y):
                self.game_state = GameState.MENU
            elif self.exit_button_rect.collidepoint(x, y):
                pygame.time.wait(200)
                pygame.quit()
                sys.exit()

    def handle_key(self, key: int, unicode_char: Optional[str] = None):
        """Handle keyboard input."""
        if self.game_state == GameState.MENU:
            if self.input_active:
                self.invalid_message = ""  # Clear error message on typing
                if key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif key == pygame.K_RETURN:
                    self.input_active = False
                    self.validate_and_set_grid_size()
                elif key == pygame.K_ESCAPE:
                    self.input_active = False
                    self.input_text = str(self.grid_size)
                elif unicode_char and unicode_char.isdigit() and len(self.input_text) < 3:
                    self.input_text += unicode_char

        elif key == pygame.K_r and self.game_state == GameState.GAME_OVER:
            self.game_state = GameState.MENU
        elif key == pygame.K_q and self.game_state in (GameState.PLAYING, GameState.GAME_OVER, GameState.CONFIRM_EXIT):
            if self.game_state == GameState.CONFIRM_EXIT:
                self.game_state = GameState.PLAYING
            else:
                self.game_state = GameState.MENU
        elif key == pygame.K_ESCAPE and self.game_state == GameState.PLAYING:
            self.game_state = GameState.CONFIRM_EXIT

    def run(self):
        """Main game loop."""
        running = True

        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos[0], event.pos[1])
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key, event.unicode)

            # Handle AI moves (only in AI mode)
            if (self.game_state == GameState.PLAYING and
                self.game_mode == GameMode.AI_MODE and
                not self.game.game_over and
                not self.game.win_found and
                self.game.ai_instance is not None and
                self.game.current_player == self.game.ai_player and
                self.next_ai_move_time is not None and
                    current_time >= self.next_ai_move_time):

                # Get AI move after the wait interval
                ai_move = self.game.ai_instance.get_move(self.game.board)
                if ai_move is not None:
                    row, col = ai_move
                    self.game.make_move(row, col)
                    self.next_ai_move_time = None
                    if self.game.win_found:
                        self.win_highlight_start_time = current_time
                    elif self.game.game_over:
                        self.game_state = GameState.GAME_OVER

            # Draw based on game state
            if self.game_state == GameState.MENU:
                self.draw_menu()
            elif self.game_state == GameState.PLAYING:
                self.draw_board()
                self.draw_info()

                # Auto transition to GAME_OVER after 2 seconds of win highlight
                if self.game.win_found and self.win_highlight_start_time:
                    if current_time - self.win_highlight_start_time >= 2000:
                        self.transition_to_game_over()
            elif self.game_state == GameState.CONFIRM_EXIT:
                self.draw_board()
                self.draw_info()
                self.draw_confirm_exit()
            elif self.game_state == GameState.GAME_OVER:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    ui = GameUI()
    ui.run()
