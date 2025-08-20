# ideal_completion.py
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats

# Example DataFrames (Switch with your real data loading code)
df_all = pd.read_csv('my_all_data.csv')
df_pt = pd.read_csv('my_pt_data.csv')

def center_window(window, width=300, height=200):
    """Center the Tkinter window."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def format_date_for_title(date_str):
    """Convert date from YYYYMMDD to DD/MM/YYYY"""
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return date_str

def create_report(order_number=None):
    material_number = material_number_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    if not material_number and order_number:
        order_data = df_pt[df_pt['order'] == int(order_number)]
        if not order_data.empty:
            material_number = order_data['material_number'].values[0]
            start_date = order_data['date'].min()
            end_date = order_data['date'].max()
        else:
            messagebox.showwarning("Warning", f"The order number {order_number} has no data.")
            return

    if not start_date:
        start_date = "20000101"
    if not end_date:
        end_date = "21000101"

    df_pt['date'] = df_pt['date'].astype(str)

    conditions = (df_pt['date'] >= start_date) & (df_pt['date'] <= end_date)

    if material_number:
        conditions &= (df_pt['material_number'] == int(material_number))
    
    if order_number:
        conditions &= (df_pt['order'] == int(order_number))

    filtered_df = df_pt.loc[conditions]

    if filtered_df.empty:
        messagebox.showwarning("Warning", "No data matches your chosen criteria.")
        return

    median_value_ia = np.median(filtered_df['value_ia'])
    median_value_ma = np.median(filtered_df['value_ma'])

    ia_range = (median_value_ia - 0.30 * median_value_ia, median_value_ia + 0.30 * median_value_ia)
    ma_range = (median_value_ma - 0.30 * median_value_ma, median_value_ma + 0.30 * median_value_ma)

    sorted_workstations = filtered_df['workstations'].sort_values().unique()

    # Get unique levels of hue variable `cw_ccw`
    unique_cw_ccw = filtered_df['cw_ccw'].unique()

    # Set markers based on the unique levels of `hue`
    marker_list = ['o', 'x'][:len(unique_cw_ccw)]  # Ensure the length of markers matches `hue`

    # Plot 1: Scatter Plot using lmplot
    lm = sns.lmplot(data=filtered_df,
                    x='value_ma',
                    y='value_ia',
                    hue='cw_ccw',
                    col='cw_ccw',
                    palette='bright',
                    markers=marker_list,  # Use the correct marker list
                    row='workstations',
                    row_order=sorted_workstations,
                    truncate=False,
                    legend=False,
                    aspect=1)

    lm.set(xlim=ma_range, ylim=ia_range)
    axes = lm.axes.flatten()

    def convert_to_float(val):
        try:
            return float(val)
        except ValueError:
            return None

    for ax in axes:
        ax.set_xlabel('Start Moment [Ncm]', fontsize=12)
        ax.set_ylabel('Start Current [A]', fontsize=12)

        if 'ia_exp_min' in filtered_df.columns and 'ia_exp_max' in filtered_df.columns:
            ia_exp_min_value = convert_to_float(filtered_df['ia_exp_min'].values[0])
            ia_exp_max_value = convert_to_float(filtered_df['ia_exp_max'].values[0])
            if ia_exp_min_value is not None:
                ax.axhline(y=ia_exp_min_value, color='blue', linestyle='--', label=f'ia_exp_min={round(ia_exp_min_value, 2)}')
            if ia_exp_max_value is not None:
                ax.axhline(y=ia_exp_max_value, color='blue', linestyle='--', label=f'ia_exp_max={round(ia_exp_max_value, 2)}')

        if 'ma_exp_min' in filtered_df.columns and 'ma_exp_max' in filtered_df.columns:
            ma_exp_min_value = convert_to_float(filtered_df['ma_exp_min'].values[0])
            ma_exp_max_value = convert_to_float(filtered_df['ma_exp_max'].values[0])
            if ma_exp_min_value is not None:
                ax.axvline(x=ma_exp_min_value, color='blue', linestyle='--', label=f'ma_exp_min={round(ma_exp_min_value, 2)}')
            if ma_exp_max_value is not None:
                ax.axvline(x=ma_exp_max_value, color='blue', linestyle='--', label=f'ma_exp_max={round(ma_exp_max_value, 2)}')

        if 'ia_min' in filtered_df.columns and 'ia_max' in filtered_df.columns:
            ia_min_value = convert_to_float(filtered_df['ia_min'].values[0])
            ia_max_value = convert_to_float(filtered_df['ia_max'].values[0])
            if ia_min_value is not None:
                ax.axhline(y=ia_min_value, color='red', linestyle='--', label=f'ia_min={round(ia_min_value, 2)}')
            if ia_max_value is not None:
                ax.axhline(y=ia_max_value, color='red', linestyle='--', label=f'ia_max={round(ia_max_value, 2)}')

        if 'ma_min' in filtered_df.columns and 'ma_max' in filtered_df.columns:
            ma_min_value = convert_to_float(filtered_df['ma_min'].values[0])
            ma_max_value = convert_to_float(filtered_df['ma_max'].values[0])
            if ma_min_value is not None:
                ax.axvline(x=ma_min_value, color='red', linestyle='--', label=f'ma_min={round(ma_min_value, 2)}')
            if ma_max_value is not None:
                ax.axvline(x=ma_max_value, color='red', linestyle='--', label=f'ma_max={round(ma_max_value, 2)}')

        handles, labels = ax.get_legend_handles_labels()
        handles = [handle for i, handle in enumerate(handles) if 'cw' not in labels[i] and 'ccw' not in labels[i]]
        labels = [label for label in labels if 'cw' not in label and 'ccw' not in label]
        
        ax.legend(handles, labels, loc='upper right', fontsize='small')

    for i, ax in enumerate(axes):
        row_title = lm.row_names[i // len(lm.col_names)]
        col_title = lm.col_names[i % len(lm.col_names)]
        ax.set_title(f"Workstation = {row_title} | Orientation = {col_title}", fontsize=12)

    start_date_display = format_date_for_title(start_date)
    end_date_display = format_date_for_title(end_date)

    title_parts = [f"Material Number: {material_number}"]
    if order_number:
        title_parts.append(f"Order Number: {order_number}")
    title_parts.append(f"Date Range: {start_date_display} - {end_date_display}")
    full_title = " | ".join(title_parts)
    
    plt.suptitle(full_title, fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.9])

    pdf_filename = (
        f"report_{material_number}_{start_date}_{end_date}.pdf" if material_number
        else f"report_order_{order_number}_{start_date}_{end_date}.pdf"
        if order_number
        else f"report_{start_date}_{end_date}.pdf"
    )

    with PdfPages(pdf_filename) as pdf:
        # Save the first page (scatter plot with lmplot)
        plt.savefig(pdf, format='pdf')
        plt.close()

        # Plot 2: Analysis of Motor Resistance
        df_motor = df_all.query(
            f'material_number == {material_number} and workstations != "repair" and year > 2023 and ia_ccw > 0'
        )
        df_motor = pd.melt(df_motor, id_vars=['year', 'month', 'day', 'spec_imc', 'material_number', 'workstations', 'ia_max', 'ia_min', 'ia_expected', 'order', 'serial_number'], value_vars=['ia_cw', 'ia_ccw'], 
                            var_name='ia', value_name='results')
        df_motor['order_adj'] = df_motor['order'].astype(str) + ' - ' + df_motor['ia'].astype(str)

        group_stats = df_motor.groupby(['material_number', 'order', 'order_adj', 'workstations', 'ia_max', 'ia_min', 'ia_expected'])['results'].agg(['mean', 'std', 'count']).reset_index()

        mean_resistance = group_stats['mean'].mean()
        std_dev_resistance = group_stats['mean'].std()
        upper_limit = mean_resistance + 3 * std_dev_resistance
        lower_limit = mean_resistance - 3 * std_dev_resistance

        plt.figure(figsize=(26, 12))
        plt.errorbar(
            x=group_stats['order_adj'], 
            y=group_stats['mean'],
            yerr=4 * group_stats['std'],
            fmt='o',
            color='black',
            ecolor='black',
            elinewidth=3,
            capsize=6,
            label='Mean ± 4 Std Dev'
        )

        plt.axhline(y=upper_limit, color='green', linestyle='--', label=f'UCL: {upper_limit:.2f}')
        plt.axhline(y=lower_limit, color='green', linestyle='--', label=f'LCL: {lower_limit:.2f}')
        plt.axhline(y=mean_resistance, color='green', linestyle='--', label=f'Mean: {mean_resistance:.2f}')

        plt.title(f'Mean and ±4 Standard Deviations with Control Limits for Motor Resistance by Order', fontsize=14)
        plt.xlabel('Order', fontsize=12)
        plt.ylabel('Motor Resistance [Ω]', fontsize=12)

        # Add legend for the second plot
        plt.legend(loc='upper right', fontsize='medium')
        # Add legend for the second plot (positioned outside the graph)
        plt.legend(bbox_to_anchor=(1, 1), loc='upper left', fontsize=20)

        # Ensure the layout is updated before saving
        plt.tight_layout(rect=[0, 0, 0.95, 1])

        # Save the adjusted layout and legend placement to the PDF
        plt.savefig(pdf, format='pdf')
        plt.close()
        
    messagebox.showinfo("Success", f"Report saved as {pdf_filename}")

def on_submit():
    try:
        order_number = int(order_number_entry.get()) if order_number_entry.get() else None
    except ValueError:
        messagebox.showwarning("Warning", "Order Number should be an integer.")
        return
    create_report(order_number)

def create_gui():
    root = tk.Tk()
    center_window(root, 400, 250)
    root.title("Report Generator")

    tk.Label(root, text="Material Number:").grid(row=0, column=0, padx=10, pady=10)
    global material_number_entry
    material_number_entry = tk.Entry(root)
    material_number_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Start Date (YYYYMMDD):").grid(row=1, column=0, padx=10, pady=10)
    global start_date_entry
    start_date_entry = tk.Entry(root)
    start_date_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="End Date (YYYYMMDD):").grid(row=2, column=0, padx=10, pady=10)
    global end_date_entry
    end_date_entry = tk.Entry(root)
    end_date_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(root, text="Order Number (optional):").grid(row=3, column=0, padx=10, pady=10)
    global order_number_entry
    order_number_entry = tk.Entry(root)
    order_number_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Button(root, text="Generate Report", command=on_submit).grid(row=4, column=0, columnspan=2, pady=20)

    root.mainloop()

create_gui()