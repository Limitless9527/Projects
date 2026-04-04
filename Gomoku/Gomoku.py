import pygame
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
BOARD_HEIGHT = 630
UI_HEIGHT = 120
TOTAL_HEIGHT = 750
DEFAULT_GRID_SIZE = 15
CELL_SIZE = BOARD_HEIGHT // DEFAULT_GRID_SIZE
radius = CELL_SIZE // 3
WIN_LENGTH = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
DARK_GRAY = (100, 100, 100)


# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    CONFIRM_EXIT = 4


# Player enum
class Player(Enum):
    EMPTY = 0
    X = 1
    O = 2


class GomokuGame:
    def __init__(self, grid_size=DEFAULT_GRID_SIZE):
        self.grid_size = grid_size
        self.board = [[Player.EMPTY for _ in range(
            self.grid_size)] for _ in range(self.grid_size)]
        self.current_player = Player.X
        self.game_over = False
        self.winner = None
        self.winning_line = []
        self.win_found = False  # True when a winning line is detected, before GAME_OVER screen

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

    def check_winner(self, row: int, col: int):
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

    def _check_line(self, row: int, col: int, delta_row: int, delta_col: int, player: Player) -> bool:
        """Check if there's a line of WIN_LENGTH in the given direction."""
        count = 1
        line_cells = [(row, col)]

        # Check in positive direction
        r, c = row + delta_row, col + delta_col
        while 0 <= r < self.grid_size and 0 <= c < self.grid_size and self.board[r][c] == player:
            count += 1
            line_cells.append((r, c))
            r += delta_row
            c += delta_col

        # Check in negative direction
        r, c = row - delta_row, col - delta_col
        while 0 <= r < self.grid_size and 0 <= c < self.grid_size and self.board[r][c] == player:
            count += 1
            line_cells.append((r, c))
            r -= delta_row
            c -= delta_col

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

    def get_position_from_mouse(self, x: int, y: int) -> tuple[int, int] | None:
        """Convert mouse coordinates to board position."""
        board_left = (WINDOW_SIZE - self.grid_size * CELL_SIZE) // 2
        board_top = 70

        if x < board_left or x > board_left + self.grid_size * CELL_SIZE or y < board_top or y > board_top + BOARD_HEIGHT:
            return None

        col = (x - board_left) // CELL_SIZE
        row = (y - board_top) // CELL_SIZE

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return row, col
        return None


class GameUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, TOTAL_HEIGHT))
        pygame.display.set_caption("Gomoku Game")
        self.clock = pygame.time.Clock()

        # Font size
        self.font_title = pygame.font.Font(None, 100)
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 30)

        #Initialize
        self.grid_size = DEFAULT_GRID_SIZE
        self.game = GomokuGame(self.grid_size)
        self.game_state = GameState.MENU
        self.win_highlight_start_time = None

        # Button rectangle (centered, below title on menu)
        self.start_button_rect = pygame.Rect(
            WINDOW_SIZE // 2 - 100, TOTAL_HEIGHT // 2 + 50, 200, 60)

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
        self.input_box_rect = pygame.Rect(WINDOW_SIZE // 2 - 50, TOTAL_HEIGHT // 2 - 50, 100, 40)
        self.input_text = str(self.grid_size)
        self.input_active = False
        self.invalid_message = ""
        self.update_grid_dependent_vars()

    def validate_and_set_grid_size(self):
        """Validate and set the grid size from input text."""
        try:
            size = int(self.input_text)
            if 8 <= size <= 21:
                self.grid_size = size
                self.update_grid_dependent_vars()
                self.invalid_message = ""
            else:
                self.invalid_message = "Grid size must be between 8 and 21"
        except ValueError:
            self.invalid_message = "Please enter a valid number"

    def update_grid_dependent_vars(self):
        """Update variables that depend on grid_size."""
        global CELL_SIZE, radius
        CELL_SIZE = BOARD_HEIGHT // self.grid_size
        radius = CELL_SIZE // 3

    def draw_menu(self):
        """Draw the main menu screen."""
        self.screen.fill(WHITE)

        # Draw title
        title_surface = self.font_title.render("Gomoku Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(WINDOW_SIZE // 2, 120))
        self.screen.blit(title_surface, title_rect)

        # Draw subtitle
        subtitle_surface = self.font_small.render(
            "Connect 5 to Win", True, GRAY)
        subtitle_rect = subtitle_surface.get_rect(
            center=(WINDOW_SIZE // 2, 220))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # Draw grid size label
        label_surface = self.font_small.render("Grid Size (8-21):", True, BLACK)
        label_rect = label_surface.get_rect(center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 - 100))
        self.screen.blit(label_surface, label_rect)

        # Draw input box
        pygame.draw.rect(self.screen, LIGHT_GRAY if self.input_active else GRAY, self.input_box_rect)
        pygame.draw.rect(self.screen, BLACK, self.input_box_rect, 2)
        text_surface = self.font_medium.render(self.input_text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.input_box_rect.center)
        self.screen.blit(text_surface, text_rect)

        # Draw blinking cursor if active
        if self.input_active:
            text_width = text_surface.get_width()
            cursor_x = self.input_box_rect.centerx + text_width // 2 + 2
            cursor_y = self.input_box_rect.centery
            if (pygame.time.get_ticks() // 500) % 2 == 0:  # Blink every 500ms
                pygame.draw.line(self.screen, BLACK, (cursor_x, cursor_y - 10), (cursor_x, cursor_y + 10), 2)

        # Draw invalid message if any
        if self.invalid_message:
            error_surface = self.font_small.render(self.invalid_message, True, RED)
            error_rect = error_surface.get_rect(center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 - 70))
            self.screen.blit(error_surface, error_rect)

        # Draw start button
        pygame.draw.rect(self.screen, BLUE, self.start_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.start_button_rect, 3)

        button_text = self.font_medium.render("START GAME", True, WHITE)
        button_text_rect = button_text.get_rect(
            center=self.start_button_rect.center)
        self.screen.blit(button_text, button_text_rect)

        # Draw instructions
        inst_surface = self.font_small.render(
            "Click START GAME or press SPACE/ENTER to begin", True, DARK_GRAY)
        inst_rect = inst_surface.get_rect(center=(WINDOW_SIZE // 2, 400))
        self.screen.blit(inst_surface, inst_rect)

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
            result_text = "IT'S A TIE"
            result_color = DARK_GRAY
        elif self.game.winner == Player.X:
            result_text = "X WINS"
            result_color = BLUE
        else:
            result_text = "O WINS"
            result_color = RED

        result_surface = self.font_large.render(
            result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(WINDOW_SIZE // 2, 150))
        self.screen.blit(result_surface, result_rect)

        # Draw separator line
        pygame.draw.line(self.screen, GRAY, (80, 220),
                         (WINDOW_SIZE - 80, 220), 2)

        # Draw restart button
        pygame.draw.rect(self.screen, BLUE, self.restart_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.restart_button_rect, 2)
        restart_text = self.font_medium.render("Restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(
            center=self.restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)

        # Draw exit button
        pygame.draw.rect(self.screen, RED, self.exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.exit_button_rect, 2)
        exit_text = self.font_medium.render("Exit", True, WHITE)
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
        pygame.draw.rect(self.screen, WHITE, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, BLACK, (dialog_x, dialog_y, dialog_width, dialog_height), 3)

        # Draw title
        title_surface = self.font_large.render("Exit Game?", True, BLACK)
        title_rect = title_surface.get_rect(center=(WINDOW_SIZE // 2, TOTAL_HEIGHT // 2 - 40))
        self.screen.blit(title_surface, title_rect)

        # Draw exit button
        pygame.draw.rect(self.screen, RED, self.confirm_exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.confirm_exit_button_rect, 2)
        exit_text = self.font_medium.render("Exit", True, WHITE)
        exit_text_rect = exit_text.get_rect(center=self.confirm_exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

        # Draw cancel button
        pygame.draw.rect(self.screen, GRAY, self.cancel_exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.cancel_exit_button_rect, 2)
        cancel_text = self.font_medium.render("Cancel", True, BLACK)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_exit_button_rect.center)
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
        exit_text_rect = exit_text.get_rect(center=self.playing_exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

        # Draw separator line
        pygame.draw.line(self.screen, GRAY, (0, 70), (WINDOW_SIZE, 70), 2)

        # Board position (centered)
        board_left = (WINDOW_SIZE - self.grid_size * CELL_SIZE) // 2
        board_top = 70
        board_width = self.grid_size * CELL_SIZE
        board_height = BOARD_HEIGHT

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
                board_left, board_top, (105, 227, 23))  # 69E317 in RGB

    def draw_piece(self, row, col, board_left, board_top=70):
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

    def highlight_winning_line(self, board_left, board_top=70, highlight_color=(105, 227, 23)):
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
                    pygame.draw.circle(self.screen, highlight_color, (x, y), radius, 5)

    def draw_info(self):
        """Draw game information at the bottom."""
        info_y = BOARD_HEIGHT + 100

        if self.game.game_over:
            if self.game.winner is None:
                # It's a tie
                text = "It's a Tie! Press R to restart or Q to menu"
                color = DARK_GRAY
            elif self.game.winner == Player.X:
                text = "Player X Wins! Press R to restart or Q to menu"
                color = BLUE
            else:
                text = "Player O Wins! Press R to restart or Q to menu"
                color = RED
            text_surface = self.font_small.render(text, True, color)
        else:
            current = "X" if self.game.current_player == Player.X else "O"
            color = BLUE if self.game.current_player == Player.X else RED
            text = f"Player {current}'s Turn (Click to place)"
            text_surface = self.font_small.render(text, True, color)

        text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, info_y))
        self.screen.blit(text_surface, text_rect)

    def handle_click(self, x, y):
        """Handle mouse click."""
        if self.game_state == GameState.MENU:
            # Check if input box is clicked
            if self.input_box_rect.collidepoint(x, y):
                self.input_active = True
                self.invalid_message = ""  # Clear error message
            else:
                self.input_active = False
                if self.invalid_message:  # If there was an error, validate on click outside
                    self.validate_and_set_grid_size()
            
            # Check if start button is clicked
            if self.start_button_rect.collidepoint(x, y):
                self.validate_and_set_grid_size()
                if not self.invalid_message:  # Only start if valid
                    self.start_game()

        elif self.game_state == GameState.PLAYING:
            # Check if exit button is clicked
            if self.playing_exit_button_rect.collidepoint(x, y):
                self.game_state = GameState.CONFIRM_EXIT
                return
            # If a win was found, a click triggers GAME_OVER screen
            if self.game.win_found:
                self.transition_to_game_over()
                return

            pos = self.game.get_position_from_mouse(x, y)
            if pos:
                row, col = pos
                self.game.make_move(row, col)
                if self.game.win_found:
                    self.win_highlight_start_time = pygame.time.get_ticks()
                elif self.game.game_over:
                    self.game_state = GameState.GAME_OVER
        
        elif self.game_state == GameState.CONFIRM_EXIT:
            if self.confirm_exit_button_rect.collidepoint(x, y):
                self.game_state = GameState.MENU
            elif self.cancel_exit_button_rect.collidepoint(x, y):
                self.game_state = GameState.PLAYING
        
        elif self.game_state == GameState.GAME_OVER:
            # Check if buttons are clicked
            if self.restart_button_rect.collidepoint(x, y):
                self.game_state = GameState.MENU
            elif self.exit_button_rect.collidepoint(x, y):
                pygame.time.wait(200)
                pygame.quit()
                sys.exit()

    def start_game(self):
        """Start a new game."""
        self.game = GomokuGame(self.grid_size)
        self.game_state = GameState.PLAYING

    def handle_key(self, key, unicode_char=None):
        """Handle keyboard input."""
        if self.game_state == GameState.MENU:
            if key == pygame.K_RETURN:
                self.validate_and_set_grid_size()
                if not self.invalid_message:
                    self.start_game()
                self.input_active = False
            elif self.input_active:
                self.invalid_message = ""  # Clear error message on typing
                if key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif key == pygame.K_ESCAPE:
                    self.input_active = False
                    self.input_text = str(self.grid_size)
                elif unicode_char and unicode_char.isdigit() and len(self.input_text) < 3:
                    self.input_text += unicode_char
            elif key == pygame.K_SPACE:
                self.validate_and_set_grid_size()
                if not self.invalid_message:  # Only start if valid
                    self.start_game()
        elif key == pygame.K_r and self.game_state == GameState.GAME_OVER:
            self.game_state = GameState.MENU
        elif key == pygame.K_q and self.game_state in (GameState.PLAYING, GameState.GAME_OVER, GameState.CONFIRM_EXIT):
            if self.game_state == GameState.CONFIRM_EXIT:
                self.game_state = GameState.PLAYING
            else:
                self.game_state = GameState.MENU
        


    def run(self):
        """Main game loop."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos[0], event.pos[1])
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key, event.unicode)

            # Draw based on game state
            if self.game_state == GameState.MENU:
                self.draw_menu()
            elif self.game_state == GameState.PLAYING:
                self.draw_board()
                self.draw_info()

                # Auto transition to GAME_OVER after 2 seconds of win highlight
                if self.game.win_found and self.win_highlight_start_time:
                    if pygame.time.get_ticks() - self.win_highlight_start_time >= 2000:
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

