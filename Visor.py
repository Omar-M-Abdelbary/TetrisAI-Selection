# from tkinter import *
# from TetrisSIE import TetrisEnv
# import pygame 

# class BoardVision:
#     Actv = False
#     def __init__(self):
#         label_rows = []
#         self.window = Tk()
#         self.activate_bgm()
#         for i in range(TetrisEnv.MAX_TETRIS_ROWS + 4):
#             label_cols = []
#             for j in range(TetrisEnv.MAX_TETRIS_COLS):
#                 label = Label(self.window, bg='white', width=5, height=2)
#                 label.grid(row=i, column=j)
#                 label_cols.append(label)
#             label_rows.append(label_cols)
#         self.label_rows = label_rows

#     def update_board(self, board):

#         for i in range(TetrisEnv.MAX_TETRIS_ROWS + 4):
#             for j in range(TetrisEnv.MAX_TETRIS_COLS):
#                 if board[i][j] > 0:
#                     self.label_rows[i][j].config(bg='black')
#                 elif i < TetrisEnv.GAMEOVER_ROWS:
#                     if i & 1 == 1:
#                         self.label_rows[i][j].config(bg='cyan')
#                     else:
#                         self.label_rows[i][j].config(bg='blue')
#                 else:
#                     self.label_rows[i][j].config(bg='white')

#         self.window.update()

#     def close(self):
#         self.window.destroy()


























































#         # nothing to see here, go up

























#     main_sound = None
#     def activate_bgm(self):

#         if BoardVision.Actv:
#             return
#         try:
#              # just pip install it, conda fails for some reasons
#             pygame.init()
#             pygame.mixer.init()
#             sound = pygame.mixer.Sound('./Visor_files/Tetris_theme.ogg')
#             sound.set_volume(0.2)  # it is loud, 0.4 is -3.98 dB, so I will go with ~ -7 which is 0.2
#             sound.play(-1)
#             BoardVision.main_sound = sound
#             BoardVision.Actv = True
#         except ImportError or ModuleNotFoundError:
#             print(' You can act like it is playing... ')
#     def stop(self):
#         if BoardVision.Actv:
#             BoardVision.Actv = False
#             BoardVision.main_sound.stop()
import random
import numpy as np
from random import Random


def condensed_print(matrix):
    for i in matrix:
        for j in i:
            print(j, end='')
        print()


def print_all_forms():
    for piece in TetrisEnv.Pieces:
        print(piece + ":")
        print('---')
        condensed_print(TetrisEnv.Pieces[piece])
        print('#')
        condensed_print(np.rot90(TetrisEnv.Pieces[piece], axes=(1, 0)))
        print('#')
        condensed_print(np.rot90(TetrisEnv.Pieces[piece], 2, axes=(1, 0)))
        print('#')
        condensed_print(np.rot90(TetrisEnv.Pieces[piece], 3, axes=(1, 0)))
        print('---')
        print()


