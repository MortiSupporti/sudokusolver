# sudokusolver

This application reads Sudoku images and sovles them.
It has 3 run modes. 2 for your computer and 1 for building an Android APK. BUILDOZER GOES BRRRRR!

# TODO for mode 2
- Implement a visible frame for the camera activity, so that the user has an indicator where I want the sudoku area to be located.
- Implement a function that crops the framed area. Crop, maybe create a border, resize Image.
- Re-do the global variables of the gui. Issue with placing them inside a class, because I want to clean up and need to clean up before class is destroyed. Currently clean up comes after destruction of the class.
- At the very end, add "ABOUT" button with information
