#!/bin/python3.6
"""Image identifier for sudoku
reads a sudoku image and identifies its content
solves the sudoku. Comes with 3 different modes for different environments,

modes:
    0               terminal / text only
    1               graphical
    2               android

versions:
    python          3.6.9
    opencv          4.2.0
    pytesseract     0.3.8
    numpy           1.13.3
    imutils         0.5.4
    kivy            2.0.0"""
import time
import sys
import solving_algorithms as sa
import image_recognition as ir
import sudoku_gui as gui

def main():
    run_mode = 2
    image_path = "images/bla.png"
    available_modes = [0,1,2]
    if len(sys.argv) > 2:
        run_mode, image_path = sys.argv[1:3]
        if run_mode not in available_modes:
            print("ILLEGAL MODE. POLICE IS INFORMED.")
            return
    mode_cases = {
        0: terminal_only_run,
        1: graphical_run,
        2: android_run}
    mode_cases[run_mode](image_path)
    return

def terminal_only_run(image_path):
    """terminal_only_run(image_path)
    -> None

    reads and solves sudoku found at image_path
    text only, output includes read sudoku, solved sudoku, times"""
    start_time = time.time()
    loaded_image = ir.load_image(image_path)
    input_sudoku_pack = ir.image_proc_routine(loaded_image)
    fin_read_time = time.time()
    print("-----")
    print("READ SUDOKU")
    sa.print_sudoku(input_sudoku_pack[0])
    print("-----")
    sa.rsolv_recursive_solving(input_sudoku_pack[0])
    fin_solv_time = time.time()
    print("SOLVED SUDOKU")
    sa.print_sudoku(input_sudoku_pack[0])
    print("-----")
    print("Time to read Sudoku: {:.3f}s".format(fin_read_time-start_time))
    print("Time to solve Sudoku: {:.3f}s".format(fin_solv_time-fin_read_time))
    print("-----")
    return

def graphical_run(image_path):
    """graphical_run(image_path)
    -> None

    reads and solves sudoku found at image_path
    displays solved sudoku, terminal output times
    code can be modified to display reading steps
    for this see image_recognition.visualizing_current_image_processing"""
    start_time = time.time()

    loaded_image = ir.load_image(image_path)
    input_sudoku_pack = ir.image_proc_routine(loaded_image)
    fin_read_time = time.time()

    empty_sudoku = [x[:] for x in input_sudoku_pack[0]] ## deep copy
    ##each element of the old list becomes an element of the new list
    sa.rsolv_recursive_solving(input_sudoku_pack[0])
    solved_sudoku = input_sudoku_pack[0]
    output_image = ir.draw_output_image(input_sudoku_pack[2], input_sudoku_pack[1], empty_sudoku, solved_sudoku)
    fin_solv_time = time.time()

    print("Time to read Sudoku: {:.3f}s".format(fin_read_time-start_time))
    print("Time to solve Sudoku: {:.3f}s".format(fin_solv_time-fin_read_time))

    ir.display_image_and_wait(output_image)

def android_run(_):
    """android_run(_)
    -> None

    run for android
    allows to take pictures of sudoku
    processes image, solves sudoku, shows sudoku
    temporarily creates images and cleans them at shutdown
    all within a bundled app"""
    gui.gui_init("last_captured_image.png", "last_solved_image.png")
    sudoku_solver_inst = gui.SudokuSolverApp()
    sudoku_solver_inst.run()
    gui.shut_down_clean_up()
    return

main()
