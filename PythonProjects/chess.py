#!/usr/bin/env python3
"""
A complete GUI–based chess game implemented in one Python script using Tkinter.
Click a piece to select it and then click on a destination square to move.
Pawn promotions default to a queen.
"""

import tkinter as tk
from tkinter import messagebox

# --------- Chess Engine Code (adapted from a text–based version) ---------

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def parse_move(move_str):
    """
    Parse a move string like "e2e4" or "e7e8Q" (for promotion).
    Returns a dictionary with the source and destination squares and (if provided) a promotion piece.
    (Not used in the GUI version.)
    """
    move_str = move_str.strip()
    if len(move_str) not in [4, 5]:
        return None
    try:
        col_from = ord(move_str[0].lower()) - ord('a')
        row_from = 8 - int(move_str[1])
        col_to = ord(move_str[2].lower()) - ord('a')
        row_to = 8 - int(move_str[3])
    except Exception:
        return None
    promotion = move_str[4].upper() if len(move_str) == 5 else None
    return {"from": (row_from, col_from), "to": (row_to, col_to),
            "promotion": promotion, "castling": None, "en_passant": False}

class ChessGame:
    def __init__(self):
        # Initialize board as an 8x8 list. Each square is either None or a two–character string.
        # The first character is the color ("w" or "b") and the second is the piece type:
        # K, Q, R, B, N, or P.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.turn = "w"  # "w" (White) or "b" (Black)
        # Castling rights.
        self.castling_rights = {"wK": True, "wQ": True, "bK": True, "bQ": True}
        # En passant target square: a tuple (row, col) or None.
        self.en_passant_target = None
        self.fullmove_number = 1

    def get_legal_moves(self, color):
        """Generate all legal moves for the given color."""
        pseudo_moves = self.get_pseudolegal_moves(color)
        legal_moves = []
        for move in pseudo_moves:
            new_board = self.simulate_move(move, color)
            if not self.is_in_check(new_board, color):
                legal_moves.append(move)
        return legal_moves

    def get_pseudolegal_moves(self, color):
        """Generate moves that obey piece–movement rules (but may leave king in check)."""
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece[0] == color:
                    p_type = piece[1]
                    if p_type == 'P':
                        moves.extend(self.get_pawn_moves(r, c, color))
                    elif p_type == 'N':
                        moves.extend(self.get_knight_moves(r, c, color))
                    elif p_type == 'B':
                        moves.extend(self.get_bishop_moves(r, c, color))
                    elif p_type == 'R':
                        moves.extend(self.get_rook_moves(r, c, color))
                    elif p_type == 'Q':
                        moves.extend(self.get_queen_moves(r, c, color))
                    elif p_type == 'K':
                        moves.extend(self.get_king_moves(r, c, color))
        return moves

    def get_pawn_moves(self, r, c, color):
        moves = []
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        promotion_row = 0 if color == 'w' else 7
        # One square forward
        new_r = r + direction
        if in_bounds(new_r, c) and self.board[new_r][c] is None:
            if new_r == promotion_row:
                for promo in ['Q', 'R', 'B', 'N']:
                    moves.append({"from": (r, c), "to": (new_r, c),
                                  "promotion": promo, "castling": None, "en_passant": False})
            else:
                moves.append({"from": (r, c), "to": (new_r, c),
                              "promotion": None, "castling": None, "en_passant": False})
            # Two squares forward from starting row
            if r == start_row:
                new_r2 = r + 2 * direction
                if self.board[new_r2][c] is None:
                    moves.append({"from": (r, c), "to": (new_r2, c),
                                  "promotion": None, "castling": None, "en_passant": False})
        # Diagonal captures and en passant
        for dc in [-1, 1]:
            new_c = c + dc
            new_r = r + direction
            if in_bounds(new_r, new_c):
                target = self.board[new_r][new_c]
                if target is not None and target[0] != color:
                    if new_r == promotion_row:
                        for promo in ['Q', 'R', 'B', 'N']:
                            moves.append({"from": (r, c), "to": (new_r, new_c),
                                          "promotion": promo, "castling": None, "en_passant": False})
                    else:
                        moves.append({"from": (r, c), "to": (new_r, new_c),
                                      "promotion": None, "castling": None, "en_passant": False})
            # En passant capture:
            if self.en_passant_target == (new_r, new_c):
                moves.append({"from": (r, c), "to": (new_r, new_c),
                              "promotion": None, "castling": None, "en_passant": True})
        return moves

    def get_knight_moves(self, r, c, color):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_r = r + dr
            new_c = c + dc
            if in_bounds(new_r, new_c):
                target = self.board[new_r][new_c]
                if target is None or target[0] != color:
                    moves.append({"from": (r, c), "to": (new_r, new_c),
                                  "promotion": None, "castling": None, "en_passant": False})
        return moves

    def get_sliding_moves(self, r, c, color, directions):
        moves = []
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            while in_bounds(new_r, new_c):
                target = self.board[new_r][new_c]
                if target is None:
                    moves.append({"from": (r, c), "to": (new_r, new_c),
                                  "promotion": None, "castling": None, "en_passant": False})
                else:
                    if target[0] != color:
                        moves.append({"from": (r, c), "to": (new_r, new_c),
                                      "promotion": None, "castling": None, "en_passant": False})
                    break
                new_r += dr
                new_c += dc
        return moves

    def get_bishop_moves(self, r, c, color):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.get_sliding_moves(r, c, color, directions)

    def get_rook_moves(self, r, c, color):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.get_sliding_moves(r, c, color, directions)

    def get_queen_moves(self, r, c, color):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                      (-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.get_sliding_moves(r, c, color, directions)

    def get_king_moves(self, r, c, color):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_r = r + dr
                new_c = c + dc
                if in_bounds(new_r, new_c):
                    target = self.board[new_r][new_c]
                    if target is None or target[0] != color:
                        moves.append({"from": (r, c), "to": (new_r, new_c),
                                      "promotion": None, "castling": None, "en_passant": False})
        # Castling moves (only if king is not in check)
        if not self.is_in_check(self.board, color):
            if color == 'w' and (r, c) == (7, 4):
                # White kingside
                if self.castling_rights.get("wK", False):
                    if self.board[7][5] is None and self.board[7][6] is None:
                        if (not self.square_under_attack(7, 5, 'b') and
                            not self.square_under_attack(7, 6, 'b')):
                            moves.append({"from": (7, 4), "to": (7, 6),
                                          "promotion": None, "castling": "kingside", "en_passant": False})
                # White queenside
                if self.castling_rights.get("wQ", False):
                    if (self.board[7][1] is None and self.board[7][2] is None and self.board[7][3] is None):
                        if (not self.square_under_attack(7, 3, 'b') and
                            not self.square_under_attack(7, 2, 'b')):
                            moves.append({"from": (7, 4), "to": (7, 2),
                                          "promotion": None, "castling": "queenside", "en_passant": False})
            elif color == 'b' and (r, c) == (0, 4):
                # Black kingside
                if self.castling_rights.get("bK", False):
                    if self.board[0][5] is None and self.board[0][6] is None:
                        if (not self.square_under_attack(0, 5, 'w') and
                            not self.square_under_attack(0, 6, 'w')):
                            moves.append({"from": (0, 4), "to": (0, 6),
                                          "promotion": None, "castling": "kingside", "en_passant": False})
                # Black queenside
                if self.castling_rights.get("bQ", False):
                    if (self.board[0][1] is None and self.board[0][2] is None and self.board[0][3] is None):
                        if (not self.square_under_attack(0, 3, 'w') and
                            not self.square_under_attack(0, 2, 'w')):
                            moves.append({"from": (0, 4), "to": (0, 2),
                                          "promotion": None, "castling": "queenside", "en_passant": False})
        return moves

    def square_under_attack(self, r, c, attacker_color):
        return self.is_square_attacked(self.board, r, c, attacker_color)

    def is_square_attacked(self, board, r, c, attacker_color):
        # Check pawn attacks.
        if attacker_color == 'w':
            pawn_dirs = [(1, -1), (1, 1)]
        else:
            pawn_dirs = [(-1, -1), (-1, 1)]
        for dr, dc in pawn_dirs:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                piece = board[rr][cc]
                if piece == attacker_color + 'P':
                    return True
        # Check knight attacks.
        knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                          (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_offsets:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                piece = board[rr][cc]
                if piece == attacker_color + 'N':
                    return True
        # Check sliding pieces (rook/queen).
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            while in_bounds(rr, cc):
                piece = board[rr][cc]
                if piece is None:
                    rr += dr
                    cc += dc
                    continue
                if piece[0] == attacker_color and (piece[1] == 'R' or piece[1] == 'Q'):
                    return True
                break
        # Check sliding pieces (bishop/queen).
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            while in_bounds(rr, cc):
                piece = board[rr][cc]
                if piece is None:
                    rr += dr
                    cc += dc
                    continue
                if piece[0] == attacker_color and (piece[1] == 'B' or piece[1] == 'Q'):
                    return True
                break
        # Check king attacks.
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc):
                    piece = board[rr][cc]
                    if piece == attacker_color + 'K':
                        return True
        return False

    def is_in_check(self, board, color):
        # Locate the king and then check if that square is attacked.
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == color + 'K':
                    return self.is_square_attacked(board, r, c, 'w' if color == 'b' else 'b')
        return False

    def simulate_move(self, move, color):
        """
        Return a new board (a deep copy of self.board) with the given move applied.
        Used to test if a move leaves the king in check.
        """
        new_board = [row[:] for row in self.board]
        (r_from, c_from) = move["from"]
        (r_to, c_to) = move["to"]
        piece = new_board[r_from][c_from]
        if move["castling"]:
            new_board[r_from][c_from] = None
            new_board[r_to][c_to] = piece
            if move["castling"] == "kingside":
                if color == 'w':
                    new_board[7][7] = None
                    new_board[7][5] = 'wR'
                else:
                    new_board[0][7] = None
                    new_board[0][5] = 'bR'
            elif move["castling"] == "queenside":
                if color == 'w':
                    new_board[7][0] = None
                    new_board[7][3] = 'wR'
                else:
                    new_board[0][0] = None
                    new_board[0][3] = 'bR'
        else:
            new_board[r_from][c_from] = None
            if move["en_passant"]:
                new_board[r_to][c_to] = piece
                if color == 'w':
                    new_board[r_to + 1][c_to] = None
                else:
                    new_board[r_to - 1][c_to] = None
            else:
                new_board[r_to][c_to] = piece
            if move["promotion"]:
                new_board[r_to][c_to] = color + move["promotion"]
        return new_board

    def apply_move(self, move):
        """
        Apply a legal move to update the board, castling rights, en passant target, and turn.
        """
        (r_from, c_from) = move["from"]
        (r_to, c_to) = move["to"]
        piece = self.board[r_from][c_from]
        color = piece[0]
        if move["castling"]:
            self.board[r_from][c_from] = None
            self.board[r_to][c_to] = piece
            if move["castling"] == "kingside":
                if color == 'w':
                    self.board[7][7] = None
                    self.board[7][5] = 'wR'
                else:
                    self.board[0][7] = None
                    self.board[0][5] = 'bR'
            elif move["castling"] == "queenside":
                if color == 'w':
                    self.board[7][0] = None
                    self.board[7][3] = 'wR'
                else:
                    self.board[0][0] = None
                    self.board[0][3] = 'bR'
        else:
            self.board[r_from][c_from] = None
            if move["en_passant"]:
                self.board[r_to][c_to] = piece
                if color == 'w':
                    self.board[r_to + 1][c_to] = None
                else:
                    self.board[r_to - 1][c_to] = None
            else:
                self.board[r_to][c_to] = piece
            if move["promotion"]:
                self.board[r_to][c_to] = color + move["promotion"]

        # Update castling rights.
        if piece[1] == 'K':
            if color == 'w':
                self.castling_rights["wK"] = False
                self.castling_rights["wQ"] = False
            else:
                self.castling_rights["bK"] = False
                self.castling_rights["bQ"] = False
        if piece[1] == 'R':
            if color == 'w':
                if (r_from, c_from) == (7, 0):
                    self.castling_rights["wQ"] = False
                elif (r_from, c_from) == (7, 7):
                    self.castling_rights["wK"] = False
            else:
                if (r_from, c_from) == (0, 0):
                    self.castling_rights["bQ"] = False
                elif (r_from, c_from) == (0, 7):
                    self.castling_rights["bK"] = False
        target = None
        if not move["en_passant"] and not move["castling"]:
            target = self.board[r_to][c_to]
        if target is not None and target[1] == 'R':
            if target[0] == 'w':
                if (r_to, c_to) == (7, 0):
                    self.castling_rights["wQ"] = False
                elif (r_to, c_to) == (7, 7):
                    self.castling_rights["wK"] = False
            else:
                if (r_to, c_to) == (0, 0):
                    self.castling_rights["bQ"] = False
                elif (r_to, c_to) == (0, 7):
                    self.castling_rights["bK"] = False

        # Update en passant target.
        self.en_passant_target = None
        if piece[1] == 'P' and abs(r_to - r_from) == 2:
            ep_row = (r_from + r_to) // 2
            self.en_passant_target = (ep_row, c_from)

        # Switch turn.
        self.turn = 'b' if self.turn == 'w' else 'w'
        if self.turn == 'w':
            self.fullmove_number += 1

# --------- GUI Code using Tkinter ---------

# Unicode symbols for chess pieces.
PIECE_UNICODE = {
    "wK": "\u2654",
    "wQ": "\u2655",
    "wR": "\u2656",
    "wB": "\u2657",
    "wN": "\u2658",
    "wP": "\u2659",
    "bK": "\u265A",
    "bQ": "\u265B",
    "bR": "\u265C",
    "bB": "\u265D",
    "bN": "\u265E",
    "bP": "\u265F"
}

# Colors for the board squares.
LIGHT_COLOR = "#F0D9B5"
DARK_COLOR = "#B58863"
HIGHLIGHT_COLOR = "#DDD23B"  # Color to highlight a selected square.

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.game = ChessGame()
        self.square_size = 60
        self.board_size = self.square_size * 8

        # Create a canvas to draw the chessboard.
        self.canvas = tk.Canvas(root, width=self.board_size, height=self.board_size)
        self.canvas.pack(side=tk.TOP)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Status label to show messages and turn information.
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Helvetica", 14))
        self.status_label.pack(side=tk.TOP, pady=5)

        # Track the currently selected square (if any).
        self.selected_square = None

        self.draw_board()
        self.update_status()

    def draw_board(self):
        """Draw the board and pieces on the canvas."""
        self.canvas.delete("all")
        for r in range(8):
            for c in range(8):
                x1 = c * self.square_size
                y1 = r * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                # Alternate colors.
                if (r + c) % 2 == 0:
                    fill_color = LIGHT_COLOR
                else:
                    fill_color = DARK_COLOR
                # Highlight the selected square.
                if self.selected_square == (r, c):
                    fill_color = HIGHLIGHT_COLOR
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                piece = self.game.board[r][c]
                if piece is not None:
                    # Draw the Unicode chess piece in the center.
                    symbol = PIECE_UNICODE.get(piece, piece)
                    self.canvas.create_text(x1 + self.square_size/2, y1 + self.square_size/2,
                                            text=symbol, font=("Arial", 36))
        # Optionally, draw board coordinates.
        # (This can be extended if desired.)

    def update_status(self):
        """Update the status label with whose turn it is or game over message."""
        legal_moves = self.game.get_legal_moves(self.game.turn)
        if not legal_moves:
            if self.game.is_in_check(self.game.board, self.game.turn):
                winner = "White" if self.game.turn == 'b' else "Black"
                self.status_var.set(f"Checkmate! {winner} wins.")
                messagebox.showinfo("Game Over", f"Checkmate! {winner} wins.")
            else:
                self.status_var.set("Stalemate!")
                messagebox.showinfo("Game Over", "Stalemate!")
        else:
            turn_str = "White" if self.game.turn == 'w' else "Black"
            self.status_var.set(f"{turn_str} to move.")

    def on_canvas_click(self, event):
        """Handle click events on the board."""
        if not self.game.get_legal_moves(self.game.turn):
            return  # Game over.

        # Compute board coordinates (row, col) from the click.
        col = event.x // self.square_size
        row = event.y // self.square_size
        clicked_square = (row, col)

        # If nothing is selected yet:
        if self.selected_square is None:
            piece = self.game.board[row][col]
            if piece is not None and piece[0] == self.game.turn:
                self.selected_square = clicked_square
                self.draw_board()
            return

        # If clicking the same square, deselect.
        if self.selected_square == clicked_square:
            self.selected_square = None
            self.draw_board()
            return

        # Attempt to find a legal move from the selected square to the clicked square.
        legal_moves = self.game.get_legal_moves(self.game.turn)
        candidate_moves = []
        for move in legal_moves:
            if move["from"] == self.selected_square and move["to"] == clicked_square:
                candidate_moves.append(move)
        if candidate_moves:
            # For pawn promotion, choose queen if available.
            chosen_move = None
            for move in candidate_moves:
                if move["promotion"] is None or move["promotion"] == "Q":
                    chosen_move = move
                    break
            if chosen_move is None:
                chosen_move = candidate_moves[0]
            self.game.apply_move(chosen_move)
            self.selected_square = None
            self.draw_board()
            self.update_status()
        else:
            # If the clicked square contains a piece of the current player, change selection.
            piece = self.game.board[row][col]
            if piece is not None and piece[0] == self.game.turn:
                self.selected_square = clicked_square
                self.draw_board()
            else:
                # Otherwise, invalid move; deselect.
                self.selected_square = None
                self.draw_board()

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
