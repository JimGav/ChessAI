from tkinter import *
from copy import deepcopy
import random,sys,time

"""
TODO:
- fix castling
- fix castling under threat
- optimize performance
"""


class ChessGame:
	# Constructor
	def __init__(self, colors=["midnight blue", "gainsboro"], ai_max_move_depth=3, ai_opponent = True):
		self._colors = colors				# List of 2 colors for the gui
		self._curr_color = "white"	# Color of whoever's turn is it
		self._selected_btn = None 	# The button that is selected on the gui
		self._piece_imgs = None			# Images for each piece. create_gui will load them after root window is created
		self._ai_opponent = ai_opponent	
		self._winner = None
		self._has_moved = {"white_king": False, "black_king": False}	# Keep track if a king has moved. Used for castling 
		self._ai_max_move_depth = ai_max_move_depth	# Maximum recursion depth for minimax function => how many states ahead will the agent check
		self._board = self.create_board()	 	# Create 2d list representing the current state of self._board
		self._root_win = self.create_gui()	# Create the tkinter gui 
		self._tt = dict() # Transposition table hodling {state, minimax_val} pairs
		self._zobrist_keys = self.generate_zobrist_keys()
		self.count = 0	
		random.seed(100)
	""""""""""""" Initialization functions """""""""""""""""""
	# Returns dict {piece_name : img_for_piece_name} for all pieces
	def load_imgs(self):
		piece_imgs = {
			"white_pawn": PhotoImage(file="./images/white_pawn.png"),
			"black_pawn": PhotoImage(file="./images/black_pawn.png"),
			"white_rook": PhotoImage(file="./images/white_rook.png"),
			"black_rook": PhotoImage(file="./images/black_rook.png"),
			"white_bishop": PhotoImage(file="./images/white_bishop.png"),
			"black_bishop": PhotoImage(file="./images/black_bishop.png"),
			"white_knight": PhotoImage(file="./images/white_knight.png"),
			"black_knight": PhotoImage(file="./images/black_knight.png"),
			"white_king": PhotoImage(file="./images/white_king.png"),
			"black_king": PhotoImage(file="./images/black_king.png"),
			"white_queen": PhotoImage(file="./images/white_queen.png"),
			"black_queen": PhotoImage(file="./images/black_queen.png"),
			None: ""
			}
		return piece_imgs
	# Create 2d list representing the current state of the board
	def create_board(self):
		board = [[None for j in range(8)] for i in range(8)]
		for i in range(8):
			for j in range(8):
				if i == 1:
					board[i][j] = "white_pawn"
				elif i == 6:
					board[i][j] = "black_pawn"
				elif i == 0 and (j == 0 or j == 7):
					board[i][j] = "white_rook"
				elif i == 7 and (j == 0 or j == 7):
					board[i][j] = "black_rook"
				elif i == 0 and (j == 1 or j == 6):
					board[i][j] = "white_knight"
				elif i == 7 and (j == 1 or j == 6):
					board[i][j] = "black_knight"
				elif i == 0 and (j == 2 or j == 5):
					board[i][j] = "white_bishop"
				elif i == 7 and (j == 2 or j == 5):
					board[i][j] = "black_bishop" 
				elif i == 0 and j == 3:
					board[i][j] = "white_king"
				elif i == 7 and j == 3:
					board[i][j] = "black_king"
				elif i == 0 and j == 4:
					board[i][j] = "white_queen"
				elif i == 7 and j == 4:
					board[i][j] = "black_queen"		
		return  board
	# Create the tkinter gui window and initializes it
	def create_gui(self):
		r = Tk()
		self._piece_imgs = self.load_imgs()
		for i in range(8):
			for j in range(8):
				piece = self._board[i][j]
				b = Button(r, padx=29, pady=21, background= self._colors[1] if (i+j)%2 == 0 else self._colors[0])
				if piece != None:
					b.config(image=self._piece_imgs[piece])
				b.grid(row=i,column=j, sticky="nwes")
				b.bind('<Button-1>', self.button_clicked) 
		return r
	# Generates an 8x8 array containing 1 random int for every piece and square
	def generate_zobrist_keys(self):
		a = [[None for y in range(8)] for x in range(8)]
		for i in range(8):
			for j in range(8):
				a[i][j] = dict()
				for color in ("white", "black"):
					for key in (color + "_king", color + "_queen", color + "_pawn", color + "_rook", color + "_knight", color + "_bishop", color):
						a[i][j][key] = random.randint(0, 999999999)
		return a
	""""""""""""""""""""""""""""""""""""""""""""""""""""""""


	""""""""""""" Control functions """""""""""""""""""
	# Starts gameloop
	def play(self):
		self._root_win.mainloop()
	# Handles button click events
	def button_clicked(self, event):
		b = event.widget
		i = b.grid_info()["row"]	  
		j = b.grid_info()["column"]

		# Select button
		if self._selected_btn is None:
			if self._board[i][j] is not None and self._board[i][j][0] == self._curr_color[0]:
				self._selected_btn = b
		# Deselect button and play move if move legal
		else:
			x = self._selected_btn.grid_info()["row"]	  
			y = self._selected_btn.grid_info()["column"]
			self._selected_btn = None
			
			if self.move_legal((x, y),(i,j), self._board, self._curr_color):
				self._board = self.play_move((x, y),(i,j), self._board, True)
				self.pass_move()
				if self.in_checkmate(self._board, self._curr_color):
					self._winner = self._curr_color
					self.update_gui(winner_color = self._winner)
					return
				self.update_gui(winner_color = self._winner)
				# AI reply
				if self._ai_opponent:
					move = self.find_move(self._board, self._curr_color)	
					if self.move_legal(*move, self._board, self._curr_color):
						self._board = self.play_move(*move, self._board, True) 
						self.pass_move()
						
						if self.in_checkmate(self._board, self._curr_color):
							self._winner = self._curr_color

		self.update_gui(winner_color = self._winner)
	# Prints given board on console 
	def print_board(self, board):
		for i in range(8):
			print(33*"=")
			for j in range(8):
				if board[i][j] is None:
					sys.stdout.write("|   ")
				else:
					if board[i][j] == "white_knight" or board[i][j] == "black_knight":
						sys.stdout.write("|"+board[i][j].split("_")[0][0] + "_" + "n")
					else:
						sys.stdout.write("|"+board[i][j].split("_")[0][0] + "_" + board[i][j].split("_")[1][0])
			print("|")
		print(33*"=")
	# Updates gui to match self._board
	def update_gui(self, winner_color=None):
		for btn in self._root_win.grid_slaves():
			i = btn.grid_info()["row"]	  
			j = btn.grid_info()["column"]
			piece = self._board[i][j]
			btn.config(image=self._piece_imgs[piece])
			if btn == self._selected_btn:
				btn.config(background="yellow")
			else:
				btn.config(background=self._colors[1] if (i+j)%2 == 0 else self._colors[0])

			# Color of checkmated king = red
			if winner_color and piece == winner_color + "_king":
				btn.config(background = "red")
		self._root_win.update_idletasks()	# Refresh tkinter window
	# Flips self._curr_color
	def pass_move(self):
		if self._curr_color == "white":
			self._curr_color = "black"
		else:
			self._curr_color = "white"
	# Return a new board after playing the move on given board
	def play_move(self, start:tuple, target:tuple, board, main_call = False):		# main_call ->  board == self._board
		new_board = deepcopy(board)
		piece = board[start[0]][start[1]]
		color = self.get_color(board, start[0] ,start[1])

		if piece == color + "_king" and not self._has_moved[color + "_king"] and abs(target[1] - start[1]) > 1:
			# Castling
			x = 0 if color == "white" else 7
			if target == (x,0):	# O-O
				new_board[x][1] = color + "_king"
				new_board[x][3] = None
				new_board[x][0] = None
				new_board[x][2] = color + "_rook"
			elif target == (x, 7): # O-O-O
				new_board[x][5] = color + "_king"
				new_board[x][3] = None
				new_board[x][7] = None
				new_board[x][4] = color + "_rook"
			if main_call:
				self._has_moved[color + "_king"] = True
		else:
			# Normal move
			new_board[target[0]][target[1]] = new_board[start[0]][start[1]]
			new_board[start[0]][start[1]] = None	

		# Handle pawn promotions
		if piece == "white_pawn" and target[0] == 7:
			new_board[target[0]][target[1]] = "white_queen"
		if piece == "black_pawn" and target[0] == 0:
			new_board[target[0]][target[1]] = "black_queen"

		return new_board
	""""""""""""""""""""""""""""""""""""""""""""""""""

	
	""""""""""""" Helper functions """""""""""""""""""
	# Finds the king's position of given color
	def king_pos(self, board:list, color:str):
		for i in range(8):
			for j in range(8):
				if board[i][j] == color + "_king":
					return i,j
		return None
	# Returns whether king of given color is in check
	def in_check(self, board, color:str):		
			enemy_color = self.flip_color(color)
			return self.king_pos(board, color) in self.get_all_targets(board, enemy_color)
	# Returns whether king of given color is in checkmate
	def in_checkmate(self, board, color:str):	
		return len(self.get_legal_moves(board, color)) == 0
	# Returns whether given position is inside the bounds of chess board
	def in_bounds(self, i, j):
		return i >= 0 and j >= 0 and i < 8 and j < 8
	# Returns the number of points the given color has
	def get_points(self, board, color):
		points = 0
		for i in range(8):
			for j in range(8):
				piece = board[i][j]
				if piece is None:
					continue
				if piece == color + "_pawn":
					points += 1
				if piece == color + "_knight" or piece == color + "_bishop":
					points += 3
				if piece == color + "_rook":
					points += 5
				if piece == color + "_queen":
					points += 9
		
		return points
	# Returns the color of the piece that occupies given square
	def get_color(self, board, i, j):
		piece = board[i][j]
		if piece is None:
			return None
		return piece.split("_")[0]
	# Returns the other color
	def flip_color(self, color):
		if color == "white":
			return "black"
		else:
			return "white"
	# Returns how many center squares the given piece occupies
	def center_occupation(self, board, i, j):
		targets = self.get_piece_targets(board, i, j)
		color = self.get_color(board, i ,j)
		count = 0
		if color == "white":
			center_sqrs = ((4,3),(4,4))
		else:
			center_sqrs = ((3,4),(3,3))
		for square in center_sqrs:
			if square in targets:
				count += 1
		return count
	""""""""""""""""""""""""""""""""""""""""""""""""""


	""""""""""""" Chess rule functions """""""""""""""""""
	# Returns all legal moves in the current position
	def get_legal_moves(self, board, color):
		moves = []
		for i in range(8):
			for j in range(8):
				if board[i][j] is None:
					continue
				if board[i][j][0] == color[0]:
					for square in self.get_avail_squares((i,j),board):
						move = [(i,j), square]
						if self.move_legal(*move, board, color):
							moves.append(move)
		return moves
	# Check if given move is legal.
	def move_legal(self, start:tuple, end:tuple, board, color):
		# Validate bounds
		if not self.in_bounds(*start) or not self.in_bounds(*end):
			return False
		# Validate piece not None
		if board[start[0]][start[1]] is None:
			return False
		# Validate legal move
		if not end in self.get_avail_squares(start, board):
			return False
		t_board = self.play_move(start, end, board, False)
		if self.in_check(t_board, color):
			return False
		
		return True
	# Returns all available squares a piece can be moved to from given start position
	def get_avail_squares(self, start, board):
		i,j = start
		piece = board[i][j]
		color = self.get_color(board, i ,j)
		avail_squares = []

		if piece == "white_pawn":
			if self.in_bounds(i+1,j) and board[i+1][j] is None:
				avail_squares.append((i+1,j))
				if i == 1 and board[i+2][j] is None:
					avail_squares.append((i+2,j))
			for target in self.get_piece_targets(board, i, j):
				if not self.in_bounds(target[0], target[1]):
					continue
				t_piece = board[target[0]][target[1]]
				if t_piece is None:
					continue
				if t_piece[0] != color[0]:
					avail_squares.append((target[0], target[1]))
			return avail_squares
		elif piece == "black_pawn":
			if self.in_bounds(i-1,j) and board[i-1][j] is None:
				avail_squares.append((i-1,j))
				if i == 6 and board[i-2][j] is None:
					avail_squares.append((i-2,j))
			for target in self.get_piece_targets(board, i, j):
				if not self.in_bounds(target[0], target[1]):
					continue
				t_piece = board[target[0]][target[1]]
				if t_piece is None:
					continue
				if t_piece[0] != color[0]:
					avail_squares.append((target[0], target[1]))
			return avail_squares
		elif piece == color + "_king":
			# Castling
			if not self._has_moved[color + "_king"]:
				x = 0 if color == "white" else 7
				# Short Castling
				f = True
				for y in range(j-1, j-3, -1):
					if self.in_bounds(x,y) and board[x][y] != None: 
						f = False
						break
				if f and board[x][j-3] == color + "_rook":	
					avail_squares.append((x, j-3))
				# Long Castling
				f = True
				for y in range(j+1, j+4):
					if self.in_bounds(x,y) and board[x][y] != None: 
						f = False
						break
				if f and board[x][j+4] == color + "_rook":	
					avail_squares.append((x, j+4))
		
		targets = self.get_piece_targets(board, i ,j)
		for target in targets:
			if target is None or self.get_color(board, *target) != self.get_color(board, *start):
				avail_squares.append(target)

		return avail_squares
	# Returns all the squares targeted from given piece
	def get_piece_targets(self, board, i, j):
		piece = board[i][j]
		color = self.get_color(board, i , j)

		sq = []
		if piece == "white_pawn":
			sq.append((i+1, j-1))
			sq.append((i+1, j+1))
		if piece == "black_pawn":
			sq.append((i-1, j-1))
			sq.append((i-1,j+1))
		if piece == color + "_knight":
			for square in [(i-1,j-2),(i-2,j-1),(i+1,j-2),(i+2,j-1),(i-1,j+2),(i-2,j+1),(i+1,j+2),(i+2,j+1)]:
				if self.in_bounds(*square):
					sq.append(square)
		if piece == color + "_queen" or piece == color + "_bishop":
			# Top right diagonal
			for r in range(1,8):
				if not self.in_bounds(i+r,j+r):
					break
				sq.append((i+r,j+r))
				if  board[i+r][j+r] is not None:
					break
			# Top left diagonal
			for r in range(1,8):
				if not self.in_bounds(i+r,j-r):
					break
				sq.append((i+r,j-r))
				if  board[i+r][j-r] is not None:
					break
			# Bottom right diagonal
			for r in range(1,8):
				if not self.in_bounds(i-r,j+r):
					break
				sq.append((i-r,j+r))
				if  board[i-r][j+r] is not None:
					break
			# Bottom left diagonal
			for r in range(1,8):
				if not self.in_bounds(i-r,j-r):
					break
				sq.append((i-r,j-r))
				if  board[i-r][j-r] is not None:
					break
		if piece == color + "_queen" or piece == color + "_rook":
			# Top
			for r in range(1,8):		
				if not self.in_bounds(i+r,j):
					break
				sq.append((i+r,j))
				if  board[i+r][j] is not None:
					break
			# Left
			for r in range(1,8):
				if not self.in_bounds(i,j-r):
					break
				sq.append((i,j-r))
				if  board[i][j-r] is not None:
					break
			# Right
			for r in range(1,8):
				if not self.in_bounds(i,j+r):
					break
				sq.append((i,j+r))
				if  board[i][j+r] is not None:
					break
			# Bottom 
			for r in range(1,8):
				if not self.in_bounds(i-r,j):
					break
				sq.append((i-r,j))
				if  board[i-r][j] is not None:
					break
		if piece == color + "_king":
			for x in range(-1,2):
				for y in range(-1,2):
					if not self.in_bounds(i+x,j+y):
						continue
					sq.append((i+x,j+y))		

		return sq
	# Returns a list of all squares that are targeted by given color
	def get_all_targets(self, board, color):
		targets = []
		for i in range(8):
				for j in range(8):
					if board[i][j] != None and board[i][j][0] == color[0]:
						targets.extend(self.get_piece_targets(board, i,j))
							
		return targets
	""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	

