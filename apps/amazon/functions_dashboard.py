import pandas as pd
import numpy as np
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objects as go

def bar_chart(data, chart_config):
    fig = px.bar(data, x=chart_config['x'], y=chart_config['y'])

    plot_obj = plot({'data': fig}, output_type='div')

    return plot_obj