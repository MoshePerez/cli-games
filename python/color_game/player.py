from copy import deepcopy
from typing import List, Tuple
from color_game import Bottle, Color


MOVES_CACHE = {}


def bottle_list_to_cache_key(bottles: List[Bottle]):
    key = ''
    for bottle in bottles:
        for color in bottle._colors_list:
            if color is None:
                key += 'None'
            else:
                key += Color(color).name
    return key


def sort_moves_by_priority(bottles: List[Bottle], moves: List[Tuple[int, int]]):
    moves_to_empty_bottle = []
    moves_to_non_empty_bottle = []
    for move in moves:
        target_index = move[1]
        if bottles[target_index].is_empty():
            moves_to_empty_bottle.append(move)
        else:
            moves_to_non_empty_bottle.append(move)
    return moves_to_non_empty_bottle + moves_to_empty_bottle


def get_available_moves(bottles: List[Bottle]) -> List[Tuple[int, int]]:
    cache_key = bottle_list_to_cache_key(bottles)
    if cache_key in MOVES_CACHE:
        return MOVES_CACHE[cache_key]
    available_moves = []
    valid_sources = [(i, bottle) for (i, bottle) in enumerate(bottles)
                     if not bottle.is_complete() and not bottle.is_empty()]
    valid_targets = [(i, bottle) for (i, bottle) in enumerate(bottles) if not bottle.is_full()]
    valid_sources_dict = {}
    valid_targets_dict = {}
    for i, source in valid_sources:
        top_color, top_layer_size = source.get_top_color_and_size()
        empty_space = source.get_empty_space_count()
        valid_sources_dict[source] = {
            "top_color": top_color, "top_layer_size": top_layer_size, "empty_space": empty_space, 'bottle_number': i
        }
    for i, target in valid_targets:
        top_color, top_layer_size = target.get_top_color_and_size()
        empty_space = target.get_empty_space_count()
        valid_targets_dict[target] = {
            "top_color": top_color, "top_layer_size": top_layer_size, "empty_space": empty_space, 'bottle_number': i
        }
    
    for source, source_info in valid_sources_dict.items():
        available_targets = [
            target_info for target, target_info in valid_targets_dict.items()
            if source != target 
            and target_info['empty_space'] >= source_info['top_layer_size']
            and (
                target_info['top_color'] == source_info['top_color'] 
                or target.is_empty() and not source.is_one_color())
        ]
        available_moves.extend([(source_info['bottle_number'], target_info['bottle_number'])
                                for target_info in available_targets])    
    sorted_moves = sort_moves_by_priority(bottles, available_moves)
    MOVES_CACHE[cache_key] = sorted_moves
    return sorted_moves


def get_wining_move_sequence(bottles: List[Bottle]):
    try:
        return _get_wining_move_sequence(bottles)
    finally:
        MOVES_CACHE.clear()


def _get_wining_move_sequence(bottles: List[Bottle]):
    wining_state_found = all((bottle.is_complete() or bottle.is_empty()) for bottle in bottles)
    if wining_state_found:
        return True, []
    available_moves = get_available_moves(bottles)

    for move in available_moves:
        source_index, target_index = move
        test_bottles = deepcopy(bottles)
        source_bottle = test_bottles[source_index]
        target_bottle = test_bottles[target_index]
        source_bottle.pour_into(target_bottle)
        is_next_move_wining, next_move_sequence = get_wining_move_sequence(test_bottles)
        if is_next_move_wining:
            return True, [move] + next_move_sequence

    return False, []