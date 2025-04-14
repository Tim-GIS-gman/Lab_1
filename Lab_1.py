import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\madch\Documents\ArcGIS\Projects\APPS_LAB_1\APPS_LAB_1.gdb"


print("Available feature classes:", arcpy.ListFeatureClasses())


def buffer_layer(input_layer, output_name, distance):
    print(f"Buffering {input_layer} by {distance} feet...")
    arcpy.Buffer_analysis(input_layer, output_name, f"{distance} Feet", "FULL", "ROUND", "ALL")

def intersect_layers(input_layers, output_name):
    print(f"Intersecting layers: {input_layers}...")
    arcpy.Intersect_analysis(input_layers, output_name)

def spatial_join(target_layer, join_layer, output_name):
    print(f"Performing spatial join between {target_layer} and {join_layer}...")
    arcpy.SpatialJoin_analysis(target_layer, join_layer, output_name)

def count_at_risk_addresses(joined_layer):
    print("Counting at-risk addresses...")
    count = 0
    with arcpy.da.SearchCursor(joined_layer, ["Join_Count"]) as cursor:
        for row in cursor:
            if row[0] > 0:
                count += 1
    print(f"Number of at-risk addresses: {count}")
    return count

def main():
    # Prompt buffer distances
    distances = {
        "Mosquito_Larval_Sites": int(input("Buffer distance for Mosquito Larval Sites (ft): ")),
        "Wetlands": int(input("Buffer distance for Wetlands (ft): ")),
        "Lakes_and_Reservoirs": int(input("Buffer distance for Lakes and Reservoirs (ft): ")),
        "OSMP_Properties": int(input("Buffer distance for OSMP Properties (ft): "))
    }

    buffered_layers = []
    for layer, dist in distances.items():
        output = f"{layer}_Buffer"
        buffer_layer(layer, output, dist)
        buffered_layers.append(output)

    # Intersect all buffered layers
    intersect_output = "Risk_Intersect"
    intersect_layers(buffered_layers, intersect_output)

    # Spatial join with addresses
    joined_output = "Addresses_At_Risk"
    spatial_join("Addresses", intersect_output, joined_output)

    # Count addresses
    count_at_risk_addresses(joined_output)

if __name__ == "__main__":
    main()
