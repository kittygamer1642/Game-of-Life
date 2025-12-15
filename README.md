# The Game of Life
This is a Python implementation of John Conway's Game of Life.

The game is played on a grid of sqare cells that can be alive or dead, and the user defines the inital layout.
When the simulation is run, the following rules are applied to each cell:
1. If a cell has less than 2 living neighbors then it dies
2. If a cell has more than 4 neighbors then it dies
3. If a cell has exactly 3 neighbors then it comes to life

This process repeats to create new arrangements of cells.
## How to use:
To edit the cells, click on the tool you want to use and edit the cells using the mouse.

To start / pause the simulation, press space.

Press R To reset the simulation.

Press enter to step the simulation forward one generation.
### Saving / loading patterns:
Press the save button (down arrow) to save the current pattern. When you press it go to the console and enter the name you want to save it as.

To load a saved pattern, press the load button (up arrow). Then go to the console and enter the name of the save you want to load.
