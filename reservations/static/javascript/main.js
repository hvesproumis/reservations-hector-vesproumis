const point_origin = new ol.Feature(new ol.geom.Point([1.452164858, 43.60666424]));
const point_destination = new ol.Feature(new ol.geom.Point([-0.55333112, 44.821996712]));

const line_route = new ol.Feature(
  new ol.geom.LineString([
    [1.452164858, 43.60666424],
    [-0.55333112, 44.821996712],
  ]),
);

const map = new ol.Map({
  layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM(),
    }),
    new ol.layer.Vector({
        source: new ol.source.Vector({
          features: [point_origin, point_destination, line_route],
        }),
        style: {
          'icon-src': '/static/images/icon.svg',
          'icon-opacity': 0.95,
          'icon-anchor': [0.5, 1],
          'icon-anchor-x-units': 'fraction',
          'icon-anchor-y-units': 'fraction',
          'stroke-width': 3,
          'stroke-color': "#007bff",
          'fill-color': "#007bff",
        },
      }),
  ],
  target: 'map',
  view: new ol.View({
    projection: 'EPSG:4326',
    center: [ 1.4745892853362077, 43.56614582002566],
    zoom: 10,
  }),
});

document.getElementById('zoom-out').onclick = function () {
  const view = map.getView();
  const zoom = view.getZoom();
  view.setZoom(zoom - 1);
};

document.getElementById('zoom-in').onclick = function () {
  const view = map.getView();
  const zoom = view.getZoom();
  view.setZoom(zoom + 1);
};