import customtkinter
from business_app.GUI.frames import *
customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Venteks Financial Proyections.py")

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w * 0.9, h * 0.9))

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Venteks Proyections",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_input_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame,command=self.sidebar_history_button_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_proj_button_event)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_past_proj_event)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        self.my_frame = EmptyFrame(master=self)
        self.my_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew", rowspan=3, columnspan=3)

        self.default_button_color = self.sidebar_button_1.cget('fg_color')
        self.pressed_button_color = ["#1f538d", "#133F71"]

        # set default values
        self.sidebar_button_1.configure(text="Inputs")
        self.sidebar_button_2.configure(text="History")
        self.sidebar_button_3.configure(text="Projections")
        self.sidebar_button_4.configure(text="Past Projections")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self, button, frame):
        self.my_frame.destroy()

        if button.cget('fg_color') == self.default_button_color:

            self.my_frame = frame(master=self)
            self.sidebar_button_1.configure(fg_color=self.default_button_color)
            self.sidebar_button_2.configure(fg_color=self.default_button_color)
            self.sidebar_button_3.configure(fg_color=self.default_button_color)
            self.sidebar_button_4.configure(fg_color=self.default_button_color)
            button.configure(fg_color=self.pressed_button_color)

        else:
            self.my_frame = EmptyFrame(master=self)
            self.sidebar_button_1.configure(fg_color=self.default_button_color)
            self.sidebar_button_2.configure(fg_color=self.default_button_color)
            self.sidebar_button_3.configure(fg_color=self.default_button_color)
            self.sidebar_button_4.configure(fg_color=self.default_button_color)

    def sidebar_input_button_event(self):
        self.sidebar_button_event(self.sidebar_button_1, InputFrame)

    def sidebar_history_button_event(self):
        self.sidebar_button_event(self.sidebar_button_2, HistoryFrame)

    def sidebar_proj_button_event(self):
        self.sidebar_button_event(self.sidebar_button_3, ProjectionFrame)

    def sidebar_past_proj_event(self):
        self.sidebar_button_event(self.sidebar_button_4, PastProjectionsFrame)


if __name__ == "__main__":
    app = App()
    app.mainloop()
