import yaml
import arcpy
from etl.GSheetsEtl import GSheetsEtl


def load_config():
    with open('config/wnvoutbreak.yaml', 'r') as file:
        return yaml.safe_load(file)

def buffer_layer(input_layer, output_layer, distance):
    print(f"Buffering {input_layer} by {distance} feet...")
    arcpy.Buffer_analysis(input_layer, output_layer, f"{distance} Feet", "FULL", "ROUND", "ALL")

def erase_analysis(input_layer, erase_layer, output_layer):
    print(f"Erasing {erase_layer} from {input_layer}...")
    arcpy.Erase_analysis(in_features=input_layer, erase_features=erase_layer, out_feature_class=output_layer)

def spatial_join(target, join_layer, output_layer):
    print(f"Joining {target} with {join_layer}...")
    arcpy.SpatialJoin_analysis(target, join_layer, output_layer)

def count_addresses(joined_layer):
    print("Counting addresses to notify...")
    count = 0
    with arcpy.da.SearchCursor(joined_layer, ["Join_Count"]) as cursor:
        for row in cursor:
            if row[0] > 0:
                count += 1
    print(f"✅ {count} Boulder addresses need to be notified.")
    return count
def export_notified_addresses(input_fc, output_fc):
    print(f"Exporting only addresses with Join_Count > 0 to {output_fc}...")
    arcpy.MakeFeatureLayer_management(input_fc, "temp_layer", "Join_Count > 0")
    arcpy.CopyFeatures_management("temp_layer", output_fc)
    print("Export complete.")



def main():
    config = load_config()

    arcpy.env.workspace = f"{config['proj_dir']}APPS_LAB_1.gdb"
    arcpy.env.overwriteOutput = True

    print("Workspace set to:", arcpy.env.workspace)
    print("Available layers:", arcpy.ListFeatureClasses())

    print("\nRunning ETL process...")
    etl = GSheetsEtl(config)
    etl.process()

    buffer_layer("Avoid_Points", "Avoid_Points_Buffer", 1500)
    erase_analysis("Risk_Intersect", "Avoid_Points_Buffer", "Risk_Intersect_Final")
    spatial_join("Addresses", "Risk_Intersect_Final", "Addresses_To_Notify")
    count_addresses("Addresses_To_Notify")

    export_notified_addresses("Addresses_To_Notify", "Addresses_To_Notify_Clean")


if __name__ == "__main__":
    main()



