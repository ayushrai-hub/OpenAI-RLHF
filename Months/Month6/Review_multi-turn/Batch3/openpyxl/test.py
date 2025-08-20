import unittest
from openpyxl import Workbook
from openpyxl import load_workbook
import os
from ideal_completion import populate_report_data


def generate_data(ws1_name, ws2_name, ws1_values, ws2_values, wb_path):
    wb = Workbook()
    ws = wb.active
    ws.title = ws1_name

    for k, v in ws1_values.items():
        ws[k] = v

    ws2 = wb.create_sheet(title=ws2_name)

    for k, v in ws2_values.items():
        ws2[k] = v

    wb.active = ws
    wb.save(wb_path)


def validate_workbook(ws1_name, ws2_name, wb_path):
    ref = {
        'E55': 'AH6', 'E56': 'AH7', 'E57': 'AH8', 'E58': 'AH9', 'H55': 'AH10',
        'H56': 'AH11', 'H57': 'AH12', 'H58': 'AH13', 'H21': 'AH15', 'H22': 'AH16',
        'H23': 'AH17', 'H24': 'AH18', 'E25': 'AH19', 'E20': 'AH20', 'H30': 'AH21',
        'E49': 'AH23', 'E51': 'AH24', 'E52': 'AI24', 'E50': 'AH25', 'E53': 'AH26',
        'E54': 'AI26', 'H51': 'AH27', 'H52': 'AI27', 'H53': 'AH28', 'E21': 'AH30',
        'H49': 'AH32', 'H50': 'AH31', 'E23': 'AH35', 'E24': 'AH36', 'E59': 'AH37',
        'E60': 'AH38', 'E61': 'AH39', 'E62': 'AH40', 'H59': 'AH41', 'H60': 'AH42',
        'H61': 'AH43'}
    wb = load_workbook(wb_path)
    ws = wb[ws1_name]
    ws2 = wb[ws2_name]
    validation_arr = []
    for k, v in ref.items():
        validation_arr.append(ws2[k].value == ws[v].value)
        if ws2[k].value != ws[v].value:
            print(ws2[k].value, ws[v].value)
    return validation_arr


class TestPythonCode(unittest.TestCase):
    def test_date_included_in_the_sheet_name(self):
        ws1_values = {"B17": "12.10.2024"}
        ws1_name = "ActiveSheet"
        wb_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_workbook.xlsx")
        ws2_name = "Report for 12.10.2024"
        ws2_values = {}
        for i in range(ord('A'), ord('Z') + 1):
            for j in range(1, 66):
                cell = f"{chr(i)}{j}"
                ws2_values[cell] = cell
        generate_data(ws1_name, ws2_name, ws1_values, ws2_values, wb_path)
        populate_report_data(wb_path)
        arr = validate_workbook(ws1_name, ws2_name, wb_path)
        os.remove(wb_path)
        self.assertTrue(all(arr))

    def test_date_identical_with_the_sheet_name(self):
        ws1_values = {"B17": "12.10.2024"}
        ws1_name = "ActiveSheet"
        wb_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_workbook.xlsx")
        ws2_name = "12.10.2024"
        ws2_values = {}
        for i in range(ord('A'), ord('Z') + 1):
            for j in range(1, 66):
                cell = f"{chr(i)}{j}"
                ws2_values[cell] = cell
        generate_data(ws1_name, ws2_name, ws1_values, ws2_values, wb_path)
        populate_report_data(wb_path)
        arr = validate_workbook(ws1_name, ws2_name, wb_path)
        os.remove(wb_path)
        self.assertTrue(all(arr))

    def test_date_incompatible_with_worksheets(self):
        ws1_values = {"B17": "12.10.2024"}
        ws1_name = "ActiveSheet"
        wb_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_workbook.xlsx")
        ws2_name = "20.11.2023"
        ws2_values = {}
        for i in range(ord('A'), ord('Z') + 1):
            for j in range(1, 66):
                cell = f"{chr(i)}{j}"
                ws2_values[cell] = cell
        generate_data(ws1_name, ws2_name, ws1_values, ws2_values, wb_path)
        untouched_cells = [
            'AH6', 'AH7', 'AH8', 'AH9', 'AH10', 'AH11', 'AH12', 'AH13', 'AH15',
            'AH16', 'AH17', 'AH18', 'AH19', 'AH20', 'AH21', 'AH23', 'AH24',
            'AI24', 'AH25', 'AH26', 'AI26', 'AH27', 'AI27', 'AH28', 'AH30',
            'AH32', 'AH31', 'AH35', 'AH36', 'AH37', 'AH38', 'AH39', 'AH40',
            'AH41', 'AH42', 'AH43']
        wb = load_workbook(wb_path)
        ws = wb[ws1_name]
        ref = {}
        for cell in untouched_cells:
            ref[cell] = ws[cell].value
        populate_report_data(wb_path)
        arr = []
        for cell in untouched_cells:
            arr.append(ref[cell] == ws[cell].value)
        os.remove(wb_path)
        self.assertTrue(all(arr))




if __name__ == "__main__":
    unittest.main(verbosity=2)