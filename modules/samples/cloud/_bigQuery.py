import json
import httplib2
import numpy
import re
from datetime import datetime

class _BigQueryService():
    def __init__(self):
        pass

    @staticmethod
    def data(sql):
        return _BigQueryData(sql)

    @staticmethod
    def table(name):
        m = re.match('^\[([a-z0-9\-_]+)\:([a-z0-9]+)\.([a-z0-9]+)\]$', name)
        if m is not None:
            return _BigQueryTable(name, m.groups())

        m = re.match('^\[([a-z0-9]+)\.([a-z0-9]+)\]$', name)
        if m is not None:
            from _internals import _Metadata
            metadata = _Metadata.load()

            groups = m.groups()

            parts = []
            parts.append(metadata.projectId());
            parts.append(groups[0])
            parts.append(groups[1]);
            return _BigQueryTable(name, parts);

        return None

class _BigQueryTable():
    def __init__(self, name, parts):
        self._name = name
        self._project = parts[0]
        self._dataset = parts[1]
        self._table = parts[2]
        self._schema = None

    def name(self):
        return self._name

    def schema(self):
        if self._schema is None:
            self._schema = _BigQueryExecutor.schema(self._project, self._dataset, self._table)
        return self._schema

    def sql(self):
        return self._name

class _BigQueryData():
    def __init__(self, sql):
        self._sql = sql
        self._data = None
        pass

    def execute(self):
        if self._data is None:
            self._data = _BigQueryExecutor.query(self._sql)
        return self._data

    def sql(self):
        return self._sql

    def dataFrame(self):
        from pandas import DataFrame

        items = self.execute()
        if len(items) == 0:
            return DataFrame()
        return DataFrame.from_dict(items)

    def list(self):
        return self.execute()


_BIGQUERY_ENDPOINT = 'https://www.googleapis.com/bigquery/v2'
_BIGQUERY_QUERY_SEGMENT = '/projects/%s/queries'
_BIGQUERY_JOB_SEGMENT = '/projects/%s/queries/%s?maxResults=%d&timeoutMs=%d'
_BIGQUERY_JOB_PAGE_SEGMENT = '/projects/%s/queries/%s?maxResults=%d&timeoutMs=%d&pageToken=%s'
_BIGQUERY_TABLE_SEGMENT = '/projects/%s/datasets/%s/tables/%s'
_BIGQUERY_PAGE_SIZE = 5000
_BIGQUERY_TIMEOUT = 60000

class _BigQueryExecutor():
    @staticmethod
    def schema(project, dataset, table):
        from _internals import _Metadata
        metadata = _Metadata.load()

        url = _BIGQUERY_ENDPOINT + (_BIGQUERY_TABLE_SEGMENT % (project, dataset, table))
        headers = { \
          'Authorization': 'OAuth ' + metadata.accessToken() \
        }

        http = httplib2.Http()
        response, content = http.request(url, method = 'GET', headers = headers)

        if response.status == 200:
            result = json.loads(content)
            return result['schema']['fields']
        else:
            print str(response.status)
            print content
            return None

    @staticmethod
    def query(sql):
        from _internals import _Metadata
        metadata = _Metadata.load()

        request = { \
          'kind': 'bigquery#queryRequest', \
          'query': sql, \
          'defaultDataset': { 'datasetId':'github' }, \
          'maxResults': _BIGQUERY_PAGE_SIZE, \
          'timeoutMs': _BIGQUERY_TIMEOUT
        }

        url = _BIGQUERY_ENDPOINT + (_BIGQUERY_QUERY_SEGMENT % metadata.projectId())
        body = json.dumps(request)
        headers = { \
          'Content-Type': 'application/json', \
          'Content-Length': str(len(body)), \
          'Authorization': 'OAuth ' + metadata.accessToken() \
        }

        http = httplib2.Http()
        response, content = http.request(url, method = 'POST', headers = headers, body = body)

        if response.status == 200:
            result = json.loads(content)
            try:
                return _BigQueryExecutor.parseData(metadata, result)
            except:
                print result
                return None
        else:
            print str(response.status)
            print content
            # TODO: Throw error
            return None

    @staticmethod
    def queryNextPage(metadata, jobId, pageToken):
        url = _BIGQUERY_ENDPOINT + \
              _BIGQUERY_JOB_PAGE_SEGMENT % (metadata.projectId(), jobId,
                                            _BIGQUERY_PAGE_SIZE, _BIGQUERY_TIMEOUT,
                                            pageToken)
        headers = { 'Authorization': 'OAuth ' + metadata.accessToken() }

        http = httplib2.Http()
        response, content = http.request(url, method = 'GET', headers = headers)

        if response.status == 200:
            return json.loads(content)
        else:
            # TODO: Throw error
            print str(response.status)
            print content
            return None

    @staticmethod
    def waitForCompletion(metadata, jobId):
        url = _BIGQUERY_ENDPOINT + \
              _BIGQUERY_JOB_SEGMENT % (metadata.projectId(), jobId,
                                       _BIGQUERY_PAGE_SIZE, _BIGQUERY_TIMEOUT)
        headers = { 'Authorization': 'OAuth ' + metadata.accessToken() }

        http = httplib2.Http()
        response, content = http.request(url, method = 'GET', headers = headers)

        if response.status == 200:
            return json.loads(content)
        else:
            # TODO: Throw error
            print str(response.status)
            print content
            return None

    @staticmethod
    def parseValue(type, value):
        if value is None or value == 'null':
            return None
        if type == 'INTEGER' or type == 'FLOAT':
           return float(value)
        elif type == 'TIMESTAMP':
            return numpy.datetime64(datetime.utcfromtimestamp(float(value)))
        elif type == 'BOOLEAN':
            return value == 'true'
        elif type == 'STRING':
            return value
        else:
            return str(value)

    @staticmethod
    def parseData(metadata, result):
        job = result['jobReference']['jobId']

        while result['jobComplete'] == False:
            result = _BigQueryExecutor.waitForCompletion(metadata, job)

        fields = result['schema']['fields']
        totalCount = float(result['totalRows'])

        rows = []
        while len(rows) < totalCount:
            for r in result['rows']:
                row = {}
                for i, f in enumerate(r['f']):
                    row[fields[i]['name']] = _BigQueryExecutor.parseValue(fields[i]['type'], f['v'])
                rows.append(row)

            if len(rows) < totalCount:
                pageToken = result['pageToken']
                result = _BigQueryExecutor.queryNextPage(metadata, job, pageToken)

        return rows
