from __future__ import annotations
from typing import List, Optional, Tuple
from enum import Enum
import random


YOU_WIN_BANNER = """
██╗   ██╗ ██████╗ ██╗   ██╗    ██╗    ██╗██╗███╗   ██╗██╗
╚██╗ ██╔╝██╔═══██╗██║   ██║    ██║    ██║██║████╗  ██║██║
 ╚████╔╝ ██║   ██║██║   ██║    ██║ █╗ ██║██║██╔██╗ ██║██║
  ╚██╔╝  ██║   ██║██║   ██║    ██║███╗██║██║██║╚██╗██║╚═╝
   ██║   ╚██████╔╝╚██████╔╝    ╚███╔███╔╝██║██║ ╚████║██╗
   ╚═╝    ╚═════╝  ╚═════╝      ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝ 
"""
YOU_LOSE_BANNER = """
██╗   ██╗ ██████╗ ██╗   ██╗    ██╗      ██████╗ ███████╗███████╗██╗
╚██╗ ██╔╝██╔═══██╗██║   ██║    ██║     ██╔═══██╗██╔════╝██╔════╝██║
 ╚████╔╝ ██║   ██║██║   ██║    ██║     ██║   ██║███████╗█████╗  ██║
  ╚██╔╝  ██║   ██║██║   ██║    ██║     ██║   ██║╚════██║██╔══╝  ╚═╝
   ██║   ╚██████╔╝╚██████╔╝    ███████╗╚██████╔╝███████║███████╗██╗
   ╚═╝    ╚═════╝  ╚═════╝     ╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝
"""
RESET_COLOR = '\x1b[0m'


class Color(Enum):
    RED = '\x1b[41m'
    GREEN = '\x1b[42m'
    YELLOW = '\x1b[43m'
    BLUE = '\x1b[44m'
    PINK = '\x1b[45m'
    CYAN = '\x1b[46m'
    WHITE = '\x1b[47m'


def colored_space(color: Color, size: int):
    if color is None:
        return ' '*size
    return color.value + ' '*size + RESET_COLOR


class Bottle:
    def __init__(self, color_list: List[Optional[Color]]) -> None:
        self._colors_list = color_list
        self.size = len(color_list)

    def __getitem__(self, index):
        return self._colors_list[index]
    
    def __str__(self) -> str:
        return '\n'.join([f"|{colored_space(color, 3)}|" for color in self._colors_list[::-1]])

    def is_full(self):
        return self[-1] is not None
    
    def is_empty(self):
        return self[0] is None

    def is_one_color(self):
        return len(set([i for i in self._colors_list if i is not None])) == 1
    
    def is_complete(self):
        return self.is_full() and self.is_one_color()

    def get_empty_space_count(self):
        return self._colors_list.count(None)

    def pop_color_unit(self):
        for i in list(range(self.size -1, -1, -1)):
            if self[i] is not None:
                color = self[i]
                self._colors_list[i] = None
                return color
        raise IndexError("pop from empty bottle")

    def push_color_unit(self, color_unit: Color):
        for i in range(self.size):
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


def get_random_mixed_bottles(bottle_count: int, bottle_size: int) -> List[Bottle]:
    all_colors = list(Color)
    colors_to_use = random.sample(all_colors, k=bottle_count) * bottle_size
    random.shuffle(colors_to_use)
    # make sure there are no sequences of length bottle_size
    prev_color = None
    count = 0
    for color in colors_to_use:
        if count == bottle_size:
            return get_random_mixed_bottles(bottle_count, bottle_size)
        if prev_color == color:
            count += 1
        else:
            prev_color = color
            count = 0
    
    colors_lists = [colors_to_use[x:x+bottle_size] for x in range(0, len(colors_to_use), bottle_size)]
    return [Bottle(color_list) for color_list in colors_lists]


class Game:
    def __init__(self, full_count: int = 7, empty_count: int = 2,
                 bottle_size: int = 4, bottles: List[Bottle] = None) -> None:
        if bottles:
            self.bottles = bottles
            self.bottles_size = bottles[0].size
        else:
            full_bottles = get_random_mixed_bottles(full_count, bottle_size)
            empty_bottles = [Bottle([None] * bottle_size) for _ in range(empty_count)]
            self.bottles = full_bottles + empty_bottles
            self.bottles_size = bottle_size

    def is_game_won(self):
        return all((bottle.is_complete() or bottle.is_empty()) for bottle in self.bottles)
    
    def is_game_lost(self):
        if not any(bottle.is_empty() for bottle in self.bottles):
            valid_sources = [bottle for bottle in self.bottles if not bottle.is_complete() and not bottle.is_empty()]
            valid_targets = [bottle for bottle in self.bottles if not bottle.is_full()]
            valid_sources_dict = {}
            valid_targets_dict = {}
            for source in valid_sources:
                top_color, top_layer_size = source.get_top_color_and_size()
                empty_space = source.get_empty_space_count()
                valid_sources_dict[source] = {
                    "top_color": top_color, "top_layer_size": top_layer_size, "empty_space": empty_space
                }
            for target in valid_targets:
                top_color, top_layer_size = target.get_top_color_and_size()
                empty_space = target.get_empty_space_count()
                valid_targets_dict[target] = {
                    "top_color": top_color, "top_layer_size": top_layer_size, "empty_space": empty_space
                }
            
            for source, source_info in valid_sources_dict.items():
                available_targets = [
                    target for target, target_info in valid_targets_dict.items()
                    if source != target and target_info['top_color'] == source_info['top_color']
                    and target_info['empty_space'] >= source_info['top_layer_size']
                ]
                if available_targets:
                    return False
            else:
                return True

        return False

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

    def get_index_from_input(self, prompt: str) -> Bottle:
        while True:
            try:
                return int(input(prompt)) - 1
            except Exception:
                print("Invalid input")

    def play_move(self, move: Tuple[int, int]):
        source_index, target_index = move
        source_bottle = self.bottles[source_index]
        target_bottle = self.bottles[target_index]
        source_bottle.pour_into(target_bottle)
