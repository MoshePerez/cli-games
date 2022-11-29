import argparse
import time
import os
from copy import deepcopy
from color_game import Game, YOU_LOSE_BANNER, YOU_WIN_BANNER
from player import get_wining_move_sequence


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def run_game(game: Game, auto_play=False):
    error_str = None
    while True:
        clear_screen()
        if error_str is not None:
            print(error_str)
        game.print_bottles()
        if game.is_game_won():
            print(YOU_WIN_BANNER)
            return
        if game.is_game_lost():
            print(YOU_LOSE_BANNER)
            return
        if auto_play:
            print("getting wining move sequence...")
            wining_moves_found, moves = get_wining_move_sequence(game.bottles)
            if not wining_moves_found:
                print("there is no way to win!")
                return
            for move in moves:
                print((move[0]+1, move[1]+1))
                time.sleep(0.05)
                game.play_move(move)
                clear_screen()
                game.print_bottles()
        else:
            source_index = game.get_index_from_input(prompt="Enter source bottle number:\n")
            target_index = game.get_index_from_input(prompt="Enter target bottle number:\n")
            error_str = game.play_move((source_index, target_index))


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--bottle_size',  type=int, default=4, help='the number of layers in each bottle')
    parser.add_argument('--auto_play', action='store_true', help='let the computer solve the game')
    args = parser.parse_args()
    try:
        game = Game(bottle_size=args.bottle_size)
        while True:
            game_bottles_at_start = deepcopy(game.bottles)
            run_game(game, auto_play=args.auto_play)
            user_input = input("press any key to play again, r to retry the same game, or Ctrl+c to exit\n")
            if user_input == 'r':
                game = Game(bottles=game_bottles_at_start)
            else:
                game = Game(bottle_size=args.bottle_size)
    except KeyboardInterrupt:
        print("\nBye!")

if __name__ == '__main__':
    main()