import arcpy

fc = arcpy.GetParameterAsText(0)
zip = arcpy.GetParameterAsText(1)
resultsWorkspace = arcpy.GetParameterAsText(2)
search_distance = arcpy.GetParameterAsText(3)
nameField = arcpy.GetParameterAsText(4)
field_value = arcpy.GetParameterAsText(5)
arcpy.env.workspace = resultsWorkspace

# Make a feature layer
arcpy.MakeFeatureLayer_management(fc, "Facilit")
arcpy.MakeFeatureLayer_management(zip, "Zip")

arcpy.SelectLayerByLocation_management('Facilit', 'WITHIN_A_DISTANCE_GEODESIC', 'Zip', search_distance, 'NEW_SELECTION')
arcpy.SelectLayerByAttribute_management("Facilit", "SUBSET_SELECTION",
                                        '"' + str(nameField) + '" =' + "'" + str(field_value) + "'")
arcpy.AddMessage("Create new Selection")
# Create a new feature class similar to facilities.shp in Results directory
newshp = "facilities_Distance_" + search_distance + '.shp'
arcpy.CreateFeatureclass_management(arcpy.env.workspace, newshp, "POINT", spatial_reference="Facilit")
arcpy.AddMessage("Create new Facilities shape file")

# Create fields
new_fields = ['ADDRESS', 'NAME', 'FACILITY']
for i in new_fields:
    arcpy.AddField_management(newshp, i, "TEXT")
arcpy.AddMessage("Create new fields in " + newshp)

# insert search fields from "Facilit to facilities_Distance_3000.shp
search = ('SHAPE@XY', 'ADDRESS', 'NAME', 'FACILITY')
with arcpy.da.InsertCursor(newshp, search) as cursorInsert, arcpy.da.SearchCursor("Facilit", search) as cursorSearch:
    for row in cursorSearch:
        cursorInsert.insertRow(row)
arcpy.AddMessage("Updated fields: " + (str(search)))

# Create a new field COLLEGE_NAME
newfield = field_value[:5] + '_NAME'
arcpy.AddField_management(newshp, newfield, "DOUBLE")
arcpy.AddMessage("Create new fields field COLLEGE_NAME")

value = []
with arcpy.da.SearchCursor("Facilit", ('FAC_ID',)) as cursorS:
    for row in cursorS:
        value.append(row)

with arcpy.da.UpdateCursor(newshp, newfield, ) as cursorUP:
    v = 0
    for u in cursorUP:
        u = value[v]
        cursorUP.updateRow(u)
        v += 1
arcpy.AddMessage("Insert data into new fields field COLLEGE_NAME")

arcpy.Delete_management("Facilit")
arcpy.Delete_management("Zip")
