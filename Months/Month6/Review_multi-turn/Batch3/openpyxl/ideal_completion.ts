import openpyxl

def populate_report_data(workbook_path: str) -> None:
    wb = openpyxl.load_workbook(workbook_path)
    active_sheet = wb.active

    # Get the date value from cell B17
    date_value = active_sheet["B17"].value
    date_str = None
    if date_value is None:
        date_str = None
    elif hasattr(date_value, "strftime"):
        try:
            date_str = date_value.strftime("%Y-%m-%d")
        except Exception:
            date_str = str(date_value)
    else:
        date_str = str(date_value)

    # Find matching report sheet
    report_sheet_name = None
    if date_str:
        for sheetname in wb.sheetnames:
            if sheetname == date_str or sheetname.strip() == f"Report for {date_str}".strip():
                report_sheet_name = sheetname
                break

    if report_sheet_name and report_sheet_name in wb.sheetnames:
        report_sheet = wb[report_sheet_name]
        mapping = {
            'E55': 'AH6', 'E56': 'AH7', 'E57': 'AH8', 'E58': 'AH9',
            'H55': 'AH10', 'H56': 'AH11', 'H57': 'AH12', 'H58': 'AH13',
            'H21': 'AH15', 'H22': 'AH16', 'H23': 'AH17', 'H24': 'AH18',
            'E25': 'AH19', 'E20': 'AH20', 'H30': 'AH21', 'E49': 'AH23',
            'E51': 'AH24', 'E52': 'AI24', 'E50': 'AH25', 'E53': 'AH26',
            'E54': 'AI26', 'H51': 'AH27', 'H52': 'AI27', 'H53': 'AH28',
            'E21': 'AH30', 'E22': 'AH31', 'H49': 'AH32', 'H50': 'AH31',
            'E23': 'AH35', 'E24': 'AH36', 'E59': 'AH37', 'E60': 'AH38',
            'E61': 'AH39', 'E62': 'AH40', 'H59': 'AH41', 'H60': 'AH42',
            'H61': 'AH43'
        }
        for src, dest in mapping.items():
            try:
                active_sheet[dest].value = report_sheet[src].value
            except Exception:
                continue

    wb.save(workbook_path)
