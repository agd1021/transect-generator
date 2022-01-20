# MaxRandomTransects_v05.py
# Created: 07/26/2017
# By: Allison Davis, Wildlife Technician
# University of Kentucky, Department of Forestry and Natural Resources
# For: Jonathan Matthews, Graduate student
# Draws random, nonoverlapping, nonparallel sampling transects within a polygon
# Last Updated: 07/28/2017 4:30 PM

# ------------------------------ Versions -------------------------------------
# v02: Saves trial counts
# v03: Uses RandomTransects_v03.py
# v04: Writes BestTrial to disc each time, so if program is interrupted,
# the feature class of the best outcome so far is retained.
# v04: Buffers each trasect by one transect_length instead of two, allowing
# for more transects to fit inside InputPolygon.
# v05: Uses LinearTransects function defition from RandomTransects_v05.py
# -----------------------------------------------------------------------------

# Imports
import arcpy
import os
import random
import csv

# Inputs
InputPolygon = arcpy.GetParameterAsText(0)
transect_length = float( arcpy.GetParameterAsText(1) )
max_transects = int( arcpy.GetParameterAsText(2) )
max_iterations = int( arcpy.GetParameterAsText(3) )
WorkspaceGDB = arcpy.GetParameterAsText(4)
OutputTransects = arcpy.GetParameterAsText(5)
CountsCSV = arcpy.GetParameterAsText(6) # Optional

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


def MaximizeNTransects(InputPolygon, transect_length, max_transects,
                       max_iterations, WorkspaceGDB, OutputTransects):
    """
    Iterates LinearTransects function up to max_iterations times to draw as
    as close to max_transects within InputPolygon as possible.

    Dependences:
    import arcpy
    """

    arcpy.AddMessage("Initializing iterator...")
    i = 0
    BestCount = 0
    BestTrialFC = os.path.join( WorkspaceGDB, "BestTrial" )
    TrialCounts = ["Counts"]

    while i < max_iterations:

        arcpy.AddMessage("\nIteration {0} of {1}".format(i, max_iterations))
        
        # Runs Random Transect Tool
        TargetSamplingProportion = 1.0
        Trial = LinearTransects(InputPolygon, transect_length, max_transects,
                    TargetSamplingProportion, OutputTransects, WorkspaceGDB)

        # Count transects drawn in this trial
        TrialCount = int( arcpy.GetCount_management(Trial).getOutput(0) )
        arcpy.AddMessage("\n\tNumber of transects drawn in this iteration: {}"
                         .format(TrialCount) )

        # If PresentTrial equals maximum transect goal, close the 'while' loop.
        if TrialCount == max_transects:
            arcpy.AddMessage("Maximum number of transects achieved!")
            
            BestTrial = Trial
            arcpy.AddMessage("\nWriting to file...")
            arcpy.CopyFeatures_management( BestTrial, OutputTransects)
            arcpy.Delete_management( Trial )
            
            i = max_iterations

        # Otherwise, compare TrialCount to BestCount
        else:

            if TrialCount > BestCount:
                arcpy.AddMessage("\tBest count improved!") 

                # Present trial becomes BestTrial
                BestCount = TrialCount
                BestTrial = Trial

                # Replace OutputTransects with new BestTrial
                if i != 0: 
                    arcpy.Delete_management( BestTrialFC )
                    # When i == 0, OutputTransects doesn't exist yet
                
                arcpy.AddMessage("\n\tWriting new BestTrial to file...")
                arcpy.CopyFeatures_management( BestTrial, BestTrialFC )
                arcpy.Delete_management( Trial )
                    
            else:
                arcpy.AddMessage("\tBest count is unchanged.")
                arcpy.Delete_management( Trial )

            # Continue 'while' loop
            arcpy.AddMessage("\n\tCurrent highest count: {}".format(BestCount) )
            if CountsCSV:
                TrialCounts.append(TrialCount)
            i += 1

    # Copy the BestTrial to disc
    arcpy.CopyFeatures_management( BestTrialFC, OutputTransects )
    arcpy.Delete_management( BestTrialFC )
    arcpy.AddMessage("\nFinal transect count: {}".format(BestCount) )

    return OutputTransects, TrialCounts


# Environments
arcpy.env.overwriteOutput = True

# Processing
transects, counts = MaximizeNTransects(InputPolygon, transect_length,
                                       max_transects, max_iterations,
                                       WorkspaceGDB, OutputTransects)

# Create CSV and histogram of trial counts
if CountsCSV:
    arcpy.AddMessage("\nSaving frequencies to CSV file...")
    with open(CountsCSV, 'wb') as f:
        wr = csv.writer(f, delimiter = ',')
        wr.writerow(counts)

arcpy.AddMessage("Done.")











            
