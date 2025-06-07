# Hot Typing Action Game

A fast-paced typing game built with Pygame where players must type words correctly while avoiding enemies.

## Game Features

- Dynamic difficulty that increases as you progress
- Character movement using WASD keys
- Enemy avoidance mechanics
- Health system with invincibility frames
- Word difficulty progression (short → medium → long words)
- Score tracking based on word length
- Performance statistics (WPM, accuracy)

## How to Play

1. Use WASD keys to move your character (green circle)
2. Type the displayed words correctly
3. Avoid the red enemy or lose health
4. Complete 15 words correctly to win!

## Requirements

- Python 3.x
- Pygame library

## Installation

```bash
pip install pygame
python hot_typing_action_game.py
```

## Word Lists

The game uses three difficulty levels of word lists:
- words_short.txt: 3-5 character words
- words_medium.txt: 6-10 character words
- words_long.txt: 11-15 character words

You can customize these files with your own word lists.
