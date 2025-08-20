import plotly.graph_objects as go
import pandas as pd

def generate_customer_period_revenue_figure() -> go.Figure:
    # Sample data
    data = {
        'customer': ['Customer A', 'Customer A', 'Customer A', 'Customer B', 'Customer B', 'Customer B'],
        'period': ['2023-01', '2023-02', '2023-03', '2023-01', '2023-02', '2023-03'],
        'method': ['Method 1', 'Method 2', 'Method 3', 'Method 1', 'Method 2', 'Method 3'],
        'revenue': [100, 150, 200, 110, 160, 210]
    }
    df = pd.DataFrame(data)

    # Initialize figure
    fig = go.Figure()

    # Add traces for each combination of customer and period
    for customer in df['customer'].unique():
        for period in df['period'].unique():
            filtered_data = df[(df['customer'] == customer) & (df['period'] == period)]
            fig.add_trace(
                go.Bar(
                    x=filtered_data['method'],
                    y=filtered_data['revenue'],
                    name=f'{customer} - {period}',
                    visible=False,
                    text=[f"${val:,.2f}" for val in filtered_data['revenue']],
                    texttemplate='%{text}',
                    textposition='auto'
                )
            )

    # Initially display the first customer and period
    fig.data[0].visible = True

    # Create dropdown menus for customers
    customer_dropdown_buttons = [
        {
            'label': customer,
            'method': 'update',
            'args': [
                {'visible': [trace.name.startswith(customer) for trace in fig.data]},
                {'title': f'Customer: {customer}'}
            ]
        } 
        for customer in df['customer'].unique()
    ]

    # Create dropdown menus for periods
    period_dropdown_buttons = [
        {
            'label': period,
            'method': 'update',
            'args': [
                {'visible': [trace.name.endswith(period) for trace in fig.data]},
                {'title': f'Period: {period}'}
            ]
        } 
        for period in df['period'].unique()
    ]

    # Define callback function to update visibility based on dropdown selections
    def update_visibility(customer, period):
        return [
            trace.name.startswith(customer) and trace.name.endswith(period)
            for trace in fig.data
        ]

    # Set up update menus for the combined effect of customer and period selection
    fig.update_layout(
        updatemenus=[
            {
                'buttons': customer_dropdown_buttons,
                'direction': 'down',
                'showactive': True,
                'x': 0.17,  # Adjust position
                'xanchor': 'left',
                'y': 1.15,
                'yanchor': 'top'
            },
            {
                'buttons': period_dropdown_buttons,
                'direction': 'down',
                'showactive': True,
                'x': 0.83,  # Adjust position
                'xanchor': 'right',
                'y': 1.15,
                'yanchor': 'top'
            }
        ],
        title='Customer and Period Revenue'
    )

    # Add button callback to update visibility
    for customer in df['customer'].unique():
        for period in df['period'].unique():
            fig.add_annotation(
                x=0.5, 
                y=0.5, 
                xref='paper', 
                yref='paper', 
                text='', 
                showarrow=False,
                font=dict(size=12),
                align='center'
            )
            fig.data[0].on_change(lambda *args, cust=customer, per=period: fig.update_traces(visible=update_visibility(cust, per)))

    return fig
