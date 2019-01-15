from bokeh.plotting import figure, curdoc
from bokeh.models import Range1d, HoverTool, DataRange
from bokeh.models.sources import ColumnDataSource
from bokeh.models.formatters import DatetimeTickFormatter

import rethinkdb as r

from tornado import gen
from threading import Thread
from functools import partial

import datetime

line_list = [['BTC', 'XMR', 'BCN'],
             ['BTC', 'XMR', 'DASH'], ['BTC', 'XMR', 'LTC'], ['BTC', 'XMR', 'MAID'], ['BTC', 'XMR', 'NXT'],
             ['BTC', 'XMR', 'ZEC']]

source = ColumnDataSource(data=dict(x=[], btc_xmr_bcn=[], btc_xmr_dash=[], btc_xmr_ltc=[], btc_xmr_maid=[],
                                    btc_xmr_nxt=[], btc_xmr_zec=[]))

p = figure(plot_width=800, plot_height=400, x_axis_type='datetime', title="Triangular Arbitrage Profit")

# p.x_range.follow = "end"
# p.x_range.follow_interval = 1000 * 60
# p.x_range.min_interval = 1000 * 60

r1 = p.line(x='x', y='btc_xmr_bcn', color="firebrick", line_width=2, source=source, legend='BTC-XMR-BCN')
r2 = p.line(x='x', y='btc_xmr_dash', color="darkviolet", line_width=2, source=source, legend='BTC-XMR-DASH')
r3 = p.line(x='x', y='btc_xmr_ltc', color="orange", line_width=2, source=source, legend='BTC-XMR-LTC')
r4 = p.line(x='x', y='btc_xmr_maid', color="olivedrab", line_width=2, source=source, legend='BTC-XMR-MAID')
r5 = p.line(x='x', y='btc_xmr_nxt', color="mediumturquoise", line_width=2, source=source, legend='BTC-XMR-NXT')
r6 = p.line(x='x', y='btc_xmr_zec', color="darkslategray", line_width=2, source=source, legend='BTC-XMR-ZEC')
p.y_range = Range1d(-4, 4)

p.xaxis.axis_label = 'Time'
p.xaxis.formatter = DatetimeTickFormatter(seconds=["%S s"],
                                          minutes=["%M:%S min"],
                                          minsec=["%M:%S min"],
                                          hours=["%M:%S"])
p.yaxis.axis_label = 'Profit (%)'

p.legend.location = "top_left"
p.legend.click_policy = "hide"
p.legend.label_text_font_size = '8pt'
p.legend.orientation = "horizontal"

p.add_tools(HoverTool(show_arrow=False,
                      line_policy='nearest',
                      tooltips=None))

## important! all threads see same plot
doc = curdoc()
conn = None

start_time = datetime.datetime.now()

curr_dict = {'BTC_XMR_BCN': None, 'BTC_XMR_DASH': None, 'BTC_XMR_LTC': None, 'BTC_XMR_MAID': None, 'BTC_XMR_NXT': None,
             'BTC_XMR_ZEC': None}


@gen.coroutine
def update(x, curr_dict):
    source.stream(dict(x=[x], btc_xmr_bcn=[curr_dict['BTC_XMR_BCN']], btc_xmr_dash=[curr_dict['BTC_XMR_DASH']],
                       btc_xmr_ltc=[curr_dict['BTC_XMR_LTC']], btc_xmr_maid=[curr_dict['BTC_XMR_MAID']],
                       btc_xmr_nxt=[curr_dict['BTC_XMR_NXT']], btc_xmr_zec=[curr_dict['BTC_XMR_ZEC']]))


def stream_data():
    conn = get_connection()
    global start_time
    global curr_dict
    feed = r.union(
        r.table('{}_{}_{}'.format('BTC', 'XMR', 'BCN')).changes(),
        r.table('{}_{}_{}'.format('BTC', 'XMR', 'DASH')).changes(),
        r.table('{}_{}_{}'.format('BTC', 'XMR', 'LTC')).changes(),
        r.table('{}_{}_{}'.format('BTC', 'XMR', 'MAID')).changes(),
        r.table('{}_{}_{}'.format('BTC', 'XMR', 'NXT')).changes(),
        r.table('{}_{}_{}'.format('BTC', 'XMR', 'ZEC')).changes()).run(conn)

    for document in feed:
        x = (datetime.datetime.now() - start_time).total_seconds() * 1000
        curr_dict[document['new_val']['combination']] = document['new_val']['profit']

        # but update the document from callback
        doc.add_next_tick_callback(partial(update, x=x, curr_dict=curr_dict))


def get_connection():
    global conn
    if not conn:
        conn = r.connect("localhost", 28015, db='arbitrage')

    return conn


doc.add_root(p)
# doc.add_periodic_callback(update(x=(datetime.datetime.now() - start_time).total_seconds() * 1000, curr_dict=curr_dict), 100)

thread = Thread(target=stream_data)
thread.start()
