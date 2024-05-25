# Maze

This is just a simple maze generator using Prim's algorithm. It generates a random maze, pickles, and then provides an interface for the player to navigate using WSAD keys. There's a treasure at the center of the maze, and a bunch of randomly generated items, messages, and strangers who will talk to you.

For size changes, adjust MAZE_SIZE constant in maze.py. So far I find:
```
32x32   : very easy
64x64   : easy
128x128 : moderate
256x256 : very hard
```
Difficulty scales quickly. Try to find the treasure at the center as quickly as possible.

TODO: add minotaur
