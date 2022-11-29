use rand::{
    seq::{IteratorRandom, SliceRandom},
    thread_rng,
};
use std::io;
use std::ops::{Index, IndexMut};
use std::{cmp::min, usize};
use std::{collections::HashMap, fmt::Display};
use strum::IntoEnumIterator;
use strum_macros::EnumIter;

pub const YOU_WIN_BANNER: &str = "
██╗   ██╗ ██████╗ ██╗   ██╗    ██╗    ██╗██╗███╗   ██╗██╗
╚██╗ ██╔╝██╔═══██╗██║   ██║    ██║    ██║██║████╗  ██║██║
 ╚████╔╝ ██║   ██║██║   ██║    ██║ █╗ ██║██║██╔██╗ ██║██║
  ╚██╔╝  ██║   ██║██║   ██║    ██║███╗██║██║██║╚██╗██║╚═╝
   ██║   ╚██████╔╝╚██████╔╝    ╚███╔███╔╝██║██║ ╚████║██╗
   ╚═╝    ╚═════╝  ╚═════╝      ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝ 
";

pub const YOU_LOSE_BANNER: &str = "
██╗   ██╗ ██████╗ ██╗   ██╗    ██╗      ██████╗ ███████╗███████╗██╗
╚██╗ ██╔╝██╔═══██╗██║   ██║    ██║     ██╔═══██╗██╔════╝██╔════╝██║
 ╚████╔╝ ██║   ██║██║   ██║    ██║     ██║   ██║███████╗█████╗  ██║
  ╚██╔╝  ██║   ██║██║   ██║    ██║     ██║   ██║╚════██║██╔══╝  ╚═╝
   ██║   ╚██████╔╝╚██████╔╝    ███████╗╚██████╔╝███████║███████╗██╗
   ╚═╝    ╚═════╝  ╚═════╝     ╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝
";

const RESET_COLOR: &str = "\x1b[0m";

#[derive(Copy, Clone, PartialEq, Eq, EnumIter, Debug)]
pub enum Color {
    Red,
    Green,
    Yellow,
    Blue,
    Pink,
    Cyan,
    White,
    Transparent,
}

impl Color {
    fn value(&self) -> &str {
        match *self {
            Color::Red => "\x1b[41m",
            Color::Green => "\x1b[42m",
            Color::Yellow => "\x1b[43m",
            Color::Blue => "\x1b[44m",
            Color::Pink => "\x1b[45m",
            Color::Cyan => "\x1b[46m",
            Color::White => "\x1b[47m",
            Color::Transparent => "",
        }
    }
}

pub fn colored_space(color: Color, size: usize) -> String {
    let space = " ".repeat(size);
    if matches!(color, Color::Transparent) {
        return space;
    }
    let mut color_string = color.value().to_owned();
    color_string.push_str(&space);
    color_string.push_str(RESET_COLOR);

    color_string
}

pub struct Bottle {
    pub size: usize,
    pub color_list: Vec<Color>,
}

impl Bottle {
    pub fn is_full(&self) -> bool {
        self.color_list[self.size - 1] != Color::Transparent
    }

    pub fn is_empty(&self) -> bool {
        self.color_list[0] == Color::Transparent
    }

    pub fn is_one_color(&self) -> bool {
        let first_color = self.color_list[0];
        for color in self.color_list[1..].iter() {
            if *color != first_color && *color != Color::Transparent {
                return false;
            }
        }
        true
    }

    pub fn is_complete(&self) -> bool {
        self.is_full() && self.is_one_color()
    }

    pub fn get_empty_space_count(&self) -> usize {
        return self
            .color_list
            .iter()
            .filter(|color| **color == Color::Transparent)
            .count();
    }

    pub fn pop_color_unit(&mut self) -> Color {
        let mut ind = self.size - 1;
        loop {
            if self.color_list[ind] != Color::Transparent {
                let removed_color = self.color_list[ind];
                self.color_list[ind] = Color::Transparent;
                return removed_color;
            }
            if ind == 0 {
                panic!("Attempted to pop from empty bottle");
            }
            ind -= 1;
        }
    }