class TetrisEnv:
    SCORE_PIXEL = 1
    SCORE_SINGLE = 40 * 10
    SCORE_DOUBLE = 100 * 10
    SCORE_TRIPLE = 300 * 10
    SCORE_TETRIS = 1200 * 10
    MAX_TETRIS_ROWS = 20
    GAMEOVER_ROWS = 4
    TOTAL_ROWS = MAX_TETRIS_ROWS + GAMEOVER_ROWS
    MAX_TETRIS_COLS = 10
    GAMEOVER_PENALTY = -1000
    TETRIS_GRID = (TOTAL_ROWS, MAX_TETRIS_COLS)
    TETRIS_PIECES = ['O', 'I', 'S', 'Z', 'T', 'L', 'J']
    # Note, pieces are rotated clockwise
    Pieces = {'O': np.ones((2, 2), dtype=np.byte),
              'I': np.ones((4, 1), dtype=np.byte),
              'S': np.array([[0, 1, 1], [1, 1, 0]], dtype=np.byte),
              'Z': np.array([[1, 1, 0], [0, 1, 1]], dtype=np.byte),
              'T': np.array([[1, 1, 1], [0, 1, 0]], dtype=np.byte),
              'L': np.array([[1, 0], [1, 0], [1, 1]], dtype=np.byte),
              'J': np.array([[0, 1], [0, 1], [1, 1]], dtype=np.byte),
              }
    '''
    I:   S:      Z:      T:
      1      1 1    1 1     1 1 1
      1    1 1        1 1     1
      1
      1
    L:      J:      O:
      1        1      1 1
      1        1      1 1
      1 1    1 1
     last one is utf
    '''

    def _init_(self):
        self.RNG = Random()  # independent RNG
        self.default_seed = 17  # default seed is IT
        self.__restart()

    def __restart(self):
        self.RNG.seed(self.default_seed)
        self.board = np.zeros(self.TETRIS_GRID, dtype=np.byte)
        self.current_piece = self.RNG.choice(self.TETRIS_PIECES)
        self.next_piece = self.RNG.choice(self.TETRIS_PIECES)
        self.score = 0

    def __gen_next_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.RNG.choice(self.TETRIS_PIECES)

    def set_seed(self, seed_value):
        self.default_seed = seed_value

    def get_status(self):
        return self.board.copy(), self.current_piece, self.next_piece

    # while can move down piece, move it down (note to restrict col to rotation max)
    # which is COLS-1 - (piece width in cur rotation -1) or cancel both -1s utf-8 #
    # check if move down, row++, if not, print piece on last row, col
    def __get_score(self, value):
        if value == 1:
            return TetrisEnv.SCORE_SINGLE
        if value == 2:
            return TetrisEnv.SCORE_DOUBLE
        if value == 3:
            return TetrisEnv.SCORE_TRIPLE
        if value == 4:
            return TetrisEnv.SCORE_TETRIS
        return 0
    def __collapse_rows(self, board):
        start_collapse = -1
        for row, i in zip(board, range(TetrisEnv.TOTAL_ROWS)):
            if np.sum(row) == TetrisEnv.MAX_TETRIS_COLS:
                start_collapse = i
                break
        if start_collapse == -1:
            return 0, board
        end_collapse = start_collapse + 1
        while end_collapse < TetrisEnv.TOTAL_ROWS:
            if np.sum(board[end_collapse]) == TetrisEnv.MAX_TETRIS_COLS:
                end_collapse += 1
            else:
                break
        new_board = np.delete(board, slice(start_collapse, end_collapse), axis=0)  # now we need to add them
        new_board = np.insert(new_board, slice(0, end_collapse - start_collapse), 0, axis=0)
        score = self.__get_score(end_collapse - start_collapse)

        return score, new_board

    def __game_over(self, test_board):
        return np.sum(test_board[:TetrisEnv.GAMEOVER_ROWS]) > 0

    def __play(self, col, rot_count):
        falling_piece = self.Pieces[self.current_piece]
        if rot_count > 0:
            falling_piece = np.rot90(falling_piece, rot_count, axes=(1, 0))
        p_dims = falling_piece.shape
        col = min(col, TetrisEnv.MAX_TETRIS_COLS - p_dims[1])
        max_row = TetrisEnv.TOTAL_ROWS - p_dims[0]
        chosen_row = 0
        while chosen_row < max_row:
            next_row = chosen_row + 1
            if np.sum(np.multiply(falling_piece,
                    self.board[next_row:next_row + p_dims[0], col:col + p_dims[1]])) > 0:
                break
            chosen_row = next_row
        self.board[chosen_row:chosen_row + p_dims[0], col:col + p_dims[1]] |= falling_piece
        collapse_score, new_board = self.__collapse_rows(self.board)
        collapse_score += np.sum(falling_piece) * TetrisEnv.SCORE_PIXEL
        if self.__game_over(new_board):
            return TetrisEnv.GAMEOVER_PENALTY
        self.board = new_board
        return collapse_score

    # does not affect the class, tests a play of the game given a board and a piece b64 #
    def test_play(self, board_copy, piece_type, col, rot_count):
        falling_piece = self.Pieces[piece_type]
        if rot_count > 0:
            falling_piece = np.rot90(falling_piece, rot_count, axes=(1, 0))
        p_dims = falling_piece.shape
        col = min(col, TetrisEnv.MAX_TETRIS_COLS - p_dims[1])
        max_row = TetrisEnv.TOTAL_ROWS - p_dims[0]
        chosen_row = 0
        while chosen_row < max_row:
            next_row = chosen_row + 1
            if np.sum(np.multiply(falling_piece,
                                  board_copy[next_row:next_row + p_dims[0], col:col + p_dims[1]])) > 0:
                break
            chosen_row = next_row
        board_copy[chosen_row:chosen_row + p_dims[0], col:col + p_dims[1]] |= falling_piece
        collapse_score, board_copy = self.__collapse_rows(board_copy)
        collapse_score += np.sum(falling_piece) * TetrisEnv.SCORE_PIXEL
        if self.__game_over(board_copy):
            return TetrisEnv.GAMEOVER_PENALTY, board_copy
        return collapse_score, board_copy

    def __calc_rank_n_rot(self, scoring_function, gen_params, col):
        # should return rank score and rotation a pair (rank,rot), rot is from 0 to 3
        return scoring_function(self, gen_params, col)

    def __get_lose_msg(self):
        # if understood, send to owner
        lose_msg = b'TFVMISBfIFlPVSBMT1NFIQrilZbilKTilKTilLzilZHilaLilaLilaLilaLilaLilaLilaPilaLilaLilaPilaLilaLilaLilazilazilazilazilazilazilaPilaPilaLilaLilaLilaLilaLilaLilaPilaLilazilazilazilazilazilaPilaPilaPilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaIK4pSk4pWc4pWc4pSC4pSU4pSU4pWZ4pWZ4pWc4pWc4pWc4pWZ4pWZ4pWZ4pWZ4pWc4pWc4pWi4pWi4pWi4pWi4pWr4pWs4pWj4pWj4pWj4pWj4pWi4pWi4pWi4pWi4pWi4pWc4pWc4pWc4pWc4pWc4pWc4pWc4pWi4pWj4pWj4pWc4pWc4pWc4pWc4pWc4pSk4pSC4pSC4pSC4pSC4pWc4pWc4pWc4pWR4pWc4pWR4pWi4pWiCuKVnOKUguKUlCAgICAgICAgICAgIOKUguKUguKUguKVkeKVouKVouKVouKVouKVouKVouKVo+KVouKVouKVouKVouKVnOKVnOKUguKUguKUguKUguKUlCAgIOKUlOKUlOKUlOKUlOKUlCDilJTilZnilKTilKTilKTilKTilZzilZzilZzilZzilZzilZzilZzilZwK4pSC4pSU4pSM4pSM4pSM4pWT4pWT4pWT4pWT4pWT4pWT4pWT4pWT4pWTICAg4pSU4pWZ4pWi4pWi4pWi4pWR4pWi4pWi4pWj4pWs4pWi4pWR4pWc4pSC4pSC4pSC4pSC4pSUICAgICAgICDilZPilZbilZbilZbilZbilZbilZbilKTilKTilKTilKTilKTilKTilZzilKTilKTilZwK4pSC4pSC4pWT4pWR4pWi4pWi4pWi4pWi4pWj4pWj4pWj4pWi4pWi4pWi4pWj4pWj4pWW4pWW4pSM4pSU4pWZ4pWc4pWc4pWZ4pWi4pWi4pWj4pWi4pWi4pWi4pSk4pSC4pSC4pSC4pWW4pWW4pWW4pWW4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWj4pWj4pWj4pWi4pWi4pWi4pWi4pSk4pWc4pSk4pWc4pWc4pWc4pWcCuKUguKUlCAgICAgICAg4pSU4pWZ4pWc4pWc4pSC4pWZ4pWc4pWc4pWi4pWW4pWW4pWW4pWW4pWW4pWi4pWr4pWs4pWj4pWi4pWi4pWi4pWi4pWW4pSk4pSC4pSC4pWc4pWc4pWc4pWc4pWc4pWc4pWc4pWc4pWZ4pWZ4pWZ4pWZ4pWZ4pWc4pWc4pWc4pWc4pWc4pWi4pWi4pWR4pSk4pSk4pSkCuKVluKUkCAgIOKVk+KVk+KVluKVluKVluKVluKVluKVluKVluKVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVo+KVo+KVo+KVouKVouKVouKVouKVouKVluKVouKVouKUpOKUguKUguKUlCAgICAg4pSM4pSMICAgICAg4pSM4pSC4pSC4pSC4pWc4pWcCuKVouKVluKVnOKUpOKUguKUguKUguKVnOKVnOKVnOKVnOKVouKVouKVouKVnOKVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVo+KVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVluKUpOKUvOKVouKVouKVrOKVrOKVrOKVo+KVo+KVouKVouKVouKVouKVo+KVouKVouKVluKVluKVluKVouKVogrilaLilaLilZbilZbilZbilZbilILilILilIzilZPilZbilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaPilaPilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilZbilILilILilILilZnilZnilZnilZzilZzilaLilaLilaLilaLilaLilaLilaLilaLilaLilaIK4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWj4pWj4pWi4pWi4pWi4pWi4pWi4pWc4pWc4pWc4pWc4pWR4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWj4pWi4pWi4pWi4pWi4pWi4pWi4pWj4pWi4pWi4pWi4pWi4pWi4pWj4pWi4pWi4pWi4pWi4pWi4pWiCuKVnOKVouKVouKVouKVouKVouKVouKVouKVo+KVo+KVouKVouKVouKVouKVouKVouKVnOKVnOKVnOKVnOKVluKVouKVouKVouKVouKVouKVouKVouKVouKVnOKVnOKVnOKVouKVouKVouKVnOKVnOKVq+KVrOKVrOKVrOKVo+KVouKVouKVouKVouKVouKVouKVouKVrOKVrOKVrOKVrOKVo+KVo+KVouKVouKVouKVouKVogrilZHilaLilaLilaLilaLilaLilaLilaLilaPilaPilaLilaLilaLilZzilZzilaLilZHilKTilILilZHilaLilaLilaLilaLilaPilaLilKTilKTilKTilILilILilZbilZHilaLilaLilZbilZbilKTilZzilZzilavilazilazilazilazilazilazilazilazilazilazilazilaPilaPilaPilaLilaPilaLilaLilaIK4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWc4pSC4pSC4pWR4pWc4pWc4pWc4pWc4pWc4pWi4pWi4pWc4pWc4pWc4pWc4pWc4pWc4pSk4pWW4pWR4pWi4pWi4pWi4pWi4pWc4pWc4pWZ4pWi4pWi4pWW4pWZ4pWZ4pWi4pWr4pWs4pWs4pWs4pWs4pWs4pWj4pWj4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWiCuKVnOKVnOKVnOKVnOKVouKVouKVouKVouKVouKVnOKVnOKUguKVluKVouKVnOKVnOKVmeKVmeKVnOKUpOKUpOKUpOKUguKUguKUguKUguKVnOKVnOKVnOKVnOKVnOKVqOKVqOKVnOKVnOKVnOKUguKUguKVkeKVouKVo+KVouKUpOKVnOKVnOKVnOKVnOKVnOKVnOKVouKVouKVouKVouKVouKVouKVouKVouKVouKVouKVogrilILilILilILilILilZzilZzilaLilZzilZzilILilILilZPilZzilJggICAgICAgIOKUlOKUlOKUlCAgICAgICAgIOKUjCAg4pSC4pWc4pSC4pSC4pSC4pWc4pSk4pSk4pWc4pWc4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWc4pWi4pWi4pWR4pWcCuKUguKUguKUguKUguKUguKUguKUguKUguKUguKUguKUguKUmCAgICAgICAgICAg4pSM4pWT4pWT4pSQICDilJTilJTilJTilJTilJQgIOKUlOKUguKUguKUlOKUlOKUlOKUlOKUguKUguKUguKUguKUguKUguKVnOKVnOKVnOKVnOKVnOKVnOKVnOKVnOKVnOKVnOKUggrilILilILilILilILilILilILilILilILilILilILilJQgICAgICAgICAgICAg4pSC4pSCICAgICDilIwgICAgIOKUguKUgiAgICAg4pSU4pSC4pSC4pSC4pSC4pSC4pSC4pWc4pWc4pWc4pWc4pSk4pSk4pSC4pSC4pSCCuKUguKUguKUguKUguKUguKUguKUguKUguKUgiAgICAgICAgICAgICAg4pSM4pWT4pWW4pSQICAgIOKUguKUgiAgICAg4pSUICAgICAgICAg4pSU4pSC4pSC4pSC4pSC4pSC4pSk4pSk4pSC4pSC4pSC4pSkCuKUguKUguKUguKUguKUguKUguKUguKUpOKUmCAgICAgICAgICAgICDilJTilZnilZzilZzilZzilKTilJAg4pSM4pSC4pSM4pSMICAg4pSM4pSM4pSQ4pSMICAgICAgICAg4pWZ4pWc4pSC4pSC4pSC4pSk4pSk4pSk4pSk4pSkCuKUguKUguKUguKUguKUguKUguKUguKUpOKUkCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICDilJTilJTilJjilJAgICAgIOKUlOKVnOKVnOKVnOKUpOKUpOKUpOKUpArilILilILilILilILilILilILilILilZHilZbilZbilJDilZPilILilIIgICDilJTilavilazilazilaPilIAgICAgICAgICAgICAgICAgICAgICAgICAg4pSU4pWW4pWW4pWW4pSC4pSC4pWW4pSk4pSk4pWc4pSk4pSCCuKUguKUguKUguKUguKUguKUguKUguKVnOKVnOKVouKVo+KUpOKUguKUguKVkeKVouKVliAgICAgICDilZPilZPilZMgICAgICAgIOKVk+KVk+KVk+KVluKVluKVluKVluKVluKVluKVluKUkCAg4pWT4pWW4pSC4pSC4pSC4pSC4pWR4pWc4pWc4pSk4pSC4pSCCuKUguKUguKUguKUguKUguKUguKUguKUguKUguKVmeKVouKUpOKUguKUguKVmeKVouKVouKUpOKVluKVluKVpeKVpeKVo+KVo+KVouKVouKVouKVrOKVrOKVrOKVrOKVrOKVrOKVrOKVo+KVo+KVo+KVouKVouKVouKVnOKVnOKVnOKVnOKUguKUguKVk+KVkeKVouKVnOKUguKUguKUguKUguKVnOKVnOKUpOKUguKUguKUggrilILilILilILilILilILilILilILilILilILilZzilZzilKTilKTilZbilILilZHilaLilKTilILilILilZnilaLilaLilaPilaPilaPilaLilaPilaLilaLilaLilaLilaLilaLilaLilaLilaLilaLilaPilaLilZzilKTilILilILilZbilaLilaPilZzilZzilKTilILilILilILilKTilZzilKTilKTilILilILilIIK4pSC4pSC4pSC4pSC4pSC4pSC4pSC4pWR4pWW4pSC4pSC4pSk4pSk4pSk4pSk4pSk4pWR4pSk4pSC4pSC4pSC4pSC4pWR4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWi4pWj4pWi4pWc4pWc4pWc4pWc4pWc4pSC4pSC4pSC4pWT4pWc4pWi4pWi4pWi4pWi4pWi4pWi4pSk4pSk4pSk4pSk4pWc4pWc4pSk4pSC4pSC4pSC4pSCCuKUguKUguKUguKUguKUguKUguKUguKVkeKVouKVluKUguKVmeKVkeKUpOKUpOKVnOKVnOKVnOKUpOKUguKUguKUguKUpOKVnOKUpOKUpOKVnOKVnOKVnOKVnOKVnOKVnOKUguKVk+KVk+KVq+KVrOKVrOKVmeKVnOKVnOKVnOKVnOKVkeKVouKVouKVouKVouKVouKVnOKUpOKUpOKUpOKVnOKUpOKUpOKUpOKUguKUguKUggrilILilILilILilILilILilILilILilZHilaLilaLilKTilILilZzilZzilKTilILilILilILilKTilZbilILilILilZzilZHilZHilZHilZHilZHilZzilKTilZbilZbilaLilaLilaLilaPilZzilZzilZbilZbilZbilZbilZbilaLilaLilaLilaLilaLilZzilZzilKTilZzilZzilZzilZzilKTilILilILilILilZE='
        return lose_msg

    def run(self, scoring_function, num_of_iters, gen_params, return_trace):
        self.__restart()
        # no trace
        if not return_trace:
            for it in range(num_of_iters):
                rates = []
                rotations = []
                for c in range(TetrisEnv.MAX_TETRIS_COLS):
                    r1, r2 = self.__calc_rank_n_rot(scoring_function, gen_params, c)
                    rates.append(r1)
                    rotations.append(r2)
                pos_to_play = rates.index(max(rates))  # plays first max found
                rot_to_play = rotations[pos_to_play]
                play_score = self.__play(pos_to_play, rot_to_play)
                self.score += play_score
                self.__gen_next_piece()
                if play_score < 0:
                    return self.score, self.board, self.__get_lose_msg()
            return self.score, self.board, ""
        else:  # we want to trace
            board_states = []
            ratings_n_rotations = []
            pieces_got = []
            # board_states.append(self.board.copy())
            for it in range(num_of_iters):
                rates = []
                rotations = []
                pieces_got.append(self.current_piece)
                for c in range(TetrisEnv.MAX_TETRIS_COLS):
                    r1, r2 = self.__calc_rank_n_rot(scoring_function, gen_params, c)
                    rates.append(r1)
                    rotations.append(r2)
                ratings_n_rotations.append(list(zip(rates, rotations)))
                pos_to_play = rates.index(max(rates))  # plays first max found
                rot_to_play = rotations[pos_to_play]
                play_score = self.__play(pos_to_play, rot_to_play)
                self.score += play_score
                self.__gen_next_piece()
                board_states.append(self.board.copy())
                if play_score < 0:
                    return self.score, board_states, ratings_n_rotations, pieces_got, self.__get_lose_msg()
            return self.score, board_states, ratings_n_rotations, pieces_got, ""
        # don't really feel like removing redundancy, cleaning code