# Minimax modeling: State = [board, curr_color], GoalState = checkmate, get_successors()
	""""""""""""" AI agent functions """""""""""""""""""
	# Finds move for given color
	def find_move(self, board, color:str):
		min_minimax = float("inf")
		best_move = None
		legal_moves = self.get_legal_moves(board, color)
		for move in legal_moves:
			s = [self.play_move(*move, board), "white"]
			m = self.minimax(s, 0, float("-inf"), float("inf"), color=="black")
			if m < min_minimax:
				min_minimax = m
				best_move = move
		print(self.count)
		return best_move
	# Finds the minimax value for given state
	def minimax(self, state, depth, alpha, beta, maximizer):
		self.count += 1
		board, color = state
		depth += 1

		# Before calculating minimax, look if it has already been calculated
		state_hash = self.zobrist_hash(board, color)
		if state_hash in self._tt:
			return self._tt[state_hash]

		if self.in_checkmate(board, "black"):
			return float("inf")
		elif self.in_checkmate(board, "white"):
			return float("-inf")
		if depth == self._ai_max_move_depth:
			return self.eval(state)
		
		if maximizer:
			bestVal = float("-inf") 
			for successor in self.get_successors(state):
				value = self.minimax(successor, depth, alpha, beta, False)
				bestVal = max( bestVal, value) 
				alpha = max( alpha, bestVal)
				if beta <= alpha:
					break
			self._tt[state_hash] = bestVal
			return bestVal
		else:
			bestVal = float("inf") 
			for successor in self.get_successors(state):
				value = self.minimax(successor, depth, alpha, beta, True)
				bestVal = min( bestVal, value) 
				beta = min( beta, bestVal)
				if beta <= alpha:
					break
			self._tt[state_hash] = bestVal
			return bestVal
	# Get successor states of given state
	def get_successors(self, state):
		board, color = state

		successors = []
		for move in self.get_legal_moves(board, color):
			s = [self.play_move(move[0],move[1], board)]
			if color == "white":
				s.append("black")
			else:
				s.append("white")
			successors.append(s)

		return successors
	# Evaluates a given state
	def eval(self, state):
		board, color = state
		c = self.eval_points(board, color) * 10000
		c2 = self.eval_center(board, color) * 10
		c3 = self.eval_mobile(board, color) * 0.1

		e =  c + c2 + c3
		return e
	# Evaluates state based on how many points each side has
	def eval_points(self, board, color):
		return self.get_points(board, "white")-self.get_points(board, "black")
	# Evaluates state based on how much is side holds the center
	def eval_center(self, board, color):
		w = 0
		b = 0
		for i in range(8):
			for j in range(8):
				piece = board[i][j]
				if piece is None:
					continue
				if self.get_color(board, i, j) == "white":
					w += self.center_occupation(board , i ,j)
				else:
					b += self.center_occupation(board , i ,j)

		return w-b
	# Evaluates state based on how mobile each side's pieces are
	def eval_mobile(self, board, color):
		w = 0
		b = 0
		for i in range(8):
			for j in range(8):
				piece = board[i][j]
				c = self.get_color(board, i, j)
				if piece is None or piece == color + "_king" or piece == color + "_pawn" or piece == color + "rook":
					continue
				if piece == "white_queen":
					w += len(self.get_piece_targets(board, i, j))/10
				elif piece == "black_queen":
					b += len(self.get_piece_targets(board, i, j))/10
				else:
					if c == "white":
						w += len(self.get_piece_targets(board, i, j))
					else:
						b += len(self.get_piece_targets(board, i, j))
		
		return w-b
	# Zobrist hashes a state
	def zobrist_hash(self, board, color):
		hash = None
		for i in range(8):
			for j in range(8):
				if board[i][j] is None:
					continue
				piece_hash_val = self._zobrist_keys[i][j][board[i][j]]
				if hash is None:
					hash = piece_hash_val
				else:
					hash = hash ^ piece_hash_val
		hash = hash ^ self._zobrist_keys[0][0][color]
		return hash
	""""""""""""""""""""""""""""""""""""""""""""""""""""""""




