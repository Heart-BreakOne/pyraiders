# This can be used for visually testing whether the coordinates and dimensions are what they are supposed to be.

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import box, Polygon, MultiPolygon, LineString
from shapely.ops import unary_union
from shapely.geometry.collection import GeometryCollection

#Generate polygon objects using the x,y, width and length attributes.

# Create polygons based on the coordinates and dimensions
def create_polygons(data):
    polygons = []

    # Check if data is None or not a dictionary
    if data is None or not isinstance(data, dict):
        return polygons

    for key, item in data.items():
        # Skip entries with non-dictionary values or None
        if not isinstance(item, dict) or not item:
            continue

        x, y, width, height = (
            float(item.get("x", 0)),
            float(item.get("y", 0)),
            float(item.get("width", 0)),
            float(item.get("height", 0)),
        )

        # Create a polygon using Shapely
        polygon = Polygon(
            [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        )

        polygons.append({key: polygon})

    return polygons

def cut_polygon(polygon, cut_line):
    # Cut the polygon with a line and return the resulting polygons
    if polygon.intersects(cut_line):
        return [polygon.difference(cut_line)]
    else:
        return [polygon]


def process_polygons(viewer_polygons, all_units_polygons):
    # Combine all other polygons into a single MultiPolygon
    other_polygons = MultiPolygon(all_units_polygons)

    # List to store the final non-overlapping polygons
    result_polygons = []

    for viewer_polygon in viewer_polygons:
        # Check for intersections with other polygons
        if viewer_polygon.intersects(other_polygons):
            # Iterate over other polygons and cut the viewer_polygon
            for other_polygon in all_units_polygons:
                cut_lines = viewer_polygon.intersection(other_polygon)
                if cut_lines.is_empty:
                    continue

                # Cut the viewer_polygon with the cut_lines
                cut_result = [viewer_polygon]
                if isinstance(cut_lines, MultiPolygon):
                    for cut_line in cut_lines.geoms:
                        cut_result = cut_polygon(cut_result[0], cut_line)
                else:
                    cut_result = cut_polygon(cut_result[0], cut_lines)

                # Update viewer_polygon with the non-overlapping parts
                viewer_polygon = cut_result[0]

                # Add the non-overlapping parts to the result
                result_polygons.extend(cut_result)

        # If viewer_polygon doesn't intersect with other_polygons, add it as is
        else:
            result_polygons.append(viewer_polygon)

    return result_polygons


# Generate an image with the polygons
    output_plot(cap_nm, result_polygons)
    
# Generate a png with the map plot by passing the captain name string and a list of Polygon objects
def output_plot(cap_nm, rf_viewer_zones):
    # Create a plot
    fig, ax = plt.subplots()

    # Plot each polygon
    for zones in rf_viewer_zones:
        x, y = zones.exterior.xy
        ax.fill(x, y, alpha=0.5)

    # Set axis labels
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    now = datetime.utcnow()
    # Save the plot to a file instead of showing it
    plt.savefig(f"{cap_nm}_output_plot_{now}.png")
    plt.close()
