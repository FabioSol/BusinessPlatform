import re
import pandas as pd
from datetime import date
from business_app import files_path
from business_app.database import db
from business_app.database.schemas import AccountingCode, TrialBalanceValue, Month
from business_app.utils.decorators import tabulate, dictionary
from peewee import DoesNotExist, IntegrityError
import xlsxwriter
import os
import warnings

pd.set_option('display.max_columns', None)
pd.options.display.float_format = '{:,.2f}'.format
warnings.simplefilter(action='ignore', category=FutureWarning)


def list_for_tree(self):
    if isinstance(self.index, pd.MultiIndex):
        idx = tuple(0 for _ in range(len(self.index[0])))
        past_idx = idx
        matrix = []
        for reg_idx, row in self.iterrows():
            idx = tuple(" " if i == j else i for i, j in zip(reg_idx, past_idx))
            past_idx = reg_idx
            formatted_row = []
            for val in row.fillna(" ").values:
                if isinstance(val, (int, float)):

                    if pd.isna(val):
                        formatted_row.append(" ")
                    else:
                        formatted_row.append(f'${val:,.2f}')
                else:
                    formatted_row.append(val)
            matrix.append(list(idx) + formatted_row)
        return matrix
    else:
        # Assuming self is a DataFrame
        formatted_values = self.applymap(lambda x: f'${x:,.2f}' if isinstance(x, (int, float)) else x)
        return formatted_values.fillna(" ").to_numpy().tolist()


pd.DataFrame.regex = lambda self, regex: self[self.index.to_series().apply(lambda x: bool(re.match(regex, x)))]
pd.DataFrame.list_for_tree = list_for_tree


