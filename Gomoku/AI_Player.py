"""
AI Player Module for Gomoku Game
Contains multiple AI implementations with different difficulty levels
"""

from enum import Enum
import random
from typing import List, Tuple, Optional


class Player(Enum):
    EMPTY = 0
    X = 1
    O = 2

    def get_display_name(self):
        if self == Player.X:
            return "X"
        elif self == Player.O:
            return "O"
        else:
            return "."


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class BaseAI:
    """Base class for all AI implementations"""

    def __init__(self, player_symbol: Player):
        self.player = player_symbol
        self.opponent = Player.O if player_symbol == Player.X else Player.X
        self.name = "Base AI"

    def get_move(self, board: List[List]) -> Optional[Tuple[int, int]]:
        """Get the best move for the AI. Override in child classes."""
        raise NotImplementedError

    @staticmethod
    def is_board_empty(board: List[List]) -> bool:
        """Check if the board has no pieces."""
        for row in board:
            if any(cell != Player.EMPTY for cell in row):
                return False
        return True

    @staticmethod
    def is_board_full(board: List[List]) -> bool:
        """Check if all cells on the board are occupied."""
        for row in board:
            for cell in row:
                if cell == Player.EMPTY:
                    return False
        return True

    @staticmethod
    def get_empty_positions(board: List[List]) -> List[Tuple[int, int]]:
        """Get all empty positions on the board."""
        empty = []
        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] == Player.EMPTY:
                    empty.append((r, c))
        return empty

    @staticmethod
    def count_line(board: List[List], row: int, col: int,
                   delta_row: int, delta_col: int, player: Player) -> Tuple[int, List, List]:
        """Count consecutive pieces in a line."""
        grid_size = len(board)
        count = 1
        line_cells = [(row, col)]
        ends = []

        # Positive direction
        r, c = row + delta_row, col + delta_col
        while 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == player:
            count += 1
            line_cells.append((r, c))
            r += delta_row
            c += delta_col
        if 0 <= r < grid_size and 0 <= c < grid_size:
            ends.append((r, c))

        # Negative direction
        r, c = row - delta_row, col - delta_col
        while 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == player:
            count += 1
            line_cells.append((r, c))
            r -= delta_row
            c -= delta_col
        if 0 <= r < grid_size and 0 <= c < grid_size:
            ends.append((r, c))

        return count, line_cells, ends


class RandomAI(BaseAI):
    """Very weak AI - places pieces randomly"""

    def __init__(self, player_symbol: Player):
        super().__init__(player_symbol)
        self.name = "Random AI"

    def get_move(self, board: List[List]) -> Optional[Tuple[int, int]]:
        empty_positions = self.get_empty_positions(board)
        if empty_positions:
            return random.choice(empty_positions)
        return None


