import os
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import solving_algorithms as sa
import image_recognition as ir
kivy.require("1.9.0")

## RICEFIELD 
## einige funktionen sind noch in main
## wie die hier einbauen ohne alles doppelt im code zu haben
## import sa und ir

## todo:

## rahmen/frame bei camera screen
## danach logik fürs bild um nur den ausschnitt zu haben
## ggf. danach ränder wegfiltern
## 1
## android rechte photo und dateien
## 
## andere methode um bilder zu regeln


from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
sm = None
capture_path = "images/last_captured_image.png"
solve_path = "images/last_solved_image.png"

class SudokuSolverApp(App):
    def __init__(self, **kwargs):
        super(SudokuSolverApp, self).__init__(**kwargs)

    def build(self):
        return sm

class SudokuGUITemplate(Screen):
    gui_loaded_image = None
    gui_solved_image = None
    capture_path = capture_path
    solve_path = solve_path
    target_dict = {
        "start":    "NO IMAGE DETECTED. LOAD IMAGE.",
        "loaded":   capture_path,
        "solved":   solve_path,
        "busy":     "images/busy.gif",
        "camera":   111}

    def __init__(self, **kwargs):
        super(SudokuGUITemplate, self).__init__(**kwargs)

    def switch_screen_to(self, target):
        if target == "camera":
            self.ids.center_image.source = self.target_dict["loaded"]
            sm.current = target
            return
        if sm.current == "camera":
            sm.current = "start"
            return
        self.ids.center_image.source = self.target_dict[target]
        return

    def capture_image(self):
        self.ids.camera.export_to_png(self.capture_path)
        sm.get_screen("start").ids.center_image.reload()
        self.gui_loaded_image = ir.load_image(self.capture_path)
        self.switch_screen_to("loaded")
        return
    
    def solve_sudoku(self):
        input_sudoku_pack = ir.image_proc_routine(self.gui_loaded_image)
        empty_sudoku = [x[:] for x in input_sudoku_pack[0]]
        sa.rsolv_recursive_solving(input_sudoku_pack[0])
        self.gui_solved_image  = ir.draw_output_image(input_sudoku_pack[2], input_sudoku_pack[1], empty_sudoku, input_sudoku_pack[0])
        ir.save_output_image(self.gui_solved_image, self.solve_path)
        self.switch_screen_to("solved")
        return


class SudokuGUIStart(SudokuGUITemplate):
    pass

class SudokuGUICamera(SudokuGUITemplate):
    pass

def gui_init(input_capture_path="images/last_captured_image.png", input_solve_path="images/last_solved_image.png"):
    global sm, capture_path, solve_path
    capture_path = input_capture_path 
    solve_path = input_solve_path
    Builder.load_file("sudoku_gui.kv")
    sm = ScreenManager(transition=NoTransition())
    sm.add_widget(SudokuGUIStart(name="start"))
    sm.add_widget(SudokuGUICamera(name="camera"))
    return

def shut_down_clean_up():
    os.remove(capture_path)
    os.remove(solve_path)
    return
