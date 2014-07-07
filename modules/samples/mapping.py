import json
from IPython.core.display import HTML

_HTML_TEMPLATE = """
<div id="%s" style="width: 100%%; height: 500px"></div>
<script>
window.createMap = function(e, data) {
  window.loadMap = function() {
    var mapOptions = {
      center: new google.maps.LatLng(37.7805081,-122.4254151),
      zoom: 13,
      draggable: false,
      scrollwheel: false
    };

    var map = new google.maps.Map(e, mapOptions);

    var heatmapLocations = [];
    for (var i = 0; i < data.length; i++) {
      var spot = data[i];
      var loc = {
        location: new google.maps.LatLng(spot.lat, spot.lon),
        weight: spot.trips
      };
      heatmapLocations.push(loc);
    }
    new google.maps.visualization.HeatmapLayer({
      data: heatmapLocations,
      dissipating: true,
      radius: 16,
      map: map
    });
  }

  var url = 'http://maps.googleapis.com/maps/api/js?libraries=geometry,visualization&callback=loadMap';
  var script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = url;
  document.getElementsByTagName('HEAD')[0].appendChild(script);
}
createMap(document.getElementById('%s'), %s);
</script>
"""

class HeatMap(object):

    def __init__(self):
        pass

    def render(self, id, data):
        html = _HTML_TEMPLATE % (id, id, json.dumps(data))
        return HTML(html)