class SimpleHeuristicAI(BaseAI):
    """AI with improved scoring"""
    def __init__(self, player_symbol: Player):
        super().__init__(player_symbol)
        self.name = "Simple AI"

    def get_move(self, board: List[List]) -> Optional[Tuple[int, int]]:
        board_size = len(board)

        # Center control for empty board
        if self.is_board_empty(board):
            center = board_size // 2
            return (center, center)

        best_score = -1
        best_move = None

        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == Player.EMPTY:
                    # Score for AI
                    self_score = self.evaluate_position(
                        board, row, col, self.player)

                    # Defensive score (block opponent)
                    opponent_score = self.evaluate_position(
                        board, row, col, self.opponent)

                    # Combine with defensive weight
                    total_score = self_score * 0.7 + opponent_score * 0.3

                    # Center bias (small bonus for center positions)
                    center = board_size // 2
                    dist_to_center = abs(row - center) + abs(col - center)
                    center_bonus = (board_size - dist_to_center) * 2
                    total_score += center_bonus

                    if total_score > best_score:
                        best_score = total_score
                        best_move = (row, col)

        return best_move

    def evaluate_position(self, board: List[List], row: int, col: int,
                          player: Player) -> int:
        """Evaluate position with improved scoring"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        original = board[row][col]
        board[row][col] = player

        for dr, dc in directions:
            count, _, _ = self.count_line(board, row, col, dr, dc, player)
            # Exponential scoring - longer lines are much more valuable
            if count >= 5:
                score += 100000
            else:
                score += 10 ** min(5, count)

        board[row][col] = original
        return score


class PatternRecognitionAI(SimpleHeuristicAI):
    """Advanced AI using pattern recognition"""

    def __init__(self, player_symbol: Player):
        super().__init__(player_symbol)
        self.name = "Pattern AI"

        # Pattern weights (higher = more valuable)
        self.pattern_scores = {
            'FIVE': 100000,          # Win
            'OPEN_FOUR': 10000,      # Four in a row with open ends
            'CLOSED_FOUR': 5000,     # Four in a row with one blocked end
            'OPEN_THREE': 2000,      # Three in a row with open ends
            'CLOSED_THREE': 500,     # Three in a row with one blocked end
            'OPEN_TWO': 100,         # Two in a row with open ends
            'CLOSED_TWO': 20,        # Two in a row with one blocked end
            'SINGLE': 5
        }

    def get_move(self, board: List[List]) -> Optional[Tuple[int, int]]:
        board_size = len(board)

        if self.is_board_empty(board):
            return (board_size // 2, board_size // 2)

        best_score = -float('inf')
        best_move = None

        # Only consider positions near existing pieces (optimization)
        candidates = self.get_candidate_moves(board, radius=2)

        for row, col in candidates:
            if board[row][col] == Player.EMPTY:
                # Offensive score
                score = self.evaluate_position_advanced(
                    board, row, col, self.player)

                # Defensive score (block opponent's threats)
                opponent_score = self.evaluate_position_advanced(
                    board, row, col, self.opponent)

                total_score = score * 0.75 + opponent_score * 0.25

                # Center bonus
                center = board_size // 2
                dist_to_center = abs(row - center) + abs(col - center)
                center_bonus = max(0, (board_size - dist_to_center)) * 2
                total_score += center_bonus

                if total_score > best_score:
                    best_score = total_score
                    best_move = (row, col)

        return best_move

    def evaluate_position_advanced(self, board: List[List], row: int, col: int,
                                   player: Player) -> int:
        """Advanced evaluation using pattern recognition"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        original = board[row][col]
        board[row][col] = player

        for dr, dc in directions:
            pattern_type = self.analyze_line_pattern(
                board, row, col, dr, dc, player)
            score += self.pattern_scores.get(pattern_type, 0)

        board[row][col] = original
        return score

    def analyze_line_pattern(self, board: List[List], row: int, col: int,
                             dr: int, dc: int, player: Player) -> str:
        """Analyze a line to determine what pattern it forms"""

        # Count consecutive pieces and open ends
        total_length = 1  # Start with current piece
        total_length, _, ends = self.count_line(board, row, col, dr, dc, player)
        open_ends = 0
        if ends:
            for end in ends:
                open_ends += (board[end[0]][end[1]] == Player.EMPTY)


        # Determine pattern type
        if total_length >= 5:
            return 'FIVE'
        elif total_length == 4:
            return 'OPEN_FOUR' if open_ends >= 2 else 'CLOSED_FOUR'
        elif total_length == 3:
            return 'OPEN_THREE' if open_ends >= 2 else 'CLOSED_THREE'
        elif total_length == 2:
            return 'OPEN_TWO' if open_ends >= 2 else 'CLOSED_TWO'
        else:
            return 'SINGLE'

    def get_candidate_moves(self, board: List[List], radius: int = 3) -> List[Tuple[int, int]]:
        """Optimization: only consider positions near existing pieces"""
        board_size = len(board)
        candidates = set()

        # Find all positions with pieces
        for r in range(board_size):
            for c in range(board_size):
                if board[r][c] != Player.EMPTY:
                    # Add surrounding positions
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < board_size and 0 <= nc < board_size
                                    and board[nr][nc] == Player.EMPTY):
                                candidates.add((nr, nc))

        # If no candidates (empty board), return center
        if not candidates:
            center = board_size // 2
            return [(center, center)]

        return list(candidates)


