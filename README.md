Logs Analysis Demos
===================

Logs analysis demo samples used to demonstrate data analysis with [BigQuery](https://developers.google.com/bigquery/)
and [IPython](http://ipython.org/) at [Google I/O 2014](https://www.google.com/events/io/schedule/session/6ac744ee-99e6-e311-b297-00155d5066d7).

# Sample Notebooks

- [Anomaly Detection with Request Logs](http://nbviewer.ipython.org/github/nikhilk/demo-logs-analysis/blob/master/notebooks/RequestLogs.ipynb)

  This demonstrates working with HTTP logs to create metrics (such as 99th percentile latency
  or request volume) using BigQuery, and then running the resulting time-series through an
  anomaly detector implemented in Python, and plotting the time-series as well as detected
  anomalies.

- [Hotspot Detection from GPS Logs](http://nbviewer.ipython.org/github/nikhilk/demo-logs-analysis/blob/master/notebooks/UberHotspots.ipynb)

  This demostrates working with a GPS stream (in particular using sample data from Uber taxis
  in SFO over a week) and aggregating the readings in a spatial manner, to determine and
  render activity hotspots.

# Running Notebooks Locally

You can execute the notebooks locally using IPython and the included sample code, once you've
uploaded the sample data into BigQuery within your cloud project.

## Loading Logs DataSets into BigQuery

- Unzip the sample data in to the data directory.
- Upload them into a Google Cloud Storage bucket within your cloud project
- Go to the BigQuery console
- Create a dataset named `requestlogs` and then a table named `logs` within it. Use the request
  logs data to populate the table.
- Repeat for a dataset named `uberlogs` and a table `logs` within it. Use the uber logs sample
  data to populate the table.

## Initializing local development environment

- Install the [Google cloud SDK](https://developers.google.com/cloud/sdk/) (which installs the gcloud tool).
- Run `gcloud auth login` to perform a login operation and authorize your local development machine.
- Run `gcloud config set project <cloud project name>` to configure the active project.
- Install node.js if you don't already have it installed locally.
- Run `node misc/metadata.js` - this runs a local emulation of the Google Cloud Metadata service
  which is used by the sample python code to authorize queries issued to BigQuery.
- Install IPython if you don't already have it. I used the [Anaconda distribution](http://continuum.io/downloads).
- Start IPython using the `run.sh` script included.
- Within the browser, select the notebook, or create a new one.
