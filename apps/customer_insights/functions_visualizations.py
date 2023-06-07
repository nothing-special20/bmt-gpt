import pandas as pd
import numpy as np
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objects as go

async def bar_chart(data, chart_config):
    fig = px.bar(data.head(5), x=chart_config['x'], y=chart_config['y'], height=400)

    plot_obj = plot({'data': fig}, output_type='div')

    return plot_obj