class ObjTrialBalance:
    def __init__(self,
                 date_month: date,
                 data: pd.DataFrame):
        req_cols = ['Name', 'Initial balance Debitor', 'Initial balance Creditor', 'Debits', 'Credits',
                    'Final balance Debitor', 'Final balance Creditor']
        if all(col in data.columns for col in req_cols) & (len(data.columns) == len(req_cols)) & \
                all(data.index.to_series().apply(lambda x: bool(re.match(r'^\d{3}-\d{2}-\d{1}', x)))):
            self.date_month = date_month
            self.data = data
        else:
            raise ValueError(f"Wrong df format, the only columns should be: {req_cols}")

    @staticmethod
    def account_code_save(account_number, account_name, account_type, account_model):
        try:
            ac = AccountingCode.get(AccountingCode.account_number == account_number)
            if ac.account_name == account_name:
                return ac
            else:
                raise DoesNotExist
        except DoesNotExist:
            return AccountingCode.create(account_number=account_number,
                                         account_name=account_name,
                                         account_type=account_type,
                                         account_model=account_model)

    def save(self, overwrite=False):
        m = Month.get(Month.month_date == self.date_month)
        for row in self.data.iterrows():
            account = row[0]
            name = row[1]['Name']
            ib_d = row[1]['Initial balance Debitor']
            ib_c = row[1]['Initial balance Creditor']
            debits = row[1]['Debits']
            credits = row[1]['Credits']
            fb_d = row[1]['Final balance Debitor']
            fb_c = row[1]['Final balance Creditor']
            ac = ObjTrialBalance.account_code_save(account, name, "None", "Default")
            if pd.isna(ib_d) & pd.isna(fb_d) & pd.isna(ib_c) & pd.isna(fb_c):
                pass
            elif pd.isna(ib_d) & pd.isna(fb_d):
                try:
                    TrialBalanceValue.create(month=m.id,
                                             account=ac.id,
                                             initial_balance=ib_c,
                                             debits=debits,
                                             credits=credits,
                                             final_balance=fb_c,
                                             is_creditor=True)
                except IntegrityError:
                    if overwrite:
                        TrialBalanceValue.update(month=m.id,
                                                 account=ac.id,
                                                 initial_balance=ib_c,
                                                 debits=debits,
                                                 credits=credits,
                                                 final_balance=fb_c,
                                                 is_creditor=True)
                    else:
                        pass
            elif pd.isna(ib_c) & pd.isna(fb_c):
                try:
                    TrialBalanceValue.create(month=m.id,
                                             account=ac.id,
                                             initial_balance=ib_d,
                                             debits=debits,
                                             credits=credits,
                                             final_balance=fb_d,
                                             is_creditor=False)
                except IntegrityError:
                    if overwrite:
                        TrialBalanceValue.update(month=m.id,
                                                 account=ac.id,
                                                 initial_balance=ib_d,
                                                 debits=debits,
                                                 credits=credits,
                                                 final_balance=fb_d,
                                                 is_creditor=False)
                    else:
                        pass
            else:
                raise ValueError(f"The account {name} must have values for debitor or creditor, not both")

    def delete(self):
        m = Month.get(Month.month_date == self.date_month).id
        q = f"DELETE FROM TrialBalanceValue WHERE TrialBalanceValue.month_id == '{m.id}' "
        db.execute_sql(q)

    @classmethod
    def from_xlsx(cls, path: str, date_month: date):

        df = pd.read_excel(path,
                           skiprows=[0, 1, 2, 3, 4, 5],
                           names=['Name', 'Initial balance Debitor', 'Initial balance Creditor', 'Debits', 'Credits',
                                  'Final balance Debitor', 'Final balance Creditor']).dropna()

        numeric_cols = ['Initial balance Debitor', 'Initial balance Creditor',
                        'Debits', 'Credits', 'Final balance Debitor', 'Final balance Creditor']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        trial_balance = cls(date_month=date_month, data=df)

        return trial_balance

    @classmethod
    def from_db(cls, month_date: date):

        @tabulate
        def get_tb():
            q = f"SELECT account_number, account_name, initial_balance, debits, credits, final_balance, is_creditor " \
                f"FROM Month " \
                f"INNER JOIN TrialBalanceValue ON Month.id=TrialBalanceValue.month_id " \
                f"INNER JOIN accountingcode ON accountingcode.id =  TrialBalanceValue.account_id " \
                f"WHERE Month.month_date = '{month_date.isoformat()}' ;"
            return db.execute_sql(q)

        def decompress(df):
            dec_df = pd.DataFrame()
            dec_df['account_number'] = df['account_number']
            dec_df['Name'] = df['account_name']
            dec_df['Initial balance Debitor'] = df[df['is_creditor'] == 0]['initial_balance']
            dec_df['Initial balance Creditor'] = df[df['is_creditor'] == 1]['initial_balance']
            dec_df['Debits'] = df['debits']
            dec_df['Credits'] = df['credits']
            dec_df['Final balance Debitor'] = df[df['is_creditor'] == 0]['final_balance']
            dec_df['Final balance Creditor'] = df[df['is_creditor'] == 1]['final_balance']
            dec_df.set_index('account_number', drop=True, inplace=True)
            dec_df.index.name = None
            return dec_df

        data = decompress(get_tb())
        return cls(date_month=month_date, data=data)

    @staticmethod
    def auto_migrate():
        dir_path = files_path + "/trial_balances"
        paths = [dir_path + "/" + file for file in os.listdir(dir_path) if file.endswith('.xlsx')]
        for p in paths:
            month = int(p[-10:-8])
            year = (int(p[-7:-5]) + 2000)
            obj = ObjTrialBalance.from_xlsx(p, date(year, month, 1))
            obj.save()

    @staticmethod
    def get_all():
        months = list(ObjTrialBalance.get_available().values())
        return [ObjTrialBalance.from_db(i) for i in months]

    @staticmethod
    def get_available():
        q = "SELECT DISTINCT (month.month_date) " \
            "FROM month INNER JOIN trialbalancevalue ON month.id=trialbalancevalue.month_id"
        return {i[0]: date.fromisoformat(i[0]) for i in db.execute_sql(q).fetchall()}

    def balance_sheet(self, with_totals=True):
        try:
            past_date = date(self.date_month.year, self.date_month.month - 1, self.date_month.day)
        except ValueError:
            past_date = date(self.date_month.year - 1, 12, self.date_month.day)

        balance = BalanceSheet(date_month=self.date_month)
        balance.index = pd.MultiIndex.from_tuples([], names=['Type of account', 'Subtype of account', 'Account'])
        types_of_account = ['100-00-000', '200-00-000', '300-00-000']
        sign_adjust = [1, -1, -1]
        types_names = []
        for t_ac in types_of_account:
            t_ac_name = self.data.loc[t_ac]['Name']
            types_names += [t_ac_name]
            subtypes_of_accounts = self.data.regex(fr"^({t_ac[:3]}-0[1-9]|1[1-9]\d)-000").index.to_list()
            if len(subtypes_of_accounts) > 0:
                for i, s_ac in enumerate(subtypes_of_accounts):
                    s_ac_name = self.data.loc[s_ac]['Name']
                    subtypes_with_ending = subtypes_of_accounts + [str(int(t_ac[0]) + 1) + t_ac[1:]]
                    subtype_df = self.data.loc[s_ac:subtypes_with_ending[i + 1]].regex(
                        f"^{s_ac[0]}(0[1-9]|[1-9][0-9])-00-000")
                    for _, row in subtype_df.iterrows():
                        row_filled = row.fillna(0)
                        initial_value = row_filled['Initial balance Debitor'] - row_filled['Initial balance Creditor']
                        final_value = row_filled['Final balance Debitor'] - row_filled['Final balance Creditor']
                        balance.loc[(t_ac_name, s_ac_name, row['Name']), 'Initial Date'] = initial_value
                        balance.loc[(t_ac_name, s_ac_name, row['Name']), 'Final Date'] = final_value

                    if with_totals:
                        st_row = self.data.loc[s_ac].fillna(0)
                        initial_value = st_row['Initial balance Debitor'] - st_row['Initial balance Creditor']
                        final_value = st_row['Final balance Debitor'] - st_row['Final balance Creditor']
                        balance.loc[(t_ac_name, s_ac_name, 'Total ' + s_ac_name), 'Initial Date'] = initial_value
                        balance.loc[(t_ac_name, s_ac_name, 'Total ' + s_ac_name), 'Final Date'] = final_value

            else:
                subtypes_of_accounts = self.data.regex(fr"^({t_ac[:1]}\d[1-9]-00)-000").index.to_list()
                for i, s_ac in enumerate(subtypes_of_accounts):
                    s_ac_name = self.data.loc[s_ac]['Name']
                    subtypes_with_ending = subtypes_of_accounts + [str(int(t_ac[0]) + 1) + t_ac[1:]]
                    subtype_df = self.data.loc[s_ac:subtypes_with_ending[i + 1]].regex(f"^{s_ac[:3]}-\d[1-9]-000")
                    for _, row in subtype_df.iterrows():
                        row_filled = row.fillna(0)
                        initial_value = row_filled['Initial balance Debitor'] - row_filled['Initial balance Creditor']
                        final_value = row_filled['Final balance Debitor'] - row_filled['Final balance Creditor']
                        balance.loc[(t_ac_name, s_ac_name, row['Name']), 'Initial Date'] = initial_value
                        balance.loc[(t_ac_name, s_ac_name, row['Name']), 'Final Date'] = final_value

                    if with_totals:
                        st_row = self.data.loc[s_ac].fillna(0)
                        initial_value = st_row['Initial balance Debitor'] - st_row['Initial balance Creditor']
                        final_value = st_row['Final balance Debitor'] - st_row['Final balance Creditor']
                        balance.loc[(t_ac_name, s_ac_name, 'Total ' + s_ac_name), 'Initial Date'] = initial_value
                        balance.loc[(t_ac_name, s_ac_name, 'Total ' + s_ac_name), 'Final Date'] = final_value
            if with_totals:
                t_row = self.data.loc[t_ac].fillna(0)
                initial_value = t_row['Initial balance Debitor'] - t_row['Initial balance Creditor']
                final_value = t_row['Final balance Debitor'] - t_row['Final balance Creditor']
                balance.loc[(t_ac_name, 'Total', ' '), 'Initial Date'] = initial_value
                balance.loc[(t_ac_name, 'Total', ' '), 'Final Date'] = final_value

        new_columns = {'Initial Date': past_date.isoformat(), 'Final Date': self.date_month.isoformat()}
        balance = balance.rename(columns=new_columns)
        idx = balance.index.get_level_values('Type of account')
        for name, sign in zip(types_names, sign_adjust):
            mask = idx == name
            balance.loc[mask] *= sign

        balance.date_month =self.date_month

        return balance

    def income_statement(self):
        df = IncomeStatement(self.date_month)
        df.index = pd.MultiIndex.from_tuples([], names=['Type of account', 'Subtype of account', 'Account'])
        types_level_0 = self.data.loc[['400-00-000', '500-00-000', '600-00-000', '700-00-000']]

        def get_row_value(row, adj=1):
            if pd.isna(row["Credits"]) & pd.isna(row["Debits"]):
                return 0
            elif pd.isna(row["Credits"]):
                return row["Debits"] * adj * -1
            elif pd.isna(row["Debits"]):
                return row["Credits"] * adj
            else:
                return row["Debits"] * adj * -1 + row["Credits"] * adj

        def get_cumulative_value(row, adj=1):
            if pd.isna(row["Final balance Creditor"]) & pd.isna(row["Final balance Debitor"]):
                return 0
            elif pd.isna(row["Final balance Creditor"]):
                return row["Final balance Debitor"] * adj * -1
            elif pd.isna(row["Final balance Debitor"]):
                return row["Final balance Creditor"] * adj
            else:
                return row["Final balance Debitor"] * adj * -1 + row["Final balance Creditor"] * adj

        for i, row0 in types_level_0.iterrows():
            types_level_1 = self.data.regex(fr"^{i[0]}(\d[1-9]|[1-9]\d)-00-000$")
            for e, row1 in types_level_1.iterrows():
                types_level_2 = self.data.regex(
                    fr"{e[:3]}-00-(\d\d[1-9]|\d[1-9]\d|[1-9]\d\d)$|{e[:3]}-(\d[1-9]|[1-9]\d)-000$")
                for j, row2 in types_level_2.iterrows():
                    df.loc[(row0['Name'], row1['Name'], row2['Name']), "Level 3"] = get_row_value(row2)
                    df.loc[(row0['Name'], row1['Name'], row2['Name']), "Cumulative 3"] = get_cumulative_value(row2)
                df.loc[(row0['Name'], row1['Name'], "Total " + row1['Name']), "Level 2"] = get_row_value(row1)
                df.loc[(row0['Name'], row1['Name'], "Total " + row1['Name']), "Cumulative 2"] = get_cumulative_value(
                    row1)
            df.loc[(row0['Name'], "Total " + row0['Name'], " "), "Level 1"] = get_row_value(row0)
            df.loc[(row0['Name'], "Total " + row0['Name'], " "), "Cumulative 1"] = get_cumulative_value(row0)
        return df