# max gain + random
def random_scoring_function(tetris_env: TetrisEnv, gen_params, col):
    board, piece, next_piece = tetris_env.get_status()  # add type hinting
    print(board)
    max_height = calculate_max_height(board)
    gaps_count = calculate_gaps_count(board)
    well_depths = sum(calculate_well_depths(board))
    bumpiness = calculate_bumpiness(board)
    val = [max_height ,gaps_count ,well_depths ,bumpiness]
    scores = []
    for i in range(4):
        score, tmp_board = tetris_env.test_play(board, piece, col, i)
        if score < 0:
            # scores.append([score * gen_params[0], i])
            cal =val[i] * score
            scores.append([cal, i])
            continue
        cal = val[i] * score
        scores.append([cal, i])
        # tmp_scores = []
        # for t in range(tetris_env.MAX_TETRIS_COLS):
        #     for j in range(4):
        #         score2, _ = tetris_env.test_play(tmp_board, next_piece, t, j)
        #         tmp_scores.append(score2 * gen_params[1])
        # max_score2 = max(tmp_scores)
        # if max_score2 >= 0:
        #     score += max_score2
    #     scores.append([score * gen_params[0], i])
    # for i in range(4):
    #     scores[i][0] *= random.randint(1, gen_params[2])
    print(scores)

    vals = max(scores, key=lambda item: item[0])  # need to store it first or it iterates
    print(val)
    return vals[0] ,vals[1]


