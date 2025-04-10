import folium

def generate_map_with_radius(locations: list, radius=150) -> folium.Map:
    """
    Generate a map with locations and a radius around each location.

    Args:
        locations (list): A list of tuples containing latitude and longitude of locations.
        radius (int): The radius in kilometers to draw around each location.

    Returns:
        folium.Map: A folium map object with the locations and radius.
    """

    # Make the map of the Netherlands
    base_map = folium.Map(location=(51.972, 5.710), zoom_start=6)
    folium.GeoJson("netherlands.geojson", name="Netherlands").add_to(base_map)
    folium.LayerControl().add_to(base_map)

    # Add markers for each location with a circle representing the radius
    for lat, lon in locations:
        folium.Marker(location=[lat, lon], popup=f"Location: {lat}, {lon}").add_to(base_map)
        folium.Circle(
            location=[lat, lon],
            radius=radius * 1000,  
            color='blue',
            fill=True,
            fill_opacity=0.2,
        ).add_to(base_map)

    base_map.save("map.html")
    return base_map

generate_map_with_radius([])