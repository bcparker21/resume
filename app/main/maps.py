import folium, json
import geopandas as gpd

def getCentroid(poly):
	return [poly.centroid[0].y,poly.centroid[0].x]

def getBounds(poly):
	x1,y1,x2,y2=poly['geometry'].total_bounds
	bounds = [[y1,x1],[y2,x2]]
	return bounds

def polyToJson(poly,savepath):
	poly.to_file(savepath,driver='GeoJSON')
	return None

def load_json(data):
	with open(data) as f:
		output = json.loads(f)
		return output

def makeMap(location, savepath=None):
	m = folium.Map(location=location,tiles=None,height='80%')
	# m.fit_bounds(bounds)
	folium.raster_layers.TileLayer(
		tiles='OpenStreetMap', name='Open Street Map').add_to(m)
	folium.raster_layers.TileLayer(
		tiles='stamenterrain', name='Terrain').add_to(m)
	folium.raster_layers.WmsTileLayer(
		url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
		layers=None,
		name='Aerial',
		attr='ESRI World Imagery',
		show=False).add_to(m)
	# fg=folium.FeatureGroup(name=layername)
	# m.add_child(fg)
	# for i in layers['geometry']:
	# 	folium.GeoJson(i).add_to(fg)
	# folium.LayerControl().add_to(m)
	if savepath:
		m.save(savepath)
	return m