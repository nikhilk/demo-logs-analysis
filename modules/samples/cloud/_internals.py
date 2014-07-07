import json
import httplib2
import os

_METADATA_ENDPOINT = 'http://%s:%s/computeMetadata/v1' % \
    (os.environ.get('METADATA_HOST', 'metadata.google.internal'),
     os.environ.get('METADATA_PORT', '80'))
_PROJECTID_SEGMENT = '/project/project-id'
_TOKEN_SEGMENT = '/instance/service-accounts/default/token'

class _Metadata():
    def __init__(self, projectId):
        self._projectId = projectId
        self._accessToken = None

    def accessToken(self):
        if self._accessToken is None:
            uri = _METADATA_ENDPOINT + _TOKEN_SEGMENT
            self._accessToken = _Metadata._loadMetadata(uri, field = 'access_token')
        return self._accessToken

    def projectId(self):
        return self._projectId

    @staticmethod
    def load():
        uri = _METADATA_ENDPOINT + _PROJECTID_SEGMENT
        projectId = _Metadata._loadMetadata(uri)

        return _Metadata(projectId)

    @staticmethod
    def _loadMetadata(uri, field = ''):
        http = httplib2.Http()
        headers = { 'X-Google-Metadata-Request': 'True' }

        resp, content = http.request(uri, method = 'GET', body = None, headers = headers)

        if (resp.status == 200):
            if len(field):
                data = json.loads(content)
                return data[field]
            else:
                return content
        else:
            raise RuntimeError('Unable to load cloud metadata.')
