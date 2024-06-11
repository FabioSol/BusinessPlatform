import customtkinter
from tkinter import ttk
import pandas as pd
from customtkinter.windows.widgets.appearance_mode.appearance_mode_tracker import AppearanceModeTracker


class CtkTreeView(customtkinter.CTkFrame):
    def __init__(self, master, df: pd.DataFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.df = df
        self.tv = None
        self.scroll_x = None
        self.scroll_y = None
        self.style = []
        self.replot()
        self._draw = self.draw

    def draw(self, no_color_updates=False):
        super()._draw(no_color_updates)
        self.replot()

    def replot(self):
        if self.tv:
            self.tv.destroy()
        if self.scroll_x:
            self.scroll_x.destroy()
        if self.scroll_y:
            self.scroll_y.destroy()

        mode = AppearanceModeTracker.get_mode()
        color1 = self._fg_color[mode]
        color2 = self._bg_color[mode]
        font_c = ("black", "white")[mode]
        blue = ("#3B8ED0", "#1F6AA5")[mode]

        self.style = ttk.Style()
        self.style.configure("Treeview",
                             background=color2,
                             foreground=font_c,
                             fieldbackground=color1)
        self.style.configure("Treeview.Heading",
                             background=color2,
                             foreground="black",
                             fg=color2,
                             bg=color2,
                             fieldbackground=color2)

        self.style.map('Treeview', background=[('selected', blue)])

        self.tv = ttk.Treeview(self)
        self.tv.place(relheight=1, relwidth=1)
        self.scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tv.yview)
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tv.xview)
        self.tv.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_x.pack(side="bottom", fill="x")
        self.scroll_y.pack(side="right", fill="y")

        if isinstance(self.df.index, pd.MultiIndex):
            self.tv["column"] = list(self.df.index.names) + list(self.df.columns)
        else:
            self.tv["column"] = list(self.df.columns)

        self.tv["show"] = "headings"
        for column in self.tv["columns"]:
            self.tv.heading(column, text=column)

        df_rows = self.df.list_for_tree()
        color = color2
        self.tv.tag_configure(color, background=color)
        for row in df_rows:
            color = color1 if color == color2 else color2
            self.tv.insert("", "end", values=row, tag=color)
        self.tv.insert("", "end", values=[" " for _ in self.tv["show"]])