    pub fn push_color_unit(&mut self, color_to_push: Color) {
        for (i, color) in self.color_list.iter().enumerate() {
            if *color == Color::Transparent {
                self.color_list[i] = color_to_push;
                return;
            }
        }
        todo!("add error handling for pushing to full bottle")
    }

    pub fn get_top_color_and_size(&self) -> (Color, usize) {
        let mut size: usize = 0;
        let mut last_color = Color::Transparent;
        for color in self
            .color_list
            .iter()
            .filter(|c| **c != Color::Transparent)
            .rev()
        {
            if last_color == Color::Transparent {
                last_color = *color;
                size += 1;
            } else if last_color == *color {
                size += 1;
            } else {
                break;
            }
        }
        (last_color, size)
    }

    pub fn pour_into(&mut self, target: &mut Bottle) -> &str {
        if target.is_full(){
            return "Target cannot be a full bottle";
        }
        if self.is_complete(){
            return "Source cannot be a completed bottle";
        }
        if self.is_empty(){
            return "Source cannot be empty";
        }
        
        let (bottle_top_color, bottle_top_size) = self.get_top_color_and_size();
        let (target_top_color, _) = target.get_top_color_and_size();
        if target_top_color != Color::Transparent && target_top_color != bottle_top_color {
            return "Source and target colors must be the same";
        }
        let moves_to_make = min(bottle_top_size, target.get_empty_space_count());
        for _ in 0..moves_to_make {
            target.push_color_unit(self.pop_color_unit());
        }
        return "";
    }
}

impl Index<usize> for Bottle {
    type Output = Color;
    fn index(&self, index: usize) -> &Self::Output {
        &self.color_list[index]
    }
}

impl IndexMut<usize> for Bottle {
    fn index_mut(&mut self, index: usize) -> &mut Color {
        &mut self.color_list[index]
    }
}

impl Display for Bottle {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut bottle_str = String::new();
        let mut ind = self.size - 1;
        loop {
            let color = self.color_list[ind];
            bottle_str.push_str(&format!("|{}|", colored_space(color, 3)));
            if ind == 0 {
                break;
            }
            bottle_str.push('\n');
            ind -= 1;
        }
        write!(f, "{}", bottle_str)
    }
}

pub fn get_random_mixed_bottles(bottle_count: usize, bottle_size: usize) -> Vec<Bottle> {
    let mut rng = thread_rng();
    let colors_to_use = Color::iter()
        .filter(|c| *c != Color::Transparent)
        .choose_multiple(&mut rng, bottle_count);

    let mut colors_vec: Vec<Color> = Vec::new();
    for _ in 0..bottle_size {
        colors_vec.append(&mut colors_to_use.clone())
    }
    colors_vec.shuffle(&mut rng);

    // make sure there are no sequences of length bottle_size
    let mut prev_color = Color::Transparent;
    let mut count = 0;
    for color in &colors_vec {
        if count == bottle_size {
            return get_random_mixed_bottles(bottle_count, bottle_size);
        }
        if prev_color == *color {
            count += 1;
        } else {
            prev_color = *color;
            count = 0
        }
    }
    let mut bottles: Vec<Bottle> = Vec::new();
    for created_bottles_count in 0..bottle_count {
        let start_ind = created_bottles_count * bottle_size;
        let end_ind = start_ind + bottle_size;
        let mut bottle_color_list: Vec<Color> = Vec::new();
        for color in colors_vec[start_ind..end_ind].iter() {
            bottle_color_list.push(*color);
        }
        bottles.push(Bottle {
            size: bottle_size,
            color_list: bottle_color_list,
        });
    }
    bottles
}

pub struct Game {
    pub bottles: Vec<Bottle>,
    pub bottle_size: usize,
}

