import pandas as pd
import numpy as np

def generate_area_html(df: pd.DataFrame) -> str:
    lines = []
    first_row = True
    for idx, row in df.iterrows():
        if not first_row:
            lines.append("        <tr>")
        else:
            lines.append("<tr>")
            first_row = False

        style_str = "border: 1px solid black; text-align: center;"

        # Location
        lines.append(f'            <td style="{style_str}">{str(row["Location"])}</td>')

        # Projection (Units)
        proj = row.get('Projection (Units)', np.nan)
        proj_val = 0 if pd.isna(proj) else proj
        proj_content = str(int(proj_val)) if isinstance(proj_val, (int, float)) and not pd.isna(proj_val) else str(proj_val)
        lines.append(f'            <td style="{style_str}">{proj_content}</td>')

        # Transactions (Units)
        trans = row.get('Transactions (Units)', np.nan)
        trans_val = 0 if pd.isna(trans) else trans
        trans_content = str(int(trans_val)) if isinstance(trans_val, (int, float)) and not pd.isna(trans_val) else str(trans_val)
        lines.append(f'            <td style="{style_str}">{trans_content}</td>')

        # SMAPE Value (%)
        smape = row.get('SMAPE Value (%)', np.nan)
        smape_val = "Unavailable" if pd.isna(smape) else smape
        lines.append(f'            <td style="{style_str}">{str(smape_val)}</td>  <!-- SMAPE value -->')

        # Requested (Units)
        req = row.get('Requested (Units)', np.nan)
        req_val = 0 if pd.isna(req) else req
        req_content = str(int(req_val)) if isinstance(req_val, (int, float)) and not pd.isna(req_val) else str(req_val)
        lines.append(f'            <td style="{style_str}">{req_content}</td>')

        # Received (Units)
        rec = row.get('Received (Units)', np.nan)
        rec_val = 0 if pd.isna(rec) else rec
        rec_content = str(int(rec_val)) if isinstance(rec_val, (int, float)) and not pd.isna(rec_val) else str(rec_val)
        lines.append(f'            <td style="{style_str}">{rec_content}</td>')

        # Fulfillment Calculation (%)
        full = row.get('Fulfillment Calculation (%)', np.nan)
        full_val = 0 if pd.isna(full) else full
        full_content = f"{full_val}%"
        lines.append(f'            <td style="{style_str}">{full_content}</td>')

        # Out of Stock Count
        out = row.get('Out of Stock Count', np.nan)
        out_val = 0 if pd.isna(out) else out
        out_content = str(int(out_val)) if isinstance(out_val, (int, float)) and not pd.isna(out_val) else str(out_val)
        lines.append(f'            <td style="{style_str}">{out_content}</td>')

        lines.append("        </tr>")

    # Join all lines with newlines
    html = "\n".join(lines)
    return html