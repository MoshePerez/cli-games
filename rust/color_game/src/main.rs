use std::io;
mod game;
use game::{Game, YOU_LOSE_BANNER, YOU_WIN_BANNER};

// TODO use command args instead of hardcoded values
const BOTTLE_SIZE: usize = 6;
const FULL_BOTTLES_COUNT: usize = 7;
const EMPTY_BOTTLES_COUNT: usize = 2;

pub fn clear_screen() {
    print!("\x1Bc");
}

pub fn run_game(game: &mut Game) {
    loop {
        clear_screen();
        game.print_bottles();
        if game.is_game_won() {
            println!("{YOU_WIN_BANNER}");
            return;
        }
        if game.is_game_lost() {
            println!("{YOU_LOSE_BANNER}");
            return;
        }
        let source_index = game.get_index_from_input("Enter source bottle number:");
        let target_index = game.get_index_from_input("Enter target bottle number:");
        game.play_move(source_index, target_index);
    }
}

fn main() {
    println!("exiting..");
    ctrlc::set_handler(move || {
        println!("Bye!");
        std::process::exit(0);
    })
    .expect("Error setting Ctrl-C handler");

    loop {
        let mut game = Game::new(FULL_BOTTLES_COUNT, EMPTY_BOTTLES_COUNT, BOTTLE_SIZE);
        run_game(&mut game);
        println!("press any key to play again, or Ctrl+c to exit");
        let mut user_input = String::new();
        io::stdin()
            .read_line(&mut user_input)
            .expect("Failed to read index");
    }
}
