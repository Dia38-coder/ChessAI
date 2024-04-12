import tkinter as tk  # Import the tkinter module as tk for easy access
from tkinter import messagebox  # Import the messagebox submodule from tkinter
import chess  # Import the chess module for handling chess logic
import chess.engine  # Import the chess.engine module for interacting with chess engines
import random  # Import the random module for generating random moves


class ChessGameGUI:
    def __init__(self, root, mode, ai_difficulty):
        self.root = root  # Store the root Tkinter window
        self.mode = mode  # Store the selected mode (AI or friend)
        self.ai_difficulty = ai_difficulty  # Store the AI difficulty level
        self.board = chess.Board()  # Create a new chess board
        if mode == "AI":
            # Open the Stockfish chess engine if AI mode is selected
            self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        else:
            self.engine = None  # Set engine to None for friend mode

        # Create a canvas widget to draw the chess board
        self.board_canvas = tk.Canvas(root, width=400, height=400)
        self.board_canvas.pack()

        # Draw the initial chess board and pieces
        self.draw_board()
        self.draw_pieces()

        # Bind the on_click method to mouse clicks on the board canvas
        self.board_canvas.bind("<Button-1>", self.on_click)

        self.game_over = False  # Flag to track if the game is over
        self.selected_square = None  # Track the selected square for moves

        # Add Play Again button
        self.play_again_button = tk.Button(root, text="Play Again", command=self.play_again)
        self.play_again_button.pack(side=tk.LEFT, padx=5)  # Align button to the left with padding
        self.play_again_button.configure(bg='lightblue')  # Set button color

        # Add Undo button
        self.undo_button = tk.Button(root, text="Undo", command=self.undo_move)
        self.undo_button.pack(side=tk.LEFT, padx=5)  # Align button to the left with padding
        self.undo_button.configure(bg='lightblue')  # Set button color

        # Add Exit Game button
        self.exit_button = tk.Button(root, text="Exit Game", command=self.exit_game)
        self.exit_button.pack(side=tk.LEFT, padx=5)  # Align button to the left with padding
        self.exit_button.configure(bg='lightblue')  # Set button color

        # If AI mode and it's AI's turn, make the first move
        if mode == "AI" and self.board.turn == chess.BLACK:
            self.computer_move()

    # Method to draw the initial chess board
    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = "brown" if (row + col) % 2 == 0 else "green"
                x0, y0 = col * 50, row * 50
                x1, y1 = x0 + 50, y0 + 50
                self.board_canvas.create_rectangle(x0, y0, x1, y1, fill=color)

    # Method to draw the initial chess pieces on the board
    def draw_pieces(self):
        # Define symbols for each chess piece
        self.piece_symbols = {'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
                              'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'}
        self.piece_images = {}  # Dictionary to store piece images on canvas

        # Loop through each square on the board
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)  # Get the piece at the current square
            if piece:
                row, col = chess.square_rank(square), chess.square_file(square)
                x, y = col * 50 + 25, (7 - row) * 50 + 25  # Calculate coordinates for placing the piece
                symbol = self.piece_symbols[piece.symbol()]  # Get symbol for the piece
                self.piece_images[square] = self.board_canvas.create_text(x, y, text=symbol, font=("Arial", 24))

    # Method to handle mouse clicks on the board
    def on_click(self, event):
        if self.game_over:
            return

        square = self.get_square(event)  # Get the square clicked on the board
        if square:
            if self.selected_square is not None:
                move = chess.Move(self.selected_square, square)  # Create a move from selected square to clicked square
                if move in self.board.legal_moves:  # Check if the move is legal
                    self.board.push(move)  # Make the move on the board
                    self.board_canvas.delete("highlight")  # Remove highlighting
                    self.draw_pieces()  # Redraw the pieces on the board
                    self.selected_square = None  # Reset selected square
                    if self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_insufficient_material():
                        # Check if the game is over and display result if true
                        self.game_over = True
                        self.display_game_result()
                    elif self.mode == "AI":
                        self.computer_move()  # If AI mode, let the AI make a move
                else:
                    self.board_canvas.delete("highlight")  # Remove highlighting
                    self.selected_square = None  # Reset selected square
            else:
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn:
                    self.highlight_valid_moves(square)  # Highlight valid moves for the selected piece
                    self.selected_square = square  # Set selected square

    # Method to get the square clicked on the board
    def get_square(self, event):
        col = event.x // 50  # Calculate column number based on x-coordinate
        row = 7 - (event.y // 50)  # Calculate row number based on y-coordinate
        if 0 <= row < 8 and 0 <= col < 8:
            return chess.square(col, row)  # Return the corresponding square
        return None

    # Method to highlight valid moves for a selected piece
    def highlight_valid_moves(self, square):
        for move in self.board.legal_moves:
            if move.from_square == square:
                row, col = chess.square_rank(move.to_square), chess.square_file(move.to_square)
                x, y = col * 50 + 25, (7 - row) * 50 + 25  # Calculate coordinates for highlighting
                self.board_canvas.create_oval(x - 15, y - 15, x + 15, y + 15, outline="green", width=2,
                                              tags="highlight")


    # Method to handle playing the game again
    def play_again(self):
        self.board = chess.Board()  # Create a new chess board
        self.board_canvas.delete("all")  # Clear the board canvas
        self.draw_board()  # Redraw the board
        self.draw_pieces()  # Redraw the pieces
        self.game_over = False  # Reset game over flag
        self.selected_square = None  # Reset selected square

    # Method to undo the last move
    def undo_move(self):
        if len(self.board.move_stack) > 0:
            self.board.pop()  # Remove the last move from the move stack
            self.board_canvas.delete("all")  # Clear the board canvas
            self.draw_board()  # Redraw the board
            self.draw_pieces()  # Redraw the pieces
            self.selected_square = None  # Reset selected square

    # Method to display the game result
    def display_game_result(self):
        result = self.board.result()  # Get the result of the game
        if result == "1-0":
            message = "White wins!"
        elif result == "0-1":
            message = "Black wins!"
        else:
            message = "Draw!"

        messagebox.showinfo("Game Over", message)  # Show game over message box

    # Method to handle the AI making a move
    def computer_move(self):
        if self.ai_difficulty == "easy":
            # Make the AI choose a random move to allow the player to win
            legal_moves = list(self.board.legal_moves)
            random_move = random.choice(legal_moves)
            self.board.push(random_move)
        elif self.ai_difficulty == "medium":
            # Make the AI play a random move after a few moves
            if random.random() < 0.5:  # 50% chance to make a random move
                legal_moves = list(self.board.legal_moves)
                random_move = random.choice(legal_moves)
                self.board.push(random_move)
            else:
                result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
                move = result.move
                self.board.push(move)
        else:
            # Make the AI play normally
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
            move = result.move
            self.board.push(move)

        self.board_canvas.delete("all")  # Clear the board canvas
        self.draw_board()  # Redraw the board
        self.draw_pieces()  # Redraw the pieces

        if self.board.is_game_over():
            self.game_over = True
            self.display_game_result()

    # Method to handle exiting the game
    def exit_game(self):
        self.root.destroy()  # Destroy the Tkinter window
        messagebox.showinfo("Exit", "Thanks for playing!")  # Show exit message box

def main():
    root = tk.Tk()  # Create the main Tkinter window
    root.title("Chess Game")  # Set the title of the window

    mode_selection = messagebox.askquestion("Mode Selection", "Do you want to play with a friend?")

    if mode_selection == "yes":
        mode = "friend"
        ai_difficulty = None  # For friend mode, set AI difficulty to None
    else:
        skill_level = messagebox.askquestion("Skill Level", "Are you a beginner?")
        if skill_level == "yes":
            mode = "AI"
            ai_difficulty = "easy"  # Set AI difficulty to easy for beginners
        else:
            skill_level = messagebox.askquestion("Skill Level", "Are you an intermediate?")
            if skill_level == "yes":
                mode = "AI"
                ai_difficulty = "medium"  # Set AI difficulty to medium for intermediate players
            else:
                mode = "AI"
                ai_difficulty = "hard"  # Set AI difficulty to hard for pro players

    ChessGameGUI(root, mode, ai_difficulty)  # Create an instance of ChessGameGUI
    root.mainloop()  # Start the Tkinter event loop

if __name__ == "__main__":
    main()  # Call the main function when the script is executed
