import pandas as pd

def generate_area_html(df):
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                if "smape" in str(col).lower():
                    cell_text = "Unavailable"
                else:
                    cell_text = "0"
            else:
                if "fulfillment" in str(col).lower():
                    try:
                        cell_text = f"{int(val)}%"
                    except Exception:
                        cell_text = f"{val}%"
                elif "smape" in str(col).lower():
                    try:
                        cell_text = f"{float(val):.2f}"
                    except Exception:
                        cell_text = str(val)
                else:
                    if isinstance(val, str):
                        cell_text = val
                    elif isinstance(val, (int, float)):
                        if isinstance(val, float) and val.is_integer():
                            cell_text = str(int(val))
                        else:
                            cell_text = str(val)
                    else:
                        cell_text = str(val)
            cells.append(f'<td style="border: 1px solid black; text-align: center;">{cell_text}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return ''.join(rows)