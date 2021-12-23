# sudokusolver

This application reads Sudoku images and solves them.
It has 3 run modes:
- Text-only mode for shell. Output will be in shell.
- Graphical mode for shell. You will get a solved image of your Sudoku.
- GUI mode. Gets your image by your device camera or loads image with file manager. Output will be an image.

# TODO for mode 2
- Implement a visible frame for the camera activity, so that the user has an indicator where I want the sudoku area to be located.
- Pre-selektor for Image, so user can select only important areas.
- Implement a function that crops the framed area. Crop, maybe create a border, resize Image.
- Re-do the global variables of the gui. Issue with placing them inside a class, because I want to clean up and need to clean up before class is destroyed. Currently clean up comes after destruction of the class.
- Busy is not being displayed
- Maybe rework IR so it can read test_02.png
- At the very end, add "ABOUT" button with information
