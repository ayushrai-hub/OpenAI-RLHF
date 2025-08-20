import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats
import matplotlib.dates as mdates
from typing import Optional

# Example DataFrames (Switch with your real data loading code)
# df_all = pd.read_csv('my_all_data.csv')
# df_pt = pd.read_csv('my_pt_data.csv')

def center_window(window: tk.Tk, width: int = 300, height: int = 200) -> None:
    """Center the Tkinter window."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def format_date_for_title(date_str: str) -> str:
    """Convert date from YYYYMMDD to DD/MM/YYYY"""
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return date_str

def create_report(order_number: Optional[int] = None) -> None:
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

    # Plot 1: Scatter Plot using lmplot
    lm = sns.lmplot(data=filtered_df,
                    x='value_ma',
                    y='value_ia',
                    hue='cw_ccw',
                    col='cw_ccw',
                    palette='bright',
                    markers=['o', 'x'],
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
        
        ax.legend(handles, labels, loc='upper left', fontsize='small')

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
        max_ia = group_stats['ia_max'].astype('float').max()
        min_ia = group_stats['ia_min'].astype('float').min()
        ia_exp = group_stats['ia_expected'].mean()
        mat_num = group_stats['material_number'].mean()

        group_stats = group_stats.query('count >= 100')

        dagostino_p_values = []
        ad_statistics = []
        shapiro_p_values = []

        for _, row in group_stats.iterrows():
            order_adj = row['order_adj']
            order_data = df_motor[df_motor['order_adj'] == order_adj]['results']
            _, dagostino_p_value = stats.normaltest(order_data)
            dagostino_p_values.append(dagostino_p_value)

            ad_statistic, ad_critical_values, ad_significance_level = stats.anderson(order_data)
            ad_statistics.append(ad_statistic)

            _, shapiro_p_value = stats.shapiro(order_data)
            shapiro_p_values.append(shapiro_p_value)

        group_stats['dagostino_p_value'] = dagostino_p_values
        group_stats['ad_statistic'] = ad_statistics
        group_stats['shapiro_p_value'] = shapiro_p_values
        group_stats['±Inner Variation [%]'] = (
            (abs((group_stats['mean'] + 4 * group_stats['std']) / mean_resistance - 1) +
             abs((group_stats['mean'] - 4 * group_stats['std']) / mean_resistance - 1)) * 50
        )

        mean_resistance = group_stats['mean'].mean()
        std_dev_resistance = group_stats['mean'].std()
        upper_limit = mean_resistance + 3 * std_dev_resistance
        lower_limit = mean_resistance - 3 * std_dev_resistance
        y_min = mean_resistance * 0.7
        y_max = mean_resistance * 1.3
        filtered_df_motor = df_motor[df_motor['order_adj'].isin(group_stats['order_adj'])]
        upper_percent = ((upper_limit / mean_resistance) - 1) * 100
        lower_percent = ((lower_limit / mean_resistance) - 1) * 100

        summary_table = group_stats[['order_adj', 'mean', 'std', 'count', 'dagostino_p_value', 'ad_statistic', 'shapiro_p_value']]
        summary_table = summary_table.rename(columns={
            'mean': 'Mean Resistance [Ω]',
            'std': 'Std Dev [Ω]',
            'count': 'Sample Size',
            'dagostino_p_value': 'D\'Agostino p-Value',
            'ad_statistic': 'Anderson-Darling Statistic',
            'shapiro_p_value': 'Shapiro-Wilk p-Value'
        })
        summary_table['Upper ±4 Std Dev [%]'] = ((summary_table['Mean Resistance [Ω]'] + 4 * summary_table['Std Dev [Ω]']) / mean_resistance - 1) * 100
        summary_table['Lower ±4 Std Dev [%]'] = ((summary_table['Mean Resistance [Ω]'] - 4 * summary_table['Std Dev [Ω]']) / mean_resistance - 1) * 100
        summary_table['±Inner Variation [%]'] = (
            summary_table['Upper ±4 Std Dev [%]'].abs() + 
            summary_table['Lower ±4 Std Dev [%]'].abs()
        ) / 2

        group_stats = group_stats.sort_values(by=['order', 'order_adj'], ascending=[True, False])

        # Create a figure with enough space for a legend
        fig = plt.figure(figsize=(22, 12))  # Extra height for the legend

        # Add a main plot area
        ax1 = fig.add_subplot(111)

        # Begin plotting
        ax1.errorbar(
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
        outliers = group_stats[(group_stats['mean'] > upper_limit) | (group_stats['mean'] < lower_limit)]
        ax1.scatter(
            x=outliers['order_adj'], 
            y=outliers['mean'], 
            color='red', 
            edgecolor='black', 
            s=100, 
            marker='X',
            label='Outliers',
            zorder=5
        )
        ax1.scatter(
            x=filtered_df_motor['order_adj'], 
            y=filtered_df_motor['results'], 
            color='lightgray', 
            s=40,
            alpha=0.9,
            edgecolor='black',
            marker='D',
            linewidth=0.3,
            label='_nolegend_'
        )
        ax1.axhline(y=upper_limit, color='green', linestyle='--', label=f'UCL +{upper_percent:.2f}%: {upper_limit:.2f}')
        ax1.axhline(y=lower_limit, color='green', linestyle='--', label=f'LCL {lower_percent:.2f}%: {lower_limit:.2f}')
        ax1.axhline(y=mean_resistance, color='green', linestyle='--', label=f'Mean: {mean_resistance:.2f}')
        ax1.axhline(y=max_ia, color='red', linestyle='-', label=f'IMC +{imc_max:.2f}%: {max_ia:.2f}')
        ax1.axhline(y=min_ia, color='red', linestyle='-', label=f'IMC -{imc_min:.2f}%: {min_ia:.2f}')
        ax1.axhline(y=ia_exp_max, color='blue', linestyle='-', label=f'Model +10%: {ia_exp_max:.2f}')
        ax1.axhline(y=ia_exp_min, color='blue', linestyle='-', label=f'Model -10%: {ia_exp_min:.2f}')
        ax1.set_title(f'{mat_num:.0f} - Mean and ±4 Standard Deviations with Control Limits for Motor Resistance by Order', fontsize=14)
        ax1.set_xlabel('Order', fontsize=12)
        ax1.set_ylabel('Motor Resistance [Ω]', fontsize=12)

        x_labels = [
            f"{order_adj} | IV:{inner_variation:.2f}% | DA:{dagostino_p_value:.2f} | AD:{ad_statistic:.2f} | SW:{shapiro_p_value:.2f}" 
            for order_adj, inner_variation, dagostino_p_value, ad_statistic, shapiro_p_value in zip(
                group_stats['order_adj'], 
                group_stats['±Inner Variation [%]'], 
                group_stats['dagostino_p_value'], 
                group_stats['ad_statistic'],
                group_stats['shapiro_p_value']
            )
        ]
        ax1.set_xticks(group_stats['order_adj'])
        ax1.set_xticklabels(x_labels, rotation=90, fontsize=10)

        # Set up an area for the legend
        ax2 = fig.add_axes([0.1, 0.9, 0.8, 0.1], frame_on=False, sharex=ax1, sharey=ax1)
        ax2.legend(loc='center', bbox_to_anchor=(0.5, 0.5), ncol=3, fontsize=10)
        ax2.axis('off')  # Hide this axis

        plt.grid(True)
        ax1.set_ylim(y_min, y_max)
        plt.tight_layout(pad=3.0)  # Adjust padding for the legend

        # Save the updated graph
        plt.savefig(pdf, format='pdf')
        plt.close()
        
    messagebox.showinfo("Success", f"Report saved as {pdf_filename}")

def on_submit() -> None:
    try:
        order_number = int(order_number_entry.get()) if order_number_entry.get() else None
    except ValueError:
        messagebox.showwarning("Warning", "Order Number should be an integer.")
        return
    create_report(order_number)

def create_gui() -> None:
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