import customtkinter
from business_app.GUI.frames.subframes import EmptySubFrame


class BaseFrame(customtkinter.CTkFrame):
    def __init__(self, master, sub_frames_dict, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=0, column=1, padx=20, pady=20, sticky="nsew", rowspan=3, columnspan=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(0, minsize=0)
        self.grid_rowconfigure((1, 2), weight=1)

        def segmented_button_callback(value):
            self.sub_frame.destroy()
            self.sub_frame = sub_frames_dict.get(value)(self)

        self.segmented_button_var = customtkinter.StringVar()
        self.segmented_button = customtkinter.CTkSegmentedButton(self,
                                                                 values=list(sub_frames_dict),
                                                                 command=segmented_button_callback,
                                                                 variable=self.segmented_button_var)
        self.segmented_button.grid(row=0, column=0, padx=20, pady=20, columnspan=3)
        self.sub_frame = EmptySubFrame(master=self)