class BalanceSheet(pd.DataFrame):
    def __init__(self, date_month: date):
        super().__init__(columns=['Final Date', 'Initial Date'])
        self.date_month = date_month

    def audit(self):
        totals_calculated = self.groupby(level="Subtype of account").apply(lambda x: x.iloc[:-1].sum()).drop(
            index="Total")
        totals_saved = (self.groupby(level="Subtype of account").apply(lambda x: x.iloc[-1])).drop(index="Total")
        differences = totals_calculated - totals_saved

        types_totals = self.groupby(level="Type of account").apply(lambda x: x.iloc[-1])
        types_totals.loc['Condition'] = (types_totals.iloc[0] - (types_totals.iloc[1] + types_totals.iloc[2])).astype(
            int)
        totals = types_totals.reset_index().rename(columns={"Type of account": "Account"})
        differ = differences.reset_index().rename(columns={"Subtype of account": "Account"})
        differ.loc[len(differ) + 1] = [" "] * len(differ.columns)
        result = pd.concat([differ, totals], axis=0)
        return result

    def formatted_excel(self, name: str):
        workbook = xlsxwriter.Workbook(name)
        ws = workbook.add_worksheet(name="Balance general")

        def get_last_date():
            last_date = date(year=self.date_month.year, month=self.date_month.month, day=self.date_month.day)
            while True:
                try:
                    last_date = date(year=self.date_month.year, month=self.date_month.month, day=last_date.day + 1)
                except ValueError:
                    return last_date

        def add_header(worksheet):
            header_1 = workbook.add_format({"align": "center"})
            header_1.set_font("arial")
            worksheet.merge_range("B2:F2", "VENTEKS SA DE CV", header_1)
            header_2 = workbook.add_format({"align": "center"})
            header_2.set_font("arial")
            header_2.set_bottom()
            worksheet.merge_range("B3:D3",
                                  f"Pocisión Financiera, Balance General al {get_last_date().strftime('%d/%b/%Y')}",
                                  header_2)
            worksheet.merge_range("E3:F3", f"Fecha: {date.today().strftime('%d/%b/%Y')}", header_2)
            header_3 = workbook.add_format({'bold': True, "align": "center"})
            header_3.set_font("arial")
            header_3.set_bottom()
            for i in [ "B4", "C4", "D4", "E4", "F4"]:
                worksheet.write(i, None, header_3)

        def add_body(worksheet):
            r = 4
            c1=1
            c2=4


            f_value = workbook.add_format({'num_format': '$#,##0', 'border': 5, 'border_color': '#7AFDFF'})
            body_1 = workbook.add_format({'bold': True, 'italic': True, "align": "center"})
            body_1.set_font("arial")
            body_2 = workbook.add_format({ 'italic': True})
            body_2.set_font("arial")
            body_3 = workbook.add_format()
            body_3.set_font("arial")

            cap_struct = self.index.get_level_values(0).unique()
            assets, liabilities, equity = tuple(cap_struct)

            assets_df = self.loc[assets]
            liabilities_df = self.loc[liabilities]

            def parse_1(worksheet, df, row, column):
                total=0

                for i in df.index.get_level_values(0).unique():
                    worksheet.write(row, column, "    "+i, body_2)
                    row+=1
                    sub_df = df.loc[i]
                    for e in sub_df.iterrows():
                        worksheet.write(row, column, e[0], body_3)
                        worksheet.write(row, column + 1, e[1].to_list()[0], f_value)
                        row += 1
                        total=e[1].to_list()[0]
                    row+=1


                return row, total

            def parse_2(worksheet, name, row, column):
                compressed = self.loc[name].groupby(level=0).last()
                total=0
                for n,i in enumerate(compressed.iterrows()):
                    is_last = n==len(compressed)-1
                    if is_last:
                        row+=1
                        worksheet.write(row, column, "    "+i[0], body_2)
                        row+=1
                        total=i[1].to_list()[0]
                    else:
                        worksheet.write(row, column, i[0], body_3)
                    worksheet.write(row, column + 1, i[1].to_list()[0], f_value)
                    row+=1
                return row, total

            worksheet.write(r,c1,assets, body_1)
            worksheet.write(r, c2, liabilities, body_1)
            r+=1
            r2, assets_total = parse_1(ws,assets_df, r, c1)
            r, liabilities_total = parse_1(ws,liabilities_df, r, c2)
            r+=1
            worksheet.write(r, c2, equity, body_1)
            r+=1
            r, equity_total = parse_2(ws,equity,r,c2)

            r = max(r,r2)

            return r, assets_total, liabilities_total+equity_total


        def add_foot(worksheet, row, assets_total, li_eq_total):
            line = workbook.add_format({'bold': True, "align": "center"})
            line.set_font("arial")
            line.set_bottom()
            f_value = workbook.add_format({'num_format': '$#,##0', 'border': 5, 'border_color': '#7AFDFF'})
            foot = workbook.add_format({'bold': True, 'italic': True, "align": "center"})
            foot.set_font("arial")

            c1=1
            c2=4


            for i in [f"B{row}", f"C{row}", f"D{row}", f"E{row}", f"F{row}"]:
                worksheet.write(i, None, line)

            row+=1

            worksheet.write(row, c1, "SUMA DEL ACTIVO", foot)
            worksheet.write(row, c1+1, assets_total, f_value)
            worksheet.write(row, c2, "SUMA DEL PASIVO Y CAPITAL", foot)
            worksheet.write(row, c2+1, li_eq, f_value)

        add_header(ws)
        r, assets, li_eq = add_body(ws)
        add_foot(ws,r,assets,li_eq)


        ws.autofit()
        workbook.close()


