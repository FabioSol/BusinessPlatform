import customtkinter


class ClientSubFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=3, rowspan=3)