def print_stats(use_visuals_in_trace_p, states_p, pieces_p, sleep_time_p):
    vision = BoardVision()
    if use_visuals_in_trace_p:

        for state, piece in zip(states_p, pieces_p):
            vision.update_board(state)
            # print("piece")
            # condensed_print(piece)
            # print('-----')
            time.sleep(sleep_time_p)
        time.sleep(2)
        vision.close()
    else:
        for state, piece in zip(states_p, pieces_p):
            print("board")
            condensed_print(state)
            print("piece")
            condensed_print(piece)
            print('-----')


def calculate_max_height(board):
    # Find the maximum height by finding the first non-zero element in each column
    copy_board = np.flipud(board)
    height = []
    for row_idx, row in enumerate(copy_board):
        if any(row):
            height.append(row_idx)
        else:
            height.append(0)

    return max(height)

    return max_height


def calculate_gaps_count(board):
    # Count the number of gaps in each row
    copy_board = np.flipud(board)
    gaps_count = sum([1 for row in copy_board if any(row) and 0 in row])

    return gaps_count


def calculate_well_depths(board):
    copy_board = np.flipud(board)
    well_depths = [0] * copy_board.shape[1]
    for col in range(1, copy_board.shape[1] - 1):
        for row in range(copy_board.shape[0]):
            if copy_board[row, col] == 0 and copy_board[row, col - 1] != 0 and copy_board[row, col + 1] != 0:
                well_depths[col] += 1
    return well_depths