class MinimaxAI(PatternRecognitionAI):
    """Advanced AI using Minimax with Alpha-Beta pruning"""

    def __init__(self, player_symbol: Player, depth: int = 3):
        super().__init__(player_symbol)
        self.name = f"Minimax AI (Depth {depth})"
        self.max_depth = depth
        self.node_count = 0

    def get_move(self, board: List[List]) -> Optional[Tuple[int, int]]:
        self.node_count = 0
        board_size = len(board)

        # Quick response for empty board
        if self.is_board_empty(board):
            return (board_size // 2, board_size // 2)

        # Get candidate moves (optimization)
        candidates = self.get_candidate_moves(board, radius=2)

        best_score = -float('inf')
        best_move = None

        for row, col in candidates:
            if board[row][col] == Player.EMPTY:
                board[row][col] = self.player
                score = self.minimax(board, self.max_depth - 1,
                                     -float('inf'), float('inf'), False)
                board[row][col] = Player.EMPTY

                if score > best_score:
                    best_score = score
                    best_move = (row, col)

        print(f"Minimax evaluated {self.node_count} positions")
        return best_move

    def minimax(self, board: List[List], depth: int,
                alpha: float, beta: float, is_maximizing: bool) -> float:
        """Minimax with alpha-beta pruning"""
        self.node_count += 1

        # Check terminal states
        winner = self.check_winner_state(board)
        if winner == self.player:
            return 10000 + depth  # Prefer faster wins
        elif winner == self.opponent:
            return -10000 - depth
        elif self.is_board_full(board) or depth == 0:
            return self.evaluate_board(board)

        if is_maximizing:
            max_score = -float('inf')
            candidates = self.get_candidate_moves(board, radius=2)

            # Sort candidates by potential value (optimization)
            candidates = self.order_moves(board, candidates, self.player)

            for row, col in candidates:
                if board[row][col] == Player.EMPTY:
                    board[row][col] = self.player
                    score = self.minimax(board, depth - 1, alpha, beta, False)
                    board[row][col] = Player.EMPTY

                    max_score = max(max_score, score)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break  # Beta cutoff

            return max_score
        else:
            min_score = float('inf')
            candidates = self.get_candidate_moves(board, radius=2)

            # Sort candidates for opponent as well
            candidates = self.order_moves(board, candidates, self.opponent)

            for row, col in candidates:
                if board[row][col] == Player.EMPTY:
                    board[row][col] = self.opponent
                    score = self.minimax(board, depth - 1, alpha, beta, True)
                    board[row][col] = Player.EMPTY

                    min_score = min(min_score, score)
                    beta = min(beta, score)
                    if beta <= alpha:
                        break  # Alpha cutoff

            return min_score

    def order_moves(self, board: List[List], moves: List[Tuple[int, int]],
                    player: Player) -> List[Tuple[int, int]]:
        """Order moves by heuristic value for better pruning"""
        move_scores = []
        for row, col in moves:
            if board[row][col] == Player.EMPTY:
                score = self.evaluate_position_advanced(
                    board, row, col, player)
                move_scores.append((score, row, col))

        # Sort by score descending
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [(row, col) for _, row, col in move_scores]

    def evaluate_board(self, board: List[List]) -> float:
        """Heuristic evaluation of entire board"""
        total_score = 0.0

        # Evaluate for AI player
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == self.player:
                    total_score += self.evaluate_position_advanced(
                        board, r, c, self.player)
                elif board[r][c] == self.opponent:
                    total_score -= self.evaluate_position_advanced(
                        board, r, c, self.opponent) * 0.8

        # Center control bonus
        center = len(board) // 2
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == self.player:
                    dist = abs(r - center) + abs(c - center)
                    total_score += max(0, (len(board) - dist)) * 2

        return total_score

    def check_winner_state(self, board: List[List]) -> Optional[Player]:
        """Check if there's a winner without needing position"""
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] != Player.EMPTY:
                    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                        count, _, _ = self.count_line(
                            board, r, c, dr, dc, board[r][c])
                        if count >= 5:
                            return board[r][c]
        return None


class AIFactory:
    """Factory class to create AI instances based on difficulty"""

    @staticmethod
    def create_ai(difficulty: Difficulty, player_symbol: Player) -> BaseAI:
        """Create an AI instance with specified difficulty"""

        if difficulty == Difficulty.EASY:
            return RandomAI(player_symbol)
        elif difficulty == Difficulty.MEDIUM:
            return SimpleHeuristicAI(player_symbol)
        elif difficulty == Difficulty.HARD:
            return PatternRecognitionAI(player_symbol)
        elif difficulty == Difficulty.EXPERT:
            return MinimaxAI(player_symbol, depth=3)
        else:
            return SimpleHeuristicAI(player_symbol)

    @staticmethod
    def get_available_difficulties() -> List[Tuple[Difficulty, str]]:
        """Get list of available difficulties with descriptions"""
        return [
            (Difficulty.EASY, "Random moves - Very weak"),
            (Difficulty.MEDIUM, "Simple heuristic - Weak"),
            (Difficulty.HARD, "Pattern recognition - Strong"),
            (Difficulty.EXPERT, "Minimax search - Very strong (slower)")
        ]


# For backward compatibility with your existing code
AI_Player = SimpleHeuristicAI
