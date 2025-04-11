import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.geocoders import Nominatim
from pyproj import Geod
import matplotlib.patches as mpatches
import time
from shapely.geometry import Polygon
import numpy as np

def generate_coordinates_from_locations(locations: list) -> dict[tuple]:
    """Gets the coordinates of a city, country"""
    geolocator = Nominatim(user_agent="geolocator", timeout=10)
    
    coordinates = []
    for city, country in locations:
        try:
            # Need delay between requests
            time.sleep(1)
            location = geolocator.geocode(f"{city}, {country}")

            if location:
                coordinates.append((f"{city}, {country}", (location.longitude, location.latitude)))
            else:
                print(f"Location not found: {city}, {country}")

        except Exception as e:
            print(f"Error retrieving location {city}, {country}: {e}")
            coordinates.append((f"{city}, {country}", (None, None)))

    return coordinates

#FIXME This is wayyyy too slow...
#BUG Locations get showed even if out of the map bounds
def plot_locations_on_map(locations: list):
    # Getting world map to plot
    world = gpd.read_file("../data/map/world_map.shp")
    
    # Filter for Netherlands
    netherlands = world[world['NAME'] == 'Netherlands']
    
    # Set up geodesic and projection
    geod = Geod(ellps="WGS84")
    mercator = ccrs.Mercator()
    plate_carree = ccrs.PlateCarree()
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': mercator})

    # Map bounds (xmin, xmax, ymin, ymax)
    ax.set_extent([-2, 12, 48, 57], crs=plate_carree)  
    
    # Add features to the map
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.RIVERS)
    ax.add_feature(cfeature.LAKES)
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.5)
    
    # Plot Netherlands outline
    netherlands.plot(ax=ax, color='pink')
       
    # Locations to coordinates
    coordinates = generate_coordinates_from_locations(locations)
    
    def create_circle(lon, lat, radius_km=150):
        """Create a circle as a polygon"""
        
        # Convert radius to degrees based on latitude
        radius_lat = radius_km / 111.0
        radius_lon = radius_km / (111.0 * np.cos(np.radians(lat)))
        
        # Create a circle using numpy
        theta = np.linspace(0, 2*np.pi, 100)
        circle_x = lon + radius_lon * np.cos(theta)
        circle_y = lat + radius_lat * np.sin(theta)
        
        # Create polygon from coordinates
        return Polygon(zip(circle_x, circle_y))

    # Draw cities and circles
    for name, (lon, lat) in coordinates:
        circle = create_circle(lon, lat)
        gpd.GeoSeries([circle], crs="EPSG:4326").to_crs(epsg=3395).plot(
            ax=ax, color="blue", alpha=0.3, edgecolor="black"
        )
        ax.plot(lon, lat, marker='o', color='red', transform=plate_carree)
        ax.text(lon + 0.3, lat + 0.3, name, transform=plate_carree)
    
    # Add a legend
    circle_legend = mpatches.Patch(color='blue', alpha=0.3, label='150km Radius')
    point_legend = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=1, label='Location')
    ax.legend(handles=[circle_legend, point_legend], loc='lower right') 
    ax.set_aspect('equal')  # Forces the x and y axes to be scaled equally
    plt.savefig("../temp_files/geojson_map.png", bbox_inches='tight')
    plt.close()


locations = [['London', 'UK'], ['Amsterdam', 'Netherlands'], ['Brussels', 'Belgium'], ['Berlin', 'Germany']]
plot_locations_on_map(locations)