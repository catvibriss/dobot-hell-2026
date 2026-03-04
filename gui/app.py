from tkinter import PhotoImage
import customtkinter as ctk
from PIL import Image
from utils import sorting
import state
import asyncio

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def label_image(master: any, path: str, size: tuple[int, int], rotate: int = 0) -> ctk.CTkLabel:
    img = Image.open(path).convert("RGBA")
    img = img.rotate(rotate)
    img = img.resize(size, Image.Resampling.LANCZOS)
    
    ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=size)
    
    label = ctk.CTkLabel(master=master, text="", image=ctk_image, fg_color="transparent")
    label.image = ctk_image
    
    return label

class WarningPopup(ctk.CTkToplevel):
    def __init__(self, parent, warn_text):
        super().__init__(parent)
        
        self.title("Warning!")
        self.geometry("300x1")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color="#836F00")
        
        inner_frame = ctk.CTkFrame(self, fg_color=ctk.ThemeManager.theme["CTk"]["fg_color"])
        inner_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.label = ctk.CTkLabel(inner_frame, text=warn_text, wraplength=280, justify="center")
        self.label.pack(pady=10, padx=20)
        
        self.button = ctk.CTkButton(inner_frame, text="OK", command=self.destroy, width=80)
        self.button.pack(pady=(0, 10), padx=10)

        self.update_idletasks() 

        width = self.winfo_reqwidth()   
        height = self.winfo_reqheight()
        
        self.geometry(f"{width}x{height}") 
        
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")

class DobotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("dobot-hell-2026")
        self.geometry("900x600")
        # self.resizable(False, False)

        # self.after(100, self.insert_icon) TODO: fix this shit

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.current_frame_name = None
        self.sidebar_pages = []
        self.sidebar_buttons = {}
        self.start_show = None

        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.create_pages()
        self.create_sidebar()

        self.show_frame(self.start_show)

    def insert_icon(self):
        self.icon = PhotoImage(file="./gui/icon.png", width=32, height=32)
        self.wm_iconphoto(True, self.icon)

    def create_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, sticky="nsew")
        sidebar_frame.pack_propagate(False)

        logo = ctk.CTkImage(light_image=Image.open("./gui/logo.png"), size=(120, 55))

        lbl_title = ctk.CTkLabel(sidebar_frame, text="", image=logo, compound="left")
        lbl_title.pack(pady=20)

        for name, text in self.sidebar_pages:
            btn = ctk.CTkButton(sidebar_frame, text=text, width=150, height=40, corner_radius=10,\
                                command=lambda n=name: self.show_frame(n))
            btn.pack(pady=5)
            self.sidebar_buttons[name] = btn

    def create_pages(self):
        self.home_page()
        self.camera_page()
        self.settings_page()

    def visual_zone(self, parent):
        frame = ctk.CTkFrame(master=parent, width=900, height=600, fg_color="transparent")
        frame.pack_propagate(False)

        base_path = "./gui/images"

        base_dobot = label_image(frame, f"{base_path}/dobot/offline.png", (128, 100))
        base_dobot.place(x=25, y=100)

        help_dobot = label_image(frame, f"{base_path}/dobot/offline.png", (128, 100), 90)
        help_dobot.place(x=125, y=10)

        return frame

    def home_page(self):
        frame_name = "main"
        frame = ctk.CTkFrame(self.main_area)
        
        ctk.CTkLabel(frame, text=f"well cum to {frame_name}", font=ctk.CTkFont(size=24)).pack(pady=20)

        # visual = self.visual_zone(parent=frame)
        # visual.pack()

        def start_button_event():
            cubes = start_cubes.get()
            try:
                cubes = int(cubes)
            except:
                popup = WarningPopup(app, "Введите целое кол-во кубиков!")
                return
            sorting.start_sorting(cubes=cubes)
    
        start_button = ctk.CTkButton(frame, command=start_button_event, text="СТАРТ!")
        start_cubes = ctk.CTkEntry(frame, placeholder_text="колво кубов")  

        start_button.pack()
        start_cubes.pack()

        def disable_all_action():
            state.BASE_DOBOT._stop_and_clear_queue()
            state.BASE_DOBOT.set_suction_cup(False)
            state.BASE_DOBOT.move(x=200, y=0, z=25)

            state.CONV.disable()

        emergency_stop = ctk.CTkButton(frame, command=disable_all_action, text="STOP🚨")
        emergency_stop.pack()

        def all_homing():
            state.BASE_DOBOT.homing()
            state.HELP_DOBOT.homing()
            asyncio.run(state.SORT_DOBOT.homing())

        homing_label = ctk.CTkLabel(frame, text="Вытащите DOBOT'ов из пазов перед калибровкой")
        homing_button = ctk.CTkButton(frame, text="Homing", command=all_homing)
        
        homing_label.pack()
        homing_button.pack()

        self.frames[frame_name] = frame
        self.sidebar_pages.append((frame_name, "main"))
        self.start_show = frame_name

    def camera_page(self):
        frame_name = "camera"
        frame = ctk.CTkFrame(self.main_area)

        self.frames[frame_name] = frame
        self.sidebar_pages.append((frame_name, "camera"))

    def settings_page(self):
        frame_name = "settings"
        frame = ctk.CTkFrame(self.main_area)
        
        ctk.CTkLabel(frame, text=f"well cum to {frame_name}", font=ctk.CTkFont(size=24)).pack(pady=20)

        self.frames[frame_name] = frame
        self.sidebar_pages.append((frame_name, "fgadfgasdfg"))

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()

        if name in self.frames:
            self.frames[name].pack(fill="both", expand=True)
            self.current_frame_name = name
                    
        for btn_name, btn_widget in self.sidebar_buttons.items():            
            if btn_name == name:
                btn_widget.configure(fg_color=("#3B8ED0", "#1F6AA5"), border_color=("#3B8ED0", "#1F6AA5"), border_width=2)
            else:
                btn_widget.configure(fg_color="transparent", border_width=0)

app = DobotApp()