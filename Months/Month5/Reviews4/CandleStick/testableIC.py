import plotly.express as px
import pandas as pd

def create_candlestick_chart(data):
    df = pd.DataFrame(data)
    fig = px.candlestick(df, x='Date', open='Open', high='High', low='Low', close='Close', title="Sample Candlestick Chart")
    return fig
