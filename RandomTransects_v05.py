# RandomTransects_v05.py
# Created: 07/21/2017
# By: Allison Davis, Wildlife Technician
# University of Kentucky, Department of Forestry and Natural Resources
# For: Jonathan Matthews, Graduate student
# Draws random, nonoverlapping, nonparallel sampling transects within a polygon
# Last Updated: 07/28/2017 3:50 PM

# ----------------------------- Versions --------------------------------------
# v02: After drawing and buffering each transect, checks that the area of the
# remaining polygon is non-zero before proceeding to draw the next
# transect. Reduces processing time by stopping the program when there
# is no room left in the study area to draw new transects, even if the
# input max_transects limit has not been reached.
#
# v03: Does not buffer edge of the InputPolygon. Instead, after drawing each
# transect, saves transect only if it is completely contained within
# InputPolygon. Removes edge bias from previous method.
#
# v04: Buffers each transect by only 1 transect_length instead of 2, allowing
# more transects to fit into the InputPolygon.
#
# v05: If transect exits UnsampledZone, calculates area of UnsampledZone as a
# proportion of total InputPolygon area. If proportion has not reached
# TargetSamplingProportion (new input parameter 3), attempts to redraw
# transect.
# -----------------------------------------------------------------------------


# Imports
import arcpy, os, random

# Inputs
InputPolygon = arcpy.GetParameterAsText(0)
transect_length = float( arcpy.GetParameterAsText(1) )
max_transects = int( arcpy.GetParameterAsText(2) )
TargetSamplingProportion = float( arcpy.GetParameterAsText(3) )
WorkspaceGDB = arcpy.GetParameterAsText(4)
OutputTransects = arcpy.GetParameterAsText(5)

