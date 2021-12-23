import os
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import solving_algorithms as sa
import image_recognition as ir
kivy.require("1.9.2")

## RICEFIELD 
## einige funktionen sind noch in main
## wie die hier einbauen ohne alles doppelt im code zu haben
## import sa und ir

## todo:

## rahmen/frame bei camera screen
## danach logik fürs bild um nur den ausschnitt zu haben
## ggf. danach ränder wegfiltern
## 1

## 
## andere methode um bilder zu regeln


sm = None
capture_path = "images/temp_captured.png"
solve_path = "images/temp_solved.png"

class SudokuSolverApp(App):
    def __init__(self, **kwargs):
        super(SudokuSolverApp, self).__init__(**kwargs)

    def build(self):
        return sm

class SudokuGUITemplate(Screen):
    gui_loaded_image = None
    gui_solved_image = None
    busy_path = "busy.gif"
    capture_path = capture_path
    solve_path = solve_path
    target_dict = {
        "start":    "NO IMAGE DETECTED. LOAD IMAGE.",
        "loaded":   capture_path,
        "solved":   solve_path,
        "busy":     busy_path}
    def __init__(self, **kwargs):
        super(SudokuGUITemplate, self).__init__(**kwargs)

    def switch_screen_to(self, target):
        if target == "camera":
            self.ids.left_image.source = self.target_dict["loaded"]
            sm.current = target
            return
        if sm.current == "camera":
            sm.current = "start"
            return
        self.ids.left_image.source = self.target_dict[target]
        return

    def capture_image(self):
        self.ids.camera.export_to_png(self.capture_path)
        sm.get_screen("start").ids.right_image.reload()
        self.gui_loaded_image = ir.load_image(self.capture_path)
        self.switch_screen_to("loaded")
        return

    def popup_file_view(self):
        content = SudokuGUIFileChooserLoad(load=self.load_image, cancel=self.popup_close)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        return

    def popup_file_save(self):
        content = SudokuGUIFileChooserSave(save=self.save_image, cancel=self.popup_close)
        self._popup = Popup(title="Save file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        return

    def popup_close(self):
        self._popup.dismiss()
        return

    def load_image(self, _path, filename):
        self.gui_loaded_image = ir.load_image(filename[0])
        self.ids.left_image.source = filename[0]
        self._popup.dismiss()
        return

    def save_image(self, path, filename):
        save_location = path+"/"+filename
        ir.save_output_image(self.gui_solved_image, save_location)
        self._popup.dismiss()
    

    def solve_sudoku(self):
        #busy refresh vom sm funktioniert nicht
        self.ids.right_image.source = "busy.gif"
        input_sudoku_pack = ir.image_proc_routine(self.gui_loaded_image)
        empty_sudoku = [x[:] for x in input_sudoku_pack[0]]
        sa.rsolv_recursive_solving(input_sudoku_pack[0])
        self.gui_solved_image  = ir.draw_output_image(input_sudoku_pack[2], input_sudoku_pack[1], empty_sudoku, input_sudoku_pack[0])
        ir.save_output_image(self.gui_solved_image, self.solve_path)
        self.ids.right_image.source = self.solve_path
        return


class SudokuGUIStart(SudokuGUITemplate):
    pass

class SudokuGUICamera(SudokuGUITemplate):
    pass

class SudokuGUIFileChooserLoad(FloatLayout):
    load = ObjectProperty()
    cancel = ObjectProperty()

class SudokuGUIFileChooserSave(FloatLayout):
    save = ObjectProperty()
    save_name = ObjectProperty()
    cancel = ObjectProperty()

def gui_init():
    global sm
    Builder.load_file("sudoku_gui.kv")
    sm = ScreenManager(transition=NoTransition())
    sm.add_widget(SudokuGUIStart(name="start"))
    sm.add_widget(SudokuGUICamera(name="camera"))
    return

def shut_down_clean_up():
    if os.path.isfile(solve_path): 
        os.remove(solve_path)
    if os.path.isfile(capture_path):
        os.remove(capture_path)
    return