impl Game {
    pub fn new(full_count: usize, empty_count: usize, bottle_size: usize) -> Self {
        // TODO add option to pass bottles as argument
        let mut bottles = get_random_mixed_bottles(full_count, bottle_size);
        for _ in 0..empty_count {
            bottles.push(Bottle {
                size: bottle_size,
                color_list: vec![Color::Transparent; bottle_size],
            })
        }

        Self {
            bottles,
            bottle_size,
        }
    }

    pub fn is_game_won(&self) -> bool {
        for bottle in &self.bottles {
            if !bottle.is_complete() && !bottle.is_empty() {
                return false;
            }
        }
        true
    }

    pub fn is_game_lost(&self) -> bool {
        for bottle in &self.bottles {
            if bottle.is_empty() {
                return false;
            }
        }
        let mut valid_sources_map = HashMap::new();
        let mut valid_targets_map = HashMap::new();
        for (ind, bottle) in self.bottles.iter().enumerate() {
            let (top_color, top_layer_size) = bottle.get_top_color_and_size();
            let empty_space = bottle.get_empty_space_count();
            let bottle_info_map = HashMap::from([
                ("top_color", top_color.value().to_owned()),
                ("top_layer_size", top_layer_size.to_string()),
                ("empty_space", empty_space.to_string()),
            ]);
            if !bottle.is_full() {
                // bottle is valid target
                valid_targets_map.insert(ind, bottle_info_map.clone());
            }
            if !bottle.is_complete() && !bottle.is_empty() {
                // bottle is valid source
                valid_sources_map.insert(ind, bottle_info_map);
            }
        }
        for (source_ind, source_info) in valid_sources_map.iter() {
            for (target_ind, target_info) in valid_targets_map.iter() {
                if source_ind != target_ind
                    && target_info.get("top_color").unwrap()
                        == source_info.get("top_color").unwrap()
                {
                    let empty_space_on_target = target_info
                        .get("empty_space")
                        .unwrap()
                        .parse::<usize>()
                        .unwrap();
                    let source_top_layer_size = source_info
                        .get("top_layer_size")
                        .unwrap()
                        .parse::<usize>()
                        .unwrap();
                    if empty_space_on_target >= source_top_layer_size {
                        return false;
                    }
                }
            }
        }
        true
    }

    pub fn print_bottles(&self) {
        let first_bottle_str = self.bottles[0].to_string();
        let mut out_list: Vec<String> = first_bottle_str
            .split('\n')
            .map(|s| s.to_string())
            .collect();

        for bottle in &self.bottles[1..] {
            let bottle_str_full = bottle.to_string();
            let bottle_str_rows: Vec<&str> = bottle_str_full.split('\n').collect();
            for (i, split) in bottle_str_rows.iter().enumerate() {
                out_list[i] = format!("{}    {}", out_list[i], split);
            }
        }
        for i in 1..(self.bottles.len() + 1) {
            print!("  {i}      ");
        }
        println!();
        for row in out_list.iter() {
            println!("{row}");
        }
    }

    pub fn get_index_from_input(&self, prompt: &str) -> usize {
        loop {
            println!("{prompt}");
            let mut index_str = String::new();
            io::stdin()
                .read_line(&mut index_str)
                .expect("Failed to read index");

            match index_str.trim().parse::<usize>() {
                Ok(n) => {
                    if n > 0 && n <= self.bottles.len() {
                        return n - 1;
                    }
                    println!("invalid value")
                }
                Err(_) => {
                    println!("invalid value");
                }
            }
        }
    }

    pub fn play_move(&mut self, source_index: usize, target_index: usize) -> &str{
        if source_index == target_index{
            return "";
        }
        // This part is a bit crazy, it's a workaround to borrow 2 mutable elements
        if source_index < target_index {
            let (head, tail) = self.bottles.split_at_mut(source_index + 1);
            return head[source_index].pour_into(&mut tail[target_index - source_index - 1]);
        } else {
            let (head, tail) = self.bottles.split_at_mut(target_index + 1);
            return tail[source_index - target_index - 1].pour_into(&mut head[target_index])
        }
    }
}
