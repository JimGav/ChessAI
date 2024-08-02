from chess_game import ChessGame
import random

def randomize(cg):
	for i in range(10):
		legal_moves = cg.get_legal_moves(cg._board, cg._curr_color)
		cg._board = cg.play_move(*legal_moves[random.randint(0, len(legal_moves)-1)], cg._board, True)
		cg._curr_color = cg.flip_color(cg._curr_color)
	return cg

def test_get_avail_squares(board):
	print("------ Testing get_avail_squares ------")
	print(cg.get_avail_squares((0,0), board) == [(1,0)])
	print(cg.get_avail_squares((0,1), board) == [(2,2)])
	print(cg.get_avail_squares((0,3), board) == [(0,4)])
	print(cg.get_avail_squares((7,5), board) == [])
	print("----------------------------------------")

def test_get_piece_targets(board):
	print("------ Testing get_piece_targets ------")
	print(set(cg.get_piece_targets(board, 0,0)) == set([(1,0), (0,1),(2,0)]))
	print(set(cg.get_piece_targets(board, 7,1)) == set([(5,0), (5,2),(6,3)]))
	print(set(cg.get_piece_targets(board, 0,5)) == set([(1,4), (1,6),(2,7)]))
	print(set(cg.get_piece_targets(board, 1,1)) == set([(2,2), (2,0)]))
	print(set(cg.get_piece_targets(board, 5,6)) == set([(5,5), (5,4), (5,3), (5,7), (4,6), (3,6), (2,6), (6,6), (4,5), (6,7), (6,5), (7,4), (4,7)]))
	print("----------------------------------------")


random.seed(100)
cg = ChessGame()
cg = randomize(cg)
cg.print_board(cg._board)
test_get_avail_squares(cg._board)
test_get_piece_targets(cg._board)

