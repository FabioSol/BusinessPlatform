import customtkinter
from business_app.database.controllers.trial_balance_controller import ObjTrialBalance

class AccountingSubFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=3, rowspan=3)

        json_tb = ObjTrialBalance.get_available()
        self.trial_balances_labels = []

        def file_explorer():
            ...

        for n, key in enumerate(json_tb):
            label = customtkinter.CTkLabel(self,text=key)
            label.grid(row=n, column=1, padx=10, pady=10)
            button = customtkinter.CTkButton(self, text="Replace")
            button.grid(row=n, column=2, padx=10, pady=10)
            self.trial_balances_labels += [label]
