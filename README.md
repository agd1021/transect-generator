# transect-generator
Python Toolbox for ArcMap Desktop that creates random transects in a polygon

## Prepared for
Matthews, Jonathan A., "Quantifying white-tailed deer density and its impact on agricultural systems" (2019). Theses and Dissertations--Forestry and Natural Resources. 47. https://uknowledge.uky.edu/forestry_etds/47

## Tools:
### Random Transects
Given a single input polygon, transect length, and buffer distance around transects, iteratively places non-intersecting transects of random bearings until either the number of attempts maxes out or a satisfactory proportion of the polygon is covered. 
### Maximize Number of Random Transects
Iterates "Random Transects" in a while-loop with user-defined end-point to maximize the number of random transects placed in the polygon.

## Sample data:
<b>PrincetonFarm.shp</b> shapefile of a single polygon in which to place transects.
