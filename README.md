# transect-generator
Python Toolbox for ArcMap Desktop that creates random transects in a polygon

Prepared for: Matthews, Jonathan A., "Quantifying white-tailed deer density and its impact on agricultural systems" (2019). Theses and Dissertations--Forestry and Natural Resources. 47. https://uknowledge.uky.edu/forestry_etds/47

## Tools:
### 0) Random Transects
Given a single input polygon, transect length, and buffer distance around transects, iteratively places non-intersecting transects of random bearings until no more can be placed 
or the number of attempts maxes out. 
### 1) Maximize Number of Random Transects
Iterates "0) Random Transects" in a while-loop with user-defined end-point to maximize the number of random transects placed in the polygon.
### 2) Transect Points and Bearing to CSV
Given an input transect shapefile, drops points at the start, end, and midpoint of every transect. Outputs coordinate locations as a CSV.
### 3) Textfile to Histogram
"1) Maximize Number of Random Transects" outputs a textfile listing the number of random transects placed in each attempt. "3) Textfile to Histogram" creates a histogram from that output textfile.

## Sample data:
### PrincetonFarm.shp shapefile of a singly polygon in which to place transects.
