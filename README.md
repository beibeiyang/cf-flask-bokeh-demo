# Stock Visualization using Python, Flask, Bokeh and Cloud Foundry

This Python application is empowered by [Flask](http://flask.pocoo.org) and [Bokeh](http://bokeh.pydata.org) and can be pushed to [Pivotal Cloud Foundry](http://pivotal.io/platform) or the open-source [Cloud Foundry](https://www.cloudfoundry.org) with the built-in CF Python Buildpack.

This app calls the [Quandl Wiki EOD Stock Prices API](http://www.quandl.com) to retrieve stock prices and visualize the data using Bokeh over the Flask framework. Anonymous user is limited to 50 calls per day. Get a Quandl API key if you want more intensive use.

Live example: [http://stocks.cfapps.io](http://stocks.cfapps.io)

# Run Locally

Install dependencies: `pip install -r requirements.txt`

```
$ python stocks.py
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

# Push to Cloud Foundry

Here are the steps to push the app to Cloud Foundry:

* Modify `manifest.yml` to tailor to your environment settings
* Enter `cf login ...` to point to your CF API endpoint and the correct org and space
* Enter `cf push`

# Caveat

The app requires Bokeh v0.12.4 as defined in `requirements.txt`. You must update the template file `templates\graph.html` if you choose to use a different version of Bokeh.


# License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