def calculate_bumpiness(board):
    copy_board = np.flipud(board)
    heights = get_column_heights(copy_board)
    bumpiness = 0

    for i in range(len(heights) - 1):
        bumpiness += abs(heights[i] - heights[i + 1])

    return bumpiness


def get_column_heights(board):
    heights = []
    copy_board = np.flipud(board)
    rows, cols = copy_board.shape

    for col in range(cols):
        max_height = 0

        for row in range(rows):
            if copy_board[row, col] != 0:
                max_height = rows - row
                break

        heights.append(max_height)

    return heights


#____________________#

#____________________#
# Genetic Algorithm Parameters
import random

# Genetic Algorithm Parameters
POPULATION_SIZE = 10
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.4
ELITE_PERCENTAGE = 0.1
NUM_GENERATIONS = 100
NUM_FACTORS =4
# Tetris Board Parameters
NUM_COLUMNS = 10
NUM_ROTATIONS = 4

# Generate initial population
def generate_population():
    population = []
    for _ in range(POPULATION_SIZE):
        individual = [random.randint(0, NUM_COLUMNS - 1)for _ in range(NUM_FACTORS)]
        population.append(individual)
    return population

# Evaluate fitness of individuals in the population
def evaluate_fitness(population,val,col):
    fitness_scores = []
    for individual in population:
        score1 = (individual[0] + val[0]) + random.randint(1,10)
        score2 = (individual[1] + val[1]) * random.randint(1, 10)
        score3 = (individual[2] + val[2]) - random.randint(1,10)
        score4 = (individual[3] - val[3]) + random.randint(1, 10)
        # Placeholder, replace with actual evaluation using the rating function based on column and rotation
        fitness = ((score1 * score2) + (score3 * score4))
        fitness_scores.append(fitness)
    return fitness_scores

