from __future__ import annotations
from typing import List, Optional
from enum import Enum
import random

from colorama import Back, Style


YOU_WIN_BANNER = """
██╗   ██╗ ██████╗ ██╗   ██╗    ██╗    ██╗██╗███╗   ██╗██╗
╚██╗ ██╔╝██╔═══██╗██║   ██║    ██║    ██║██║████╗  ██║██║
 ╚████╔╝ ██║   ██║██║   ██║    ██║ █╗ ██║██║██╔██╗ ██║██║
  ╚██╔╝  ██║   ██║██║   ██║    ██║███╗██║██║██║╚██╗██║╚═╝
   ██║   ╚██████╔╝╚██████╔╝    ╚███╔███╔╝██║██║ ╚████║██╗
   ╚═╝    ╚═════╝  ╚═════╝      ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝ 
"""

class Color(Enum):
    RED = Back.RED
    GREEN = Back.GREEN
    CYAN = Back.LIGHTCYAN_EX
    YELLOW = Back.YELLOW
    PINK = Back.LIGHTMAGENTA_EX
    BLUE = Back.BLUE
    WHITE = Back.WHITE


def colored_space(color: Color, size: int):
    if color is None:
        return ' '*size
    return color.value + ' '*size + Style.RESET_ALL


class Bottle:
    def __init__(self, color_list: List[Optional[Color]]) -> None:
        if Bottle.is_color_list_valid(color_list):
            self._colors_list = color_list
        else:
            raise ValueError("invalid color list")

    def __getitem__(self, index):
        return self._colors_list[index]

    @staticmethod
    def is_color_list_valid(color_list):
        if len(color_list) != 4:
            print("bad length")
        if not all(isinstance(color, Color) or (color is None) for color in color_list):
            print('bad types')
        if len(color_list) == 4 and all(isinstance(color, Color) or (color is None) for color in color_list):
            prev_is_none = False
            for color in color_list:
                if color is None:
                    prev_is_none = True
                elif prev_is_none:    
                    return False  # there is a color on top of an empty space
            return True
        return False
    
    def __str__(self) -> str:
        return (
            f"|{colored_space(self[3], 3)}|\n"
            f"|{colored_space(self[2], 3)}|\n"
            f"|{colored_space(self[1], 3)}|\n"
            f"|{colored_space(self[0], 3)}|"
            )

    def is_full(self):
        return self[-1] is not None
    
    def is_empty(self):
        return self[0] is None

    def is_complete(self):
        return self.is_full() and len(set(self._colors_list)) == 1

    def get_empty_space_count(self):
        return self._colors_list.count(None)

    def pop_color_unit(self):
        for i in list(range(3, -1, -1)):
            if self[i] is not None:
                color = self[i]
                self._colors_list[i] = None
                return color
        raise IndexError("pop from empty bottle")

    def push_color_unit(self, color_unit: Color):
        for i in range(4):
            if self[i] is None:
                self._colors_list[i] = color_unit
                return
        raise IndexError("push to full bottle")

    def pour_into(self, target: Bottle):
        if target.is_full() or self.is_complete() or self.is_empty():
            print("invalid move")
            return
        bottle_top_color, bottle_top_size = self.get_top_color_and_size()
        target_top_color, _ = target.get_top_color_and_size()
        if target_top_color is not None and target_top_color != bottle_top_color:
            print("invalid move")
            return
        moves_to_make = min(bottle_top_size, target.get_empty_space_count())
        for _ in range(moves_to_make):
            target.push_color_unit(self.pop_color_unit())
        

    def get_top_color_and_size(self):
        size = 0
        last_color = None
        for color in self.iterate_from_top():
            if last_color is None:
                last_color = color
                size += 1
            elif last_color == color:
                size += 1
            else:
                return last_color, size
        return last_color, size
        

    def iterate_from_top(self):
        for level_color in self._colors_list[::-1]:
            if level_color is not None:
                yield level_color


def get_random_mixed_bottles(bottle_count) -> List[Bottle]:
    all_colors = list(Color)
    colors_to_use = random.sample(all_colors, k=bottle_count) * 4
    random.shuffle(colors_to_use)
    # make sure there are noe sequences of length 4
    prev_color = None
    count = 0
    for color in colors_to_use:
        if count == 4:
            return get_random_mixed_bottles(bottle_count)
        if prev_color == color:
            count += 1
        else:
            prev_color = color
            count = 0
    
    colors_lists = [colors_to_use[x:x+4] for x in range(0, len(colors_to_use), 4)]
    return [Bottle(color_list) for color_list in colors_lists]


class Game:
    def __init__(self, full_count: int = 7, empty_count: int = 2) -> None:
        full_bottles = get_random_mixed_bottles(full_count)
        empty_bottles = [Bottle([None, None, None, None]) for _ in range(empty_count)]
        self.bottles = full_bottles + empty_bottles

    def is_game_over(self):
        return all((bottle.is_complete() or bottle.is_empty()) for bottle in self.bottles)
    
    def print_bottles(self):
        out_list = self.bottles[0].__str__().split('\n')
        for bottle in self.bottles[1:]:
            splitted = bottle.__str__().split('\n')
            for i, split in enumerate(splitted):
                out_list[i] += f"    {split}"
        for i in range(1, len(self.bottles) + 1):
            print(f'  {i}      ', end='')
        print('')
        print('\n'.join(out_list))

    def get_bottle_from_input(self, prompt: str) -> Bottle:
        while True:
            try:
                input_index = int(input(prompt)) - 1
                return self.bottles[input_index]
            except Exception:
                print("Invalid input")


    def run(self):
        while True:
            self.print_bottles()
            if self.is_game_over():
                print(YOU_WIN_BANNER)
                return
            source_bottle = self.get_bottle_from_input(prompt="Enter source bottle number:\n")
            target_bottle = self.get_bottle_from_input(prompt="Enter target bottle number:\n")
            source_bottle.pour_into(target_bottle)

def main():
    try:
        while True:
            game = Game()
            game.run()    
            input("press any key to play again, or Ctrl+c to exit\n")
            print('\n\n\n\n\n')
    except KeyboardInterrupt:
        print("Bye!")

main()