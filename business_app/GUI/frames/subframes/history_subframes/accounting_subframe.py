import customtkinter
from business_app.GUI.utils import CtkTreeView
from business_app.database.controllers.trial_balance_controller import ObjTrialBalance
from datetime import date


class AccountingSubFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        n=15
        self.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=3, rowspan=3)
        self.grid_columnconfigure(tuple(range(n)), weight=1)
        self.grid_rowconfigure(tuple(range(n)), weight=1)
        dict_tb_options = ObjTrialBalance.get_available()

        def change_tb(*args):
            self.tv.destroy()
            display_option = self.display_options.get()
            self.trial_balance = ObjTrialBalance.from_db(dict_tb_options.get(self.option_date_menu.get()))
            if display_option == 'Trial Balance':
                data = self.trial_balance.data.fillna(" ")
            elif display_option == 'Balance Sheet':
                data = self.trial_balance.balance_sheet().fillna(" ")
                self.audit_btn.configure(state="normal")

            elif display_option == 'Income Statement':
                data = self.trial_balance.income_statement().fillna(" ")

            self.tv = CtkTreeView(self, data)
            self.tv.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=n, rowspan=n-1)

        def audit_button():
            if self.display_options.get() == 'Balance Sheet':
                self.tv.destroy()
                data = self.trial_balance.balance_sheet().audit()
                self.tv = CtkTreeView(self, data)
                self.tv.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=n, rowspan=n - 1)

        self.option_date_menu = customtkinter.CTkOptionMenu(self, values=list(dict_tb_options), command=change_tb)
        self.option_date_menu.grid(row=0, column=0, padx=10, pady=20)

        self.display_options = customtkinter.CTkOptionMenu(self,
                                                           values=["Trial Balance", "Balance Sheet", "Income Statement"],
                                                           command=change_tb)
        self.display_options.grid(row=0, column=1, padx=10, pady=20)

        self.trial_balance = ObjTrialBalance.from_db(list(dict_tb_options.values())[0])
        self.tv = CtkTreeView(self, self.trial_balance.data.fillna(" "))
        self.tv.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=n, rowspan=n-1)

        self.audit_btn = customtkinter.CTkButton(self, command=audit_button, state="disabled", text="Audit")
        self.audit_btn.grid(row=0, column=2, padx=10, pady=20)
