# TransectPointsAndBearings.py
# Created: 07/21/2017
# Last Updated: 11:30 AM 07/21/2017
# By: Allison Davis, Wildlife Technician
# University of Kentucky, Department of Forestry and Natural Resources
# For: Jonathan Matthews, Graduate student
# Exports a csv file with GPS coordinates of transect start/end points and bearings

import arcpy
import os
import csv

# Inputs
LineSegments = arcpy.GetParameterAsText(0)
OutputSR = arcpy.GetParameterAsText(1)
GDB = arcpy.GetParameterAsText(2)
OutCSV = arcpy.GetParameterAsText(3)

# LineSegments = r"C:\Users\User\Documents\Springer\Matthews\DeerDistanceSamplingUTM.gdb\Transects\JamesWilsonTransects"
# OutputSR = arcpy.SpatialReference('WGS 1984')

# Project LineSegments into the desired coordinate system
arcpy.AddMessage("Checking coordinate system...")

InputSR = arcpy.Describe(LineSegments).spatialReference
LineSeg = os.path.join(GDB, "lines")

if InputSR != OutputSR:
    
    arcpy.AddMessage("Projecting lines...")
    arcpy.Project_management(LineSegments, LineSeg, OutputSR)

    ResultSR = arcpy.Describe(LineSeg).spatialReference
    arcpy.AddMessage("Lines projected to " + str(ResultSR.name) )
    
else:
    arcpy.CopyFeatures_management(LineSegments, LineSeg)

# Erase current attribute table
delFields = [f.name for f in arcpy.ListFields(LineSeg) if f.required == False]
for f in delFields:
    arcpy.DeleteField_management(LineSeg, f)

# Add geometry attributes
arcpy.AddMessage("Extracting geometric attributes...")
properties = ["LINE_START_MID_END", "LINE_BEARING"]
arcpy.AddGeometryAttributes_management( LineSeg, properties )

# Export attribute table to CSV
arcpy.TableToTable_conversion(LineSeg, os.path.split(OutCSV)[0], os.path.split(OutCSV)[1])

# Clean up
arcpy.AddMessage("Cleaning up workspace...")
# arcpy.Delete_management(LineSeg)

arcpy.AddMessage("Script complete.")


