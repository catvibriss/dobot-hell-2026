from tkinter import PhotoImage
import customtkinter as ctk
from PIL import Image

# ctk.set_appearance_mode("Dark")
# ctk.set_default_color_theme("blue")

class DobotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("dobot-hell-2026")
        self.geometry("900x600")
        self.resizable(False, False)

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

    def home_page(self):
        frame_name = "main"
        frame = ctk.CTkFrame(self.main_area)
        
        ctk.CTkLabel(frame, text=f"well cum to {frame_name}", font=ctk.CTkFont(size=24)).pack(pady=20)

        self.frames[frame_name] = frame
        self.sidebar_pages.append((frame_name, "main"))
        self.start_show = frame_name

    def camera_page(self):
        frame_name = "camera"
        frame = ctk.CTkFrame(self.main_area)
        
        ctk.CTkLabel(frame, text=f"well cum to {frame_name}", font=ctk.CTkFont(size=24)).pack(pady=20)

        self.frames[frame_name] = frame
        self.sidebar_pages.append((frame_name, "FDFG"))

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