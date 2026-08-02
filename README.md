# The Game of Life
This is a Python implementation of John Conway's Game of Life.

The game is played on a grid of sqare cells that can be $${\color{#00ff00}\text{alive}}$$ or $${\color{#ff0000}\text{dead}}$$, and the user defines the inital layout.
When the simulation is run, the following rules are applied to each cell:
1. If a cell has less than $${\color{#ff0000}\text{2}}$$ living neighbors then it $${\color{#ff0000}\text{dies}}$$
2. If a cell has more than $${\color{#ff0000}\text{4}}$$ living neighbors then it $${\color{#ff0000}\text{dies}}$$
3. If a cell has exactly $${\color{#00ff00}\text{3}}$$ living neighbors then it comes to $${\color{#00ff00}\text{life}}$$

This process repeats to create the next generation.
## How to use:
To edit the cells, click on the tool you want to use and edit the cells using the <strong>mouse</strong>.

To start / pause the simulation, press <strong>space</strong>.

Press <strong>R</strong> To reset the simulation <strong>$${\color{#ff0000}\text{(WARNING: Any unsaved data will be lost! Save before you clear!)}}$$</strong>.

Press <strong>enter</strong> to step the simulation forward one generation.
### Saving / loading patterns:
Press the save button (down arrow) to save the current pattern. When you press it, the file manager should open. When it does, enter what you want to save it as and press save.

To load a saved pattern, press the load button (up arrow). When the file window opens, double-click the file you want to open.

Note: When you close the window, the program will backup the current grid, then load it again when you re-open it.
