"""Flask and Bokeh over Cloud Foundry"""
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config.from_object(__name__)

port = int(os.getenv('VCAP_APP_PORT', 8080))

from wtforms import Form, BooleanField, StringField
from wtforms.validators import DataRequired


class StockForm(Form):
    symbol = StringField('symbol', validators=[DataRequired()])
    closingPrice = BooleanField('Closing Price')
    openingPrice = BooleanField('Opening Price')
    highLow = BooleanField('Daily High and Low')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = StockForm(request.form, closingPrice=True)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('plot',
                                symbol=form.symbol.data,
                                closingPrice=form.closingPrice.data,
                                openingPrice=form.openingPrice.data,
                                highLow=form.highLow.data))
    return render_template('index.html', form=form)

# @app.route('/test')
# def test():
#     return 'Hello World! I am running on port ' + str(port)

@app.route('/stock')
def plot():
    import requests
    import json
    from bokeh.models import ColumnDataSource, HoverTool
    import numpy as np
    from bokeh.plotting import figure
    # from bokeh.io import output_file
    from bokeh.embed import components
    import pandas as pd

    symbol = request.args.get('symbol')
    closingprice = request.args.get('closingPrice')
    openingprice = request.args.get('openingPrice')
    highlow = request.args.get('highLow')

    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % symbol
    session = requests.Session()
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url).text
    json_data = json.loads(raw_data)

    print ('json_data:', json_data)

    from pandas import DataFrame

    # if exceeding API limit
    if  'quandl_error' in json_data:
        div = '<p>%s</p>' % json_data['quandl_error']
        return render_template('graph.html', script='', div=div, header='')

    # other errors
    if  'error' in json_data:
        div = '<p>%s</p>' % json_data['error']
        return render_template('graph.html', script='', div=div, header='')

    df = DataFrame(data=json_data['data'], columns=json_data['column_names'])

    #output_file('bokeh-demo.html', title='Stock Price', autosave=False, mode='inline')

    def datetime(x):
        return np.array(x, dtype=np.datetime64)

    TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"

    df['left'] = pd.DatetimeIndex(df.Date) - pd.DateOffset(days=0.5)
    df['right'] = pd.DatetimeIndex(df.Date) + pd.DateOffset(days=0.5)

    source = ColumnDataSource(data=dict(
        date=datetime(df.Date.as_matrix()),
        datastr=df.Date.as_matrix(),
        close=df.Close.as_matrix(),
        open=df.Open.as_matrix(),
        high=df.High.as_matrix(),
        low=df.Low.as_matrix(),
        left=df.left.as_matrix(),
        right=df.right.as_matrix(),
    ))

    p = figure(tools=TOOLS,
               title='',
               x_axis_type='datetime',
               plot_width=1000, plot_height=600)

    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'


    if openingprice == 'True':
        p.line('date', 'open', source=source, color='#FF0000', legend='Opening Price')
    if closingprice == 'True':
        p.line('date', 'close', source=source, color='#00FF00', legend='Closing Price')
    if highlow == 'True':
        p.quad(top='high', bottom='low', left='left', right='right', color='#A9D0F5',
           source=source, legend="High and Low", fill_alpha=0.5)

    hover = p.select_one(HoverTool)

    hover.point_policy = "follow_mouse"

    hover.tooltips = [ ("Date", "@datastr") ]

    if openingprice == 'True':
        hover.tooltips.append( ("Opening", "$@open{0.00}") )
    if closingprice == 'True':
        hover.tooltips.append( ("Closing", "$@close{0.00}") )
    if highlow == 'True':
        hover.tooltips.append( ("High", "$@high{0.00}") )
        hover.tooltips.append( ("Low", "$@low{0.00}") )

    header = "<h1>%s of %s</h1> <p><strong>Name: </strong>%s </p><p><strong>Description (from our data provider): </strong>%s</p>" \
             "<p style=\"color:red;\">Zoom into the chart to see more detail.</p>" \
             % (json_data['source_name'],
                json_data['code'],
                json_data['name'],
                json_data['description'])

    script, div = components(p)
    return render_template('graph.html', script=script, div=div, header=header)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