class IncomeStatement(pd.DataFrame):
    def __init__(self, date_month: date):
        super().__init__(columns=['Level 1', 'Level 2', 'Level 3'])
        self.date_month = date_month

    def formatted_excel(self, name: str):
        workbook = xlsxwriter.Workbook(name)
        ws = workbook.add_worksheet(name="Estado de Resultados")

        bold_c = workbook.add_format({'bold': True, "align": "center"})
        bold_c.set_font("arial")

        def get_last_date():
            last_date = date(year=self.date_month.year, month=self.date_month.month, day=self.date_month.day)
            while True:
                try:
                    last_date = date(year=self.date_month.year, month=self.date_month.month, day=last_date.day + 1)
                except ValueError:
                    return last_date

        def add_header(worksheet):
            header_1 = workbook.add_format({"align": "center"})
            header_1.set_font("arial")
            worksheet.merge_range("B2:G2", "VENTEKS SA DE CV", header_1)
            header_2 = workbook.add_format({"align": "center"})
            header_2.set_font("arial")
            header_2.set_bottom()
            worksheet.merge_range("C3:E3",
                                  f"Estado de Resultados del {self.date_month.strftime('%d/%b/%Y')} al {get_last_date().strftime('%d/%b/%Y')}",
                                  header_2)
            worksheet.merge_range("F3:G3", f"Fecha: {date.today().strftime('%d/%b/%Y')}", header_2)
            header_3 = workbook.add_format({'bold': True, "align": "center"})
            header_3.set_font("arial")
            header_3.set_bottom()
            for i in ["B3", "B4", "C4", "D4", "E4", "F4", "G4"]:
                worksheet.write(i, None, header_3)
            worksheet.write("D4", "Periodo", header_3)
            worksheet.write("E4", "%", header_3)
            worksheet.write("F4", "Acumulado", header_3)
            worksheet.write("G4", "%", header_3)

        def add_body(worksheet):
            body_1 = workbook.add_format({'bold': True, 'italic': True, "align": "center"})
            body_1.set_font("arial")
            body_2 = workbook.add_format()
            body_2.set_font("arial")
            body_3 = workbook.add_format({'bold': True})
            body_3.set_font("arial")
            f_value = workbook.add_format({'num_format': '$#,##0', 'border': 5, 'border_color': '#7AFDFF'})
            f_percentage = workbook.add_format({'num_format': '0.00'})
            c = 2
            r = 5
            worksheet.write(r, c - 1, "Ingresos", body_1)
            first_levels = self.index.get_level_values(0).unique()
            income = self.loc[first_levels[0]]
            outcome = [0, 0]
            expendure = [0, 0]
            second_level_income = income.index.get_level_values(0).unique()
            income_total = income.loc[second_level_income[-1]].dropna(axis=1).iloc[0].tolist()

            def parse_1(df, second_level, r):
                for i in second_level:
                    r += 1
                    worksheet.write(r, c, " " + i, body_2)
                    for n, row in enumerate(df.loc[i].iterrows()):
                        not_last = n < len(tuple(df.loc[i].iterrows())) - 1
                        if not_last:
                            r += 1

                        level = row[1].first_valid_index()
                        value = row[1].loc[level]

                        if level == "Level 1":
                            if not_last:
                                worksheet.write(r, c, row[0], body_3)
                            cumulative = row[1].loc["Cumulative 1"]
                            worksheet.write(r, c + 3, cumulative, f_value)
                            worksheet.write(r, c + 4, 100 * cumulative / income_total[1], f_percentage)
                        elif level == "Level 2":
                            worksheet.write(r, c, row[0], body_2)
                            cumulative = row[1].loc["Cumulative 2"]
                            worksheet.write(r, c + 3, cumulative, f_value)
                            worksheet.write(r, c + 4, 100 * cumulative / income_total[1], f_percentage)
                        elif level == "Level 3":
                            worksheet.write(r, c, row[0], body_2)
                            cumulative = row[1].loc["Cumulative 3"]
                            worksheet.write(r, c + 3, cumulative, f_value)
                            worksheet.write(r, c + 4, 100 * cumulative / income_total[1], f_percentage)

                        worksheet.write(r, c + 1, value, f_value)
                        worksheet.write(r, c + 2, 100 * value / income_total[0], f_percentage)

                    r += 1
                r += 1
                return r

            r = parse_1(income, second_level_income, r)
            worksheet.write(r, c - 1, "Egresos", body_1)

            outcome_1 = self.loc[first_levels[1]]
            outcome = outcome_1.iloc[-1].dropna().to_list()
            second_level_outcome_1 = outcome_1.index.get_level_values(0).unique()
            r = parse_1(outcome_1, second_level_outcome_1, r)

            def parse_2(acc, r):
                worksheet.write(r, c, " " + acc, body_2)
                r += 1
                df = self.loc[acc]
                idxs = df.index.get_level_values(0).unique()[:-1]
                # gastos generales
                for idx in idxs:
                    worksheet.write(r, c, idx, body_2)
                    value, cumulative = (tuple(df.loc[idx].iloc[-1].dropna().tolist()))
                    expendure[0] += value
                    expendure[1] += cumulative
                    worksheet.write(r, c + 1, value, f_value)
                    worksheet.write(r, c + 2, 100 * value / income_total[0], f_percentage)
                    worksheet.write(r, c + 3, cumulative, f_value)
                    worksheet.write(r, c + 4, 100 * cumulative / income_total[1], f_percentage)

                    r += 1
                return r

            def parse_3(acc, r):
                df = self.loc[acc]
                value, cumulative = tuple(df.iloc[-1].dropna().tolist())
                expendure[0] += value
                expendure[1] += cumulative
                # RIF
                worksheet.write(r, c, acc, body_2)
                worksheet.write(r, c + 1, value, f_value)
                worksheet.write(r, c + 2, 100 * value / income_total[0], f_percentage)
                worksheet.write(r, c + 3, cumulative, f_value)
                worksheet.write(r, c + 4, 100 * cumulative / income_total[1], f_percentage)
                r += 2
                worksheet.write(r, c, " Total gastos", body_2)
                worksheet.write(r, c + 1, expendure[0], f_value)
                worksheet.write(r, c + 2, 100 * expendure[0] / income_total[0], f_percentage)
                worksheet.write(r, c + 3, expendure[1], f_value)
                worksheet.write(r, c + 4, 100 * expendure[1] / income_total[1], f_percentage)
                return r

            r = parse_2(first_levels[2], r)
            r = parse_3(first_levels[3], r)

            outcome[0] += expendure[0]
            outcome[1] += expendure[1]
            r += 2
            worksheet.write(r, c, " Total Egresos", body_2)
            worksheet.write(r, c + 1, outcome[0], f_value)
            worksheet.write(r, c + 2, 100 * outcome[0] / income_total[0], f_percentage)
            worksheet.write(r, c + 3, outcome[1], f_value)
            worksheet.write(r, c + 4, 100 * outcome[1] / income_total[1], f_percentage)

            r += 1

            return r, outcome, income_total

        def add_foot(worksheet, r, outcome, income):
            c = 2
            r += 1
            underline = workbook.add_format()
            underline.set_bottom()
            f_value = workbook.add_format({'num_format': '$#,##0', 'border': 5, 'border_color': '#7AFDFF'})
            f_percentage = workbook.add_format({'num_format': '0.00'})
            foot = workbook.add_format({'bold': True})
            foot.set_font("arial")
            for i in range(6):
                worksheet.write(r, c + i - 1, "", underline)
            r += 1

            worksheet.write(r, c, " Utilidad (o pérdida)", foot)
            worksheet.write(r, c + 1, income[0] + outcome[0], f_value)
            worksheet.write(r, c + 2, 100 * (income[0] + outcome[0]) / income[0], f_percentage)
            worksheet.write(r, c + 3, income[1] + outcome[1], f_value)
            worksheet.write(r, c + 4, 100 * (income[1] + outcome[1]) / income[1], f_percentage)

        add_header(ws)
        r, outcome, income = add_body(ws)
        add_foot(ws, r, outcome, income)

        ws.autofit()
        workbook.close()


