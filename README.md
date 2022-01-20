# transect-generator
Python Toolbox for ArcMap Desktop that creates random transects in a polygon

## Prepared for
Matthews, Jonathan A., "Quantifying white-tailed deer density and its impact on agricultural systems" (2019). Theses and Dissertations--Forestry and Natural Resources. 47. https://uknowledge.uky.edu/forestry_etds/47

## Files
### RandomTransectGenerator.zip
Python script toolbox containing RandomTransects.py and MaxRandomTransects.py
### RandomTransects.py
Given a single input polygon, transect length, and buffer distance around transects, iteratively places non-intersecting transects of random bearings until either the number of attempts maxes out or a satisfactory proportion of the polygon is covered. 
### MaxRandomTransects.py
Iterates "Random Transects" in a while-loop with user-defined end-point to maximize the number of random transects placed in the polygon.
### PrincetonFarm.shp
Shapefile of a single polygon in which to place transects. University of Kentucky Princeton Research farm.
### RandomTransectsAlgorithm.jpg
Step-by-step illustration of how the MaxRandomTransects.py algorithm works.
### RandomTransectsExample-Princeton20.jpg
Map of random transects generated with this toolbox in PrincetonFarm.shp polygon.
