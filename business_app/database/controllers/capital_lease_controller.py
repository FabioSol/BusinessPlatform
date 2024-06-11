from datetime import date
import pandas as pd
import numpy_financial as npf
from scipy.optimize import root_scalar

pd.set_option('display.max_columns', None)
pd.options.display.float_format = '{:,.2f}'.format


class ObjCapitalLease:
    def __init__(self,
                 type_of_capital_lease,
                 lender_name,
                 start_date,
                 end_date,
                 amount,
                 interest_rate,
                 number_of_payments,
                 general_expenses,
                 deposit,
                 residual,
                 initial_payment):
        self.type_of_capital_lease = type_of_capital_lease
        self.lender_name = lender_name
        self.start_date = start_date
        self.end_date = end_date
        self.amount = amount
        self.interest_rate = interest_rate
        self.number_of_payments = number_of_payments
        self.general_expenses = general_expenses
        self.deposit = deposit
        self.residual = residual
        self.initial_payment = initial_payment

    def calculate_payments(self):
        # Calculate monthly interest rate
        monthly_interest_rate = self.interest_rate / 12
        monthly_payment = npf.pmt(monthly_interest_rate, self.number_of_payments, -self.amount, self.residual)

        payments = [self.initial_payment - amount]
        dates = [self.start_date]
        principal = [0]
        interest_payment = [0]
        principal_payment = [0]

        current_date = self.start_date
        for i in range(self.number_of_payments + 1):
            try:
                current_date = date(current_date.year, current_date.month + 1,
                                    current_date.day)  # Assuming a month has 30 days for simplicity
            except ValueError:
                current_date = date(current_date.year + 1, 1, current_date.day)

            if i == 0:
                principal += [self.amount]
            else:
                principal += [principal[-1] - principal_payment[-1]]

            if i == self.number_of_payments:
                dates += [current_date]
                interest_payment += [0]
                payments += [self.residual - self.deposit]
                if payments[-1] > 0:
                    principal_payment += [principal[-1]]
                else:
                    principal_payment += [0]
            else:
                dates += [current_date]
                interest_payment += [principal[-1] * monthly_interest_rate]
                principal_payment += [monthly_payment - interest_payment[-1]]
                payments += [monthly_payment]

        return pd.DataFrame({'date': dates,
                             'principal': principal,
                             'principal_payment': principal_payment,
                             'interest_payment': interest_payment,
                             'payments': payments})

    @classmethod
    def from_pure_lease(cls,
                        lender_name,
                        start_date,
                        amount,
                        number_of_payments,
                        deposit,
                        residual,
                        monthly_rent,
                        initial_payment):

        interest_rate = root_scalar(lambda x: (npf.pmt(x / 12, number_of_payments, -amount, residual) - monthly_rent),
                                    bracket=[0, 1]).root
        err = (npf.pmt(interest_rate / 12, number_of_payments, -amount, residual) - monthly_rent) ** 2
        end_date = start_date
        for _ in range(number_of_payments):
            try:
                end_date = date(end_date.year, end_date.month + 1,
                                end_date.day)  # Assuming a month has 30 days for simplicity
            except ValueError:
                end_date = date(end_date.year + 1, 1, end_date.day)

        if err < 0.001:
            obj = ObjCapitalLease(type_of_capital_lease="Pure lease",
                                  lender_name=lender_name,
                                  start_date=start_date,
                                  end_date=end_date,
                                  amount=amount,
                                  interest_rate=interest_rate,
                                  number_of_payments=number_of_payments,
                                  general_expenses=0,
                                  deposit=deposit,
                                  residual=residual,
                                  initial_payment=initial_payment)
            return obj


type_of_capital_lease = "credito"
lender_name = "Pto A"
start_date = date(2019, 11, 1)
end_date = date(2023, 12, 1)
amount = 2590000
interest_rate = 0.270000094416582
number_of_payments = 48
general_expenses = 0
deposit = 88791.23
residual = 1.16
initial_payment = 77700

"""
type_of_capital_lease = "credito"
lender_name = "SQN-1"
start_date = date(2020, 2, 1)
end_date = date(2022, 12, 1)
amount = 2536519.99
interest_rate =.244308793584281
number_of_payments = 36
general_expenses = 0
deposit = 90171.98
residual = 519240.50
initial_payment = 89539.16"""

obj = ObjCapitalLease(type_of_capital_lease,
                      lender_name,
                      start_date,
                      end_date,
                      amount,
                      interest_rate,
                      number_of_payments,
                      general_expenses,
                      deposit,
                      residual,
                      initial_payment)


a=(obj.calculate_payments())

lender_name = "Pto A"
start_date = date(2019, 11, 1)
amount = 2590000
number_of_payments = 48
deposit = 88791.23
residual = 1.16
monthly_rent = 88791.23 #mas iva de la renta
initial_payment = 77700

# pure lease, financial lease, simple credit,

obj = ObjCapitalLease.from_pure_lease(lender_name, start_date, amount, number_of_payments, deposit, residual,
                                      monthly_rent, initial_payment)
b=(obj.calculate_payments())
print(a)
print(b)
