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

    def __init__(self):
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

    def __calc_rank_n_rot(self, scoring_function, genetic_params, col):
        # should return rank score and rotation a pair (rank,rot), rot is from 0 to 3
        return scoring_function(self, genetic_params, col)

    def __get_lose_msg(self):
        # if understood, send to owner
        lose_msg = b'loss'
        return lose_msg

    def run(self, scoring_function, genetic_params, num_of_iters, return_trace):
        self.__restart()
        # no trace
        if not return_trace:
            for it in range(num_of_iters):
                rates = []
                rotations = []
                for c in range(TetrisEnv.MAX_TETRIS_COLS):
                    r1, r2 = self.__calc_rank_n_rot(scoring_function, genetic_params, c)
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
                    r1, r2 = self.__calc_rank_n_rot(scoring_function, genetic_params, c)
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

import numpy as np

def get_values(board):
    heights = []
    counts = []
    not_completed_rows = 0
    empty_rows = 0

    for row in board[::-1].T:
        if np.sum(row) > 0:
            heights.append(np.argwhere(row)[-1][0])

    value1 = np.max(heights)
    value2 = np.max(heights) - np.min(heights)

    for row in board:
        count = np.sum(row)
        counts.append(count)

        if 0 < count < len(row):
            not_completed_rows += 1
        elif count == 0:
            empty_rows += 1

    value3 = np.max(counts)
    value4 = not_completed_rows
    value5 = empty_rows

    return value1, value2, value3, value4, value5
    
# def random_scoring_function(tetris_env: TetrisEnv, gen_params, col):
#     board, piece, next_piece = tetris_env.get_status()  # add type hinting
#     scores = []
#     for i in range(4):
#         score, tmp_board = tetris_env.test_play(board.copy(), piece, col, i)
#         value1, value2, value3, value4, value5 = get_values(tmp_board)
#         score = score + value1*gen_params[0]  + value2 * gen_params[1] + value3*gen_params[2]  + value4 * gen_params[3] + value5 * gen_params[4]
        
#         scores.append([score , i])

#     val = max(scores, key=lambda item: item[0])  # need to store it first or it iterates
#     return val[0], val[1]

def random_scoring_function(tetris_env: TetrisEnv, gen_params, col):
    board, piece, next_piece = tetris_env.get_status()  # add type hinting
    scores = []

    def maxheight(tetrisboard):
        height = 23
        for row in range(len(tetrisboard)):
            if 1 not in tetrisboard[row]:
                height = row
        height = abs(height - 23)
        if height > 20:
            return 999
        return height

    for i in range(4):
        score4, tmp_board = tetris_env.test_play(board, piece, col, i)
        high = maxheight(tmp_board)
        score = (-high * gen_params[0]) + (score4 * gen_params[1])
        tmp_scores = []
        for t in range(tetris_env.MAX_TETRIS_COLS):
            for j in range(4):
                score3, tmp_board2 = tetris_env.test_play(tmp_board, next_piece, t, j)
                high = maxheight(tmp_board2)
                score2 = (-high * gen_params[2]) + (score3 * gen_params[3]) 
                tmp_scores.append(score2)
        max_score2 = max(tmp_scores)
        score += max_score2
        score = score * gen_params[4]
        scores.append([score, i])
    val = max(scores, key=lambda item: item[0])  # need to store it first or it iterates
    # print(val)
    return val[0], val[1]

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


if __name__ == "__main__":
    use_visuals_in_trace = True
    sleep_time = 0.8
    # just one chromosome in the population
    one_chromo_rando = [1, 1, 5, -12, 3]
    # one_chromo_competent = [-4, -1, 2,3]
    from Visor import BoardVision
    import time

    print_all_forms()
    env = TetrisEnv()
    total_score, states, rate_rot, pieces, msg = env.run(
        random_scoring_function, one_chromo_rando, 100, True)
    total_score, states, rate_rot, pieces, msg = env.run(
        random_scoring_function, one_chromo_rando, 100, True)
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
    total_score, states, rate_rot, pieces, msg = env.run(
        random_scoring_function, one_chromo_rando, 100, True)
    total_score, states, rate_rot, pieces, msg = env.run(
        random_scoring_function, one_chromo_rando, 100, True)
    print("Ratings and rotations")
    for rr in rate_rot:
        print(rr)
    print('----')
    print(total_score)
    print(msg)
    print_stats(use_visuals_in_trace, states, pieces, sleep_time)