# Select individuals based on their fitness scores
def selection(population, fitness_scores,val,col):
    elite_count = int(ELITE_PERCENTAGE * POPULATION_SIZE)
    elite_indices = sorted(range(len(fitness_scores)), key=lambda k: fitness_scores[k], reverse=True)[:elite_count]
    elite_individuals = [population[i] for i in elite_indices]
    remaining_count = POPULATION_SIZE - elite_count

    if sum(fitness_scores) > 0:
        selected_individuals = random.choices(population, weights=fitness_scores, k=remaining_count)
    else:
        selected_individuals = random.choices(population, k=remaining_count)

    return elite_individuals + selected_individuals

# Perform crossover between pairs of individuals
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

# Apply mutation to individuals
def mutation(individual):
    mutated_individual = []
    for gene in individual:
        if random.random() < MUTATION_RATE:
            if isinstance(gene, int):
                gene = random.randint(0, NUM_COLUMNS - 1)
            else:
                gene = random.randint(0, NUM_ROTATIONS - 1)
        mutated_individual.append(gene)
    return mutated_individual

# Create next generation
def create_next_generation(population, fitness_scores,val,col):
    next_generation = []
    elite_count = int(ELITE_PERCENTAGE * POPULATION_SIZE)
    elite_individuals = selection(population, fitness_scores,val,col)[:elite_count]
    next_generation.extend(elite_individuals)

    while len(next_generation) < POPULATION_SIZE:
        if sum(fitness_scores) != 0:
            best_individual = max(population, key=lambda x: evaluate_fitness([x],val,col)[0])
        elif sum(fitness_scores) == 0:
            return [random.randint(1, 9) for _ in range(len(fitness_scores))]

        if sum(fitness_scores) > 0:
            parent1, parent2 = random.choices(population, weights=fitness_scores, k=2)
        else:
            parent1, parent2 = random.choices(population, k=2)
        if random.random() < CROSSOVER_RATE:
            offspring1, offspring2 = crossover(parent1, parent2)
        else:
            offspring1, offspring2 = parent1, parent2

        offspring1 = mutation(offspring1)
        offspring2 = mutation(offspring2)

        next_generation.extend([offspring1, offspring2])

    return next_generation

