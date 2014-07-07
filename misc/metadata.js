var http = require('http'),
    url = require('url'),
    system = require('child_process');

function exec(cmd, cb) {
  process.env['TERM'] = 'vt-100';
  var child = system.exec(cmd, function(error, stdout, stderr) {
    if (error) {
      cb(error);
    }
    else {
      cb(null, stdout);
    }
  });
}

function handleProjectIdRequest(cb) {
  var cmd = 'gcloud config list project | grep project';
  exec(cmd, function(error, data) {
    if (error) {
      cb(error);
    }
    else {
      cb(null, data.replace('project = ', '').trim());
    }
  });
}

function handleAccessTokenRequest(cb) {
  var cmd = 'gcloud auth print-access-token';
  exec(cmd, function(error, data) {
    if (error) {
      cb(error);
    }
    else {
      var token = data.replace(/\u001b\[\d{0,2}m/g, '').trim();
      cb(null, { access_token: token });
    }
  });
}

function handler(req, resp) {
  console.log(req.url);

  var requestUrl = url.parse(req.url);
  var path = requestUrl.path;

  function dataCallback(error, data) {
    var status = 200;
    var contentType = 'text/plain';
    var content = data;

    if (error) {
      status = 500;
      content = error.toString();
    }
    else if (typeof data != 'string') {
      contentType = 'application/json';
      content = JSON.stringify(data);
    }

    resp.writeHead(status, { 'Content-Type': contentType });
    resp.write(content);
    resp.end();
  }

  var data = null;
  if (path == '/computeMetadata/v1/project/project-id') {
    handleProjectIdRequest(dataCallback);
  }
  else if (path == '/computeMetadata/v1/instance/service-accounts/default/token') {
    handleAccessTokenRequest(dataCallback);
  }
  else {
    resp.writeHead(404);
    resp.end();
  }
}

var server = http.createServer(handler);
var port = process.env['METADATA_PORT'] || 8889

server.listen(port);
console.log('Metadata server started. Listening on http://localhost:' + port + ' ...');
