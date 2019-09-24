from plotly.offline import plot
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import sys
from portfolio import config
import sys
sys.path.append(config.code_path)
from dataUtils.dataUtils import dBaseAction
import AlgorithcTrading.config.stocks as stocks


def get_map_chart():
    map_chart = dBaseAction(stocks.dBase, """select * from %s """ % stocks.map_chart)[0]
    return get_line_chart(data=map_chart, x_label='timestamp', output_type='html', showlegend=False, title='Market Map')


def get_volatility_chart():
    volatility_chart = dBaseAction(stocks.dBase, """select * from %s """ % stocks.volatility_chart)[0]
    return get_line_chart(data=volatility_chart, x_label='timestamp', output_type='html', showlegend=False,
                          title='Detrended Volatility')


def get_backtest_chart():
    backtest_chart = dBaseAction(stocks.dBase, """select * from %s """ % stocks.backtest_chart)[0]
    return get_line_chart(data=backtest_chart, x_label='timestamp', output_type='html', showlegend=False,
                          title='Hypothetical Trading Performance')


def get_market_chart():
    market_chart = dBaseAction(stocks.dBase, """select * from %s """ % stocks.market_chart)[0]
    return get_line_chart(data=market_chart, x_label='timestamp', output_type='html', showlegend=False,
                          title='Normalized Market Price')


def get_crypto_charts():
    chart_list = []
    charts = dBaseAction(stocks.dBase, """SELECT name FROM sqlite_master WHERE type='table'""")[0].iloc[:,0]
    charts = charts[charts.str.contains('crypto_chart_')].tolist()
    for chart in charts:
        chart_data = dBaseAction(stocks.dBase, """select * from %s """ % chart)[0]
        title = chart.replace('crypto_chart_', '').replace('_', ' ')
        chart_list.append(get_line_chart(data=chart_data, x_label='timestamp', output_type='html',
                                         showlegend=False, title=title))
    return chart_list


def get_line_chart(data, x_label='timestamp', output_type='html', showlegend=True, title='Chart'):
    fig = go.Figure()

    for y in data.drop(x_label, axis=1):
        fig.add_trace(go.Scatter(x=data[x_label], y=data[y]))

    fig.update_layout(title_text=title,
                      showlegend=showlegend,
                      height=800)

    if output_type == 'html':
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div
    elif output_type == 'chart':
        plot(fig, filename='file.html')
