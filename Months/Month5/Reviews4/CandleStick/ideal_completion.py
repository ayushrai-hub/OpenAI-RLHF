# ideal_completion.py
import plotly.graph_objects as go
import pandas as pd

def create_candlestick_chart(data):
    df = pd.DataFrame(data)

    # Create candlestick chart using plotly.graph_objects
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])

    # Set title and layout
    fig.update_layout(title="Candlestick Chart for Sample Data",
                      xaxis_title="Date",
                      yaxis_title="Price")
    
    return fig
