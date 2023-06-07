import pandas as pd
import numpy as np
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objects as go

async def bar_chart(data, chart_config):
    fig = px.bar(data.head(5), x=chart_config['x'], y=chart_config['y'], height=300, width=350)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title=None)
    fig.update_xaxes(tickangle=-45)
    fig.update_yaxes(title=None)
    fig.update_layout(
        autosize=True,
        margin=dict(l=35, r=35, b=30, t=20, pad=0), # left, right, bottom, top
    )

    plot_obj = plot({'data': fig}, output_type='div')

    return plot_obj