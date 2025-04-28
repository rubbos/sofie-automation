import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.geocoders import Nominatim
from shapely.geometry import Polygon
from functools import lru_cache
from pathlib import Path   

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

# Cache the geocoding results to avoid repeated API calls
@lru_cache(maxsize=128)
def geocode_location(location_str):
    """Geocode a location string and return longitude and latitude"""
    geolocator = Nominatim(user_agent="geolocator", timeout=10)
    try:
        location = geolocator.geocode(location_str)
        if not location:
            return None, None
        return location.longitude, location.latitude
    except Exception as e:
        return None, None

def generate_coordinates_from_locations(locations) -> list[str, tuple[float, float]]:
    """Gets the coordinates of city, country pairs with batch processing"""
    coordinates = []
    
    # Process locations in batch
    for i, row in enumerate(locations.itertuples(index=False)):
        location_str = f"{row.city}, {row.country}"
        # Add small delay to avoid rate limiting, but only between calls
        if i > 0:
            time.sleep(0.2) 
        
        lon, lat = geocode_location(location_str)
        if lon is not None and lat is not None:
            coordinates.append((location_str, (lon, lat)))
    
    return coordinates

def create_map(locations: list):
    """Plot the user locations on the map with a focus on the dutch border"""
    mercator = ccrs.Mercator()
    plate_carree = ccrs.PlateCarree()
    
    # Plot the map
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': mercator})

    # Map bounds (xmin, xmax, ymin, ymax)
    bounds = [-4, 15, 46, 59]
    ax.set_extent(bounds, crs=plate_carree)  

    # Add borders to the countries
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.5)
    
    # Plot Netherlands as a color for clarity
    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir / 'data' / 'map' / 'world_map.shp'
    world = gpd.read_file(file_path)
    netherlands = world[world['NAME'] == 'Netherlands']
    netherlands.plot(ax=ax, color='pink', transform=plate_carree)
    
    coordinates = generate_coordinates_from_locations(locations)

    # Set radius around valid locations
    circles = []
    for name, (lon, lat) in coordinates:
        # Skip coordinates that are out of bounds
        if bounds[0] <= lon >= bounds[1] or bounds[2] <= lat >= bounds[3]:
            continue

        # Create the circles to a list
        circle = create_circle(lon, lat)
        circles.append(circle)
        
        # Calculate dynamic offset based on map bounds
        offset_x = (bounds[1] - bounds[0]) * 0.01
        offset_y = (bounds[3] - bounds[2]) * 0.01
        ax.text(lon + offset_x, lat + offset_y, name, transform=plate_carree)
        ax.plot(lon, lat, marker='o', color='red', transform=plate_carree)

    # Transform all circles at once for improved performance
    transformed_circles = gpd.GeoSeries(circles, crs="EPSG:4326").to_crs(epsg=3395)
    transformed_circles.plot(ax=ax, color="blue", alpha=0.3, edgecolor="black")

    # Add a legend
    circle_legend = mpatches.Patch(color='blue', alpha=0.3, label='150km Radius')
    ax.legend(handles=[circle_legend], loc='lower right') 
    
    # Save the map and close after to free memory
    save_file_location = base_dir / 'static' / 'images' /'geojson_map.png'
    plt.savefig(save_file_location, dpi=100)
    plt.close()
