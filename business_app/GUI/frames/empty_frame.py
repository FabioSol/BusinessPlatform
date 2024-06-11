import customtkinter


class EmptyFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=0, column=1, padx=20, pady=20, sticky="nsew", rowspan=3, columnspan=3)