# Function definitions
def LinearTransects(InputPolygon, transect_length, max_transects,
                    TargetSamplingProportion, OutputTransects, WorkspaceGDB):
    """
    Draws n_transects within InputPolygon and returns OutputTransects.

    InputPolygon = polygon feature class with a single polygon
    transect_length = desired length of transect segments,
                    in linear units of the InputPolygon
    max_transects = desired maximum number of transects to be drawn
                *** This number may not be reached due to space constraints! ***
    max_iterations = number to times to attempt drawing transects
    OutputTransects = output line feature class
    WorkspaceGDB = any geodatabase that has space for the intermediate files

    Dependencies:
    import arcpy
    import os
    import random
    """

    # --------------------- Sampling Zone Parameters ------------------------ #
    
    BoundaryLyr = os.path.join(WorkspaceGDB, "Boundary") 
    arcpy.MakeFeatureLayer_management(InputPolygon, BoundaryLyr)
    with arcpy.da.SearchCursor( BoundaryLyr, ["SHAPE@AREA"] ) as cursor:
        TotalArea = [ row[0] for row in cursor ][0]
    
    # ----------------------Initialize 'while' loops ------------------------ #
    
    UnsampledArea = TotalArea
    UnsampledZone = BoundaryLyr
    
    UnsampledProportion = 1.0
    MaxUnsampledProportion = 1.0 - TargetSamplingProportion
   
    n = 0
    AllTransects = []

    

    while (UnsampledProportion>MaxUnsampledProportion) and (n<max_transects):

        # -------------------- Create Random Transect ----------------------- #

        arcpy.AddMessage( "\tCreating transect {}...".format(n) )
        
        # Drop a random point
        arcpy.AddMessage("\t\tCreating random start point...")
        arcpy.CreateRandomPoints_management(WorkspaceGDB, "randpt",
                                            UnsampledZone, "", 1)
        Vertex = os.path.join(WorkspaceGDB, "randpt")

        # Add fields x, y, distance, and bearing
        arcpy.AddMessage("\t\tAdding attibutes to the point...")
        arcpy.AddField_management(Vertex, "x", "DOUBLE")
        arcpy.AddField_management(Vertex, "y", "DOUBLE")
        arcpy.AddField_management(Vertex, "distance", "FLOAT")
        arcpy.AddField_management(Vertex, "bearing", "FLOAT")

        # Update attribute table with data for bearing distance tool
        arcpy.AddMessage("\t\tGenerating a random bearing...")
        with arcpy.da.UpdateCursor(Vertex, ["SHAPE@XY",
                                            "x", "y",
                                            "distance",
                                            "bearing"]) as cursor:
            for row in cursor:
                row[1] = row[0][0]
                row[2] = row[0][1]
                row[3] = transect_length
                row[4] = random.randint(1,360)
                cursor.updateRow(row)

        # Create a table to feed to Bearing Distance to line tool
        arcpy.AddMessage("\t\tSaving attributes as a table...")
        arcpy.TableToTable_conversion(Vertex, WorkspaceGDB, "RandPtTable")
        Table = os.path.join(WorkspaceGDB, "RandPtTable")

        # Generate transect
        arcpy.AddMessage("\t\tDrawing transect line...")
        Transect = os.path.join(WorkspaceGDB, "Transect{}".format(n) )
        arcpy.BearingDistanceToLine_management(Table, Transect,
                                               x_field = 'x', y_field = 'y',
                                               distance_field = 'distance',
                                               bearing_field = 'bearing',
                                               spatial_reference = Vertex )

        # ---------------------- Verify Transect ------------------------ #
        
        # Check that Transect is completely contained in UnsampledZone
        TransectLyr = os.path.join("in_memory", "transect_lyr")
        arcpy.MakeFeatureLayer_management(Transect, TransectLyr)
        arcpy.SelectLayerByLocation_management(TransectLyr,
                                               "COMPLETELY_WITHIN",
                                               UnsampledZone, '',
                                               "NEW_SELECTION")
        Inside = int( arcpy.GetCount_management(TransectLyr).getOutput(0) )
        
        if Inside == 1:
        
            AllTransects.append(Transect)
            arcpy.AddMessage("\t\tFinished drawing transect {}".format(n) )

            # ------------------ Update UnsampledZone ------------------- #
            
            # Buffer transect by the transect length
            arcpy.AddMessage("\t\tBuffering transect {}...".format(n) )
            TransBuffer = os.path.join(WorkspaceGDB,
                                       "Transect{}Buf".format(n) )
            arcpy.Buffer_analysis(TransectLyr, TransBuffer, transect_length )

            # Erase buffer from UnsampledZone
            arcpy.AddMessage(
                "\t\tErasing transect buffer from unsampled zone..." )
            UnsampledZone_Erase = os.path.join("in_memory",
                                               "UnsampledZone{}".format(n))
            arcpy.Erase_analysis(UnsampledZone, TransBuffer,
                                 UnsampledZone_Erase, '')
            arcpy.Delete_management(TransBuffer)

            # Get new UnsampledArea
            with arcpy.da.SearchCursor( UnsampledZone,
                                        ["SHAPE@AREA"] ) as cursor:
                UnsampledArea = [ row[0] for row in cursor ][0]

            # Update 'while' loop conditions
            UnsampledProportion = UnsampledArea / TotalArea
            UnsampledZone = UnsampledZone_Erase

            n += 1

        else:
            arcpy.AddMessage("\t\t---------------------------------")
            arcpy.AddMessage("\t\tTransect {} exited UnsampledZone.".format(n))
            arcpy.AddMessage("\t\t---------------------------------")
            arcpy.Delete_management(Transect)

            # If UnsampledArea is too small, escape the 'while' loop
            if UnsampledArea < (2.0*transect_length):
                n = max_transects
            # Otherwise, try to draw the next transect.
            else:
                n += 1

        # Clean up
        arcpy.AddMessage("\t\tCleaning up workspace..." )
        arcpy.Delete_management(Vertex)
        arcpy.Delete_management(Table)

        arcpy.AddMessage(
            "\t\tUnsampled area: {0:.2f} m".format(UnsampledArea) )
        arcpy.AddMessage(
            "\t\tUnsampled proportion: {0:.3f}".format(UnsampledProportion) )

    # ------------------------- END 'WHILE' LOOP ---------------------------- #


    # Combine transects into one shapefile
    arcpy.AddMessage("\tMerging transects into one dataset...")
    arcpy.Merge_management(AllTransects, OutputTransects, '')

    # Count features
    Result = int( arcpy.GetCount_management(OutputTransects).getOutput(0) )
    arcpy.AddMessage("\tTotal number of transects drawn: {}".format(Result) )

    # Clean up
    arcpy.AddMessage("\tCleaning up...")
    for t in AllTransects:
        arcpy.Delete_management(t)

    return OutputTransects


# Environments
arcpy.env.overwriteOutput = True

# Processing
transects = LinearTransects(InputPolygon, transect_length, max_transects,
                            TargetSamplingProportion, OutputTransects,
                            WorkspaceGDB)

arcpy.AddMessage("Script complete.")