# Main genetic algorithm
def genetic_algorithm(tetris_env: TetrisEnv, one_chromo_rando, col):
    board, piece, next_piece = tetris_env.get_status()  # add type hinting
    # print(board)
    max_height = calculate_max_height(board)
    gaps_count = calculate_gaps_count(board)
    well_depths = sum(calculate_well_depths(board))
    bumpiness = calculate_bumpiness(board)
    val = [max_height, gaps_count, well_depths, bumpiness]
    population = generate_population()

    for _ in range(NUM_GENERATIONS):
        fitness_scores = evaluate_fitness(population,val,col)
        population = create_next_generation(population, fitness_scores,val,col)


    import heapq


    # Use heapq to get the two largest numbers
    best_individual = heapq.nlargest(2, fitness_scores)

    if best_individual[1]>10:
        best_individual[1] = random.randint(1, 9)
    return best_individual

if __name__ == "_main_":
    use_visuals_in_trace = True
    sleep_time = 0.8
    # just one chromosome in the population
    # one_chromo_rando = [1, 1, 4]
    one_chromo_competent = [-4, -1, 2,3]
    from Visor import BoardVision
    import time

    # print_all_forms()
    env = TetrisEnv()
    # total_score, states, rate_rot, pieces, msg = env.run(
    #     random_scoring_function, one_chromo_rando, 100, True)
    # total_score, states, rate_rot, pieces, msg = env.run(random_scoring_function, 500, one_chromo_rando, True)
    total_score, states, rate_rot, pieces, msg = env.run(genetic_algorithm, 500, one_chromo_competent, True)

    # after running your iterations (which should be at least 500 for each chromosome)
    # you can evolve your new chromosomes from the best after you test all chromosomes here
    print("Ratings and rotations")
    for rr in rate_rot:
        print(rr)
    print('----')
    print(total_score)
    print(msg)
    print_stats(use_visuals_in_trace, states, pieces, sleep_time)
    env.set_seed(5132)
    # total_score, states, rate_rot, pieces, msg = env.run(
    #     random_scoring_function, one_chromo_rando, 100, True)
    total_score, states, rate_rot, pieces, msg = env.run(
        genetic_algorithm, 500, one_chromo_competent, True)
    # total_score, states, rate_rot, pieces, msg = env.run(random_scoring_function,  500, one_chromo_rando, True)

    print("Ratings and rotations")
    for rr in rate_rot:
        print(rr)
    print('----')
    print(total_score)
    print(msg)
    print_stats(use_visuals_in_trace, states, pieces, sleep_time)

# use log instead of printing for traces
# use smaller fonts for the message
