from tkinter import *
import random

class ChessGame:
	# Constructor
	def __init__(self, colors=["midnight blue", "gainsboro"]):
		self._colors = colors				# list of 2 colors for the gui  self._board
		self._curr_color = "white"	# color of the current side's turn
		self._selected_btn = None 	# The button that is selected on the gui
		self._piece_imgs = None			# create_gui will load them after root window is created
		self._board = self.create_board()	 	# Create 2d list representing the current state of the  self._board
		self._root_win = self.create_gui()	# Create the tkinter gui  self._board 

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

	# Create 2d list representing the current state of the  self._board
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

	# Create the tkinter gui  self._board 
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

	# Selects the button that triggers click event
	def button_clicked(self, event):
		b = event.widget
		i = b.grid_info()["row"]	  
		j = b.grid_info()["column"]
		
		# Select button
		if self._selected_btn is None:
			if self._board[i][j] is not None and self._board[i][j][0] == self._curr_color[0]:
				self._selected_btn = b
		# Deselect button and play move if move valid
		else:
			x = self._selected_btn.grid_info()["row"]	  
			y = self._selected_btn.grid_info()["column"]
			self._selected_btn = None
			if self.move_valid((x, y),(i,j)):
				self.play_move((x, y),(i,j))
				self.pass_move()
				
		self.update_gui()

	# Updates gui to match the  self._board
	def update_gui(self):
		for btn in self._root_win.grid_slaves():
			i = btn.grid_info()["row"]	  
			j = btn.grid_info()["column"]
			piece = self._board[i][j]
			btn.config(image=self._piece_imgs[piece])
			if btn == self._selected_btn:
				btn.config(background="yellow")
			else:
				btn.config(background=self._colors[1] if (i+j)%2 == 0 else self._colors[0])

	# Play the move on  self._board. If move is illegal return False
	def play_move(self, start:tuple, target:tuple):
		self._board[target[0]][target[1]] = self._board[start[0]][start[1]]
		self._board[start[0]][start[1]] = None	

	# Passes move to the other color by flipping self._curr_color
	def pass_move(self):
		if self._curr_color == "white":
			self._curr_color = "black"
		else:
			self._curr_color = "white"

	# Finds the position of given piece
	def find_pos(self, board:list, piece:str):
		for i in range(8):
			for j in range(8):
				if board[i][j] == piece:
					return i,j
		return None

	###################### Game rules functions	######################

	# Check if given move is valid. Correct color, legal etc
	# Every validation happens here. get_avail_squares just returns the moves according to rules
	def move_valid(self, start:tuple, target:tuple):
		# Validate bounds
		if not self.in_bounds(*start) or not self.in_bounds(*target):
			return False
		# Validate piece not None
		if self._board[start[0]][start[1]] is None:
			return False
		# Validate move in correct turn
		if self._board[start[0]][start[1]][0] != self._curr_color[0]:
			return False
		# Validate legal move
		if not target in self.get_avail_squares(start, self._board) or self.illegal_move(start, target):
			return False
		return True
	
	def get_avail_squares(self, start, board):
		i,j = start
		avail_targets = set()

		# white pawns
		if  board[i][j] == "white_pawn":
			if  board[i+1][j] is None:
				avail_targets.add((i+1,j))
			if i == 1 and  board[i+2][j] is None and  board[i+1][j] is None:
				avail_targets.add((i+2,j))
			if j < 7 and  board[i+1][j+1] is not None and board[i+1][j+1][0] == "b":
				avail_targets.add((i+1,j+1))
			if j > 0 and  board[i+1][j-1] is not None and  board[i+1][j-1][0] == "b":
				avail_targets.add((i+1,j-1))
			if i == 7:
				board[i][j] = "white_queen"
	# black pawns
		if  board[i][j] == "black_pawn":
			if  board[i-1][j] is None:
				avail_targets.add((i-1,j))
			if i == 6 and  board[i-2][j] is None  and  board[i-1][j] is None:
				avail_targets.add((i-2,j))
			if j < 7 and  board[i-1][j+1] is not None and  board[i-1][j+1][0] == "w":
				avail_targets.add((i-1,j+1))
			if j > 0 and  board[i-1][j-1] is not None and  board[i-1][j-1][0] == "w":
				avail_targets.add((i-1,j-1))
			if i == 0:
				board[i][j] = "black_queen"
		# knights
		if  board[i][j] == "white_knight" or  board[i][j] == "black_knight":
			for square in [(i-1,j-2),(i-2,j-1),(i+1,j-2),(i+2,j-1),(i-1,j+2),(i-2,j+1),(i+1,j+2),(i+2,j+1)]:
				if self.in_bounds(*square) and (board[square[0]][square[1]] is None or  board[square[0]][square[1]][0] !=  board[i][j][0]):
					avail_targets.add(square)
		# bishops
		if  board[i][j] in ("white_bishop", "black_bishop","white_queen","black_queen"):
			# Top right diagonal
			for r in range(1,8):
				if not self.in_bounds(i+r,j+r):
					break
				if  board[i+r][j+r] is None or  board[i+r][j+r][0] !=  board[i][j][0]:
					avail_targets.add((i+r,j+r))
				if  board[i+r][j+r] is not None:
					break
			# Top left diagonal
			for r in range(1,8):
				if not self.in_bounds(i+r,j-r):
					break
				if  board[i+r][j-r] is None or  board[i+r][j-r][0] !=  board[i][j][0]:
					avail_targets.add((i+r,j-r))
				if  board[i+r][j-r] is not None:
					break
			# Bottom right diagonal
			for r in range(1,8):
				if not self.in_bounds(i-r,j+r):
					break
				if  board[i-r][j+r] is None or  board[i-r][j+r][0] !=  board[i][j][0]:
					avail_targets.add((i-r,j+r))
				if  board[i-r][j+r] is not None:
					break
			# Bottom left diagonal
			for r in range(1,8):
				if not self.in_bounds(i-r,j-r):
					break
				if  board[i-r][j-r] is None or  board[i-r][j-r][0] !=  board[i][j][0]:
					avail_targets.add((i-r,j-r))
				if  board[i-r][j-r] is not None:
					break
		# rooks
		if  board[i][j] in ("white_rook", "black_rook","white_queen","black_queen"):
			# Top 
			for r in range(1,8):
				if not self.in_bounds(i+r,j):
					break
				if  board[i+r][j] is None or  board[i+r][j][0] !=  board[i][j][0]:
					avail_targets.add((i+r,j))
				if  board[i+r][j] is not None:
					break
			# Left
			for r in range(1,8):
				if not self.in_bounds(i,j-r):
					break
				if  board[i][j-r] is None or  board[i][j-r][0] !=  board[i][j][0]:
					avail_targets.add((i,j-r))
				if  board[i][j-r] is not None:
					break
			# Right
			for r in range(1,8):
				if not self.in_bounds(i,j+r):
					break
				if  board[i][j+r] is None or  board[i][j+r][0] !=  board[i][j][0]:
					avail_targets.add((i,j+r))
				if  board[i][j+r] is not None:
					break
			# Bottom 
			for r in range(1,8):
				if not self.in_bounds(i-r,j):
					break
				if  board[i-r][j] is None or  board[i-r][j][0] !=  board[i][j][0]:
					avail_targets.add((i-r,j))
				if  board[i-r][j] is not None:
					break
		# King #todo: add castling 
		if  board[i][j] == "white_king" or  board[i][j] == "black_king":
			for x in range(-1,2):
				for y in range(-1,2):
					if not self.in_bounds(i+x,j+y):
						continue
					if  board[i+x][j+y] is None or  board[i+x][j+y][0] !=  board[i][j][0]:
						avail_targets.add((i+x,j+y))				

		return avail_targets
	
	def in_bounds(self, i, j):
		return i >= 0 and j >=0 and i < 8 and j < 8
	
	# Checks if a move is illegal by seeing if king is in check after playing the move
	def illegal_move(self, start, target):
		t_board = [[*row] for row in self._board] # temp board to play the move. We do not want to change the actual board
		# Play the move
		t_board[target[0]][target[1]] = t_board[start[0]][start[1]]
		t_board[start[0]][start[1]] = None	

		if self.in_check(t_board) == 1 and self._curr_color == "white":
			return True
		if self.in_check(t_board) == -1 and self._curr_color == "black":
			return True
		return False

	# Returns 1 if white king in check, -1 if black in check, 0 if none
	def in_check(self, board):		
		w_targets = set()
		for i in range(8):
			for j in range(8):
				if board[i][j] != None and board[i][j][0] == "w":
					w_targets = w_targets.union(self.get_avail_squares((i,j), board))
		b_targets = set()
		for i in range(8):
			for j in range(8):
				if board[i][j] != None and board[i][j][0] == "b":
					b_targets = b_targets.union(self.get_avail_squares((i,j), board))

		print(self.find_pos(board, "white_king"), b_targets)
		if self.find_pos(board, "white_king") in b_targets:
			print("check white")
			return 1
		if self.find_pos(board, "black_king") in w_targets:
			print("check b")
			return -1

		return 0

	##################################################################

	# Starts gameloop
	def play(self):
		self._root_win.mainloop()

	