# use log instead of printing for traces
# use smaller fonts for the message


#Constants, experiment parameters
GENs = 5
POPULATION_SIZE = 12
MIXING_NUMBER = 2
CROSSOVER_RATE = 0.6
MUTATION_RATE = 0.2

import random
from scipy import special as sc

def selection(population):
    parents = []
    scores=[]
    cumulative_prob = [0]
    for ind in population:
        scores.append(env.run(random_scoring_function, ind, 300, True)[0] + 1000)
    for score in scores:
#         cumulative score
        cumulative_prob.append(score/sum(scores) + cumulative_prob[-1])
    cumulative_prob = cumulative_prob[1:]
    rands = np.random.uniform(0,1, size=int(len(population)*CROSSOVER_RATE))
    
    for i, rand in enumerate(rands):
        if rand <= cumulative_prob[0]:
            parents.append(population[0])
            continue
        for j in range(1,len(cumulative_prob)):
            if rand <= cumulative_prob[j] and rand > cumulative_prob[j-1]:
                parents.append(population[j])
                break
    
    return parents

import itertools

def crossover(parents):
    
    #random indexes to to cross states with
    cross_points = random.sample(range(GENs), MIXING_NUMBER - 1)
    offsprings = []
    
    #all permutations of parents
    permutations = list(itertools.permutations(parents, MIXING_NUMBER))
    
    for perm in permutations:
        offspring = []
        
        #track starting index of sublist
        start_pt = 0
        
        for parent_idx, cross_point in enumerate(cross_points): #doesn't account for last parent
            
            #sublist of parent to be crossed
            parent_part = perm[parent_idx][start_pt:cross_point]
            offspring.append(parent_part)
            
            #update index pointer
            start_pt = cross_point
            
        #last parent
        last_parent = perm[-1]
        parent_part = last_parent[cross_point:]
        offspring.append(parent_part)
        
        #flatten the list since append works kinda differently
        offsprings.append(list(itertools.chain(*offspring)))
    
    return offsprings

def mutate(seq):
    for row in range(len(seq)):
        if random.random() < MUTATION_RATE:
            seq[row] = np.random.uniform(-10,10)
    
    return seq

def print_found_goal(population):
    for ind in population:
        score, _, _, _, _ = env.run(
        random_scoring_function, ind, 500, True)
        print(f'{ind}. Score: {score}')


def evolution(population):
    #select individuals to become parents
    parents = selection(population)
    #recombination. Create new offsprings
    offsprings = crossover(parents)
    #mutation
    offsprings = list(map(mutate, offsprings))

    #introduce top-scoring individuals from previous generation and keep top fitness individuals
    new_gen = offsprings

    for ind in population:
        new_gen.append(ind)

    new_gen = sorted(new_gen, key=lambda ind: env.run(random_scoring_function, ind, 500, True)[0], reverse=True)[:POPULATION_SIZE]

    return new_gen

def generate_population():
    population = np.random.uniform(-10,10,size=(POPULATION_SIZE,GENs))
    
    return population


#Running the experiment

generation = 0

#generate random population
population = generate_population()
    
for i in range(4):
    print(f'Generation: {generation}')
    print_found_goal(population)
    population = evolution(population)
    generation += 1


env.run(random_scoring_function, [-2.386593920918032, -6.158331721900976, 3.4012925295187095, -2.2211769141050404, -2.2971017631738144], 600, True)[0]