# obj=ObjTrialBalance.from_xlsx(r"C:\Users\mi compu\Desktop\Programacion\python\BusinessPlatform\business_app\files\trial_balances\02 22.xlsx",date(2022,2,1))
# obj.save()
obj2 = ObjTrialBalance.from_db(date(2022, 3, 1)).balance_sheet()
# print((obj2.date_month))

print(obj2.audit())

def ov_aud(dates):
    workbook = xlsxwriter.Workbook("balance_audit.xlsx")
    for i in dates:
        ws = workbook.add_worksheet(name=i.isoformat())
        obj = ObjTrialBalance.from_db(i).balance_sheet()
        aud = obj.audit()
        for n,c in enumerate(aud.columns):
            ws.write(0,n, c)

        for n,(x,r) in enumerate(aud.iterrows()):
            print(r)
            for e, c in enumerate(r):
                print(c)
                ws.write(n+1, e, c)
        ws.autofit()
    workbook.close()

lst_dates=[date(2022, i, 1) for i in range(1,13)]+[date(2023, i, 1) for i in range(1,6)]
ov_aud(lst_dates)



#obj2.formatted_excel("prueba_b.xlsx")
# print(obj2.data.regex(r"^\d{1}00-00-000"))
# print((obj2.balance_sheet().list_for_tree()))
"""all=(ObjTrialBalance.get_all())
for i in all:
    print(i.income_statement())"""
