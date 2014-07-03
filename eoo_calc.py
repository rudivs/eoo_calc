"""Reads a tab separated text file supplied as an argument and translates DDE
and DDS values as (x,y) point coordinates, from which outer hulls are derived
for three point categories. The area of each outer hull is calculated and 
saved to a text file."""

import csv,sys
import chull
from osgeo import ogr,osr


def CalculateArea(poly):
	"""Takes a polygon in WGS84 geographic coords as input and calculates the 
	area by intersecting it with the six UTM zones covering Africa south of 
	the equator, applying the appropriate projection and summing the resulting
    areas. Returns area as a float.
	"""

	area = float(0)  #initialise area aggregator
	
	# Calculate the area of the intersection of the EOO with each UTM zone
	# [1] instantiate geometry of type polygon
	# [2] calculate intersection
	# [3] transform intersected polygon from geographic coords to UTM
	# [4] add area of polygon to cumulative total
	
	i = ogr.Geometry(ogr.wkbPolygon)   # [1]
    
	i = poly.Intersection(utm32s)      # [2]
	i.Transform(transUTM32s)           # [3]
	area += i.GetArea()                # [4]
    
	i = poly.Intersection(utm33s)      # [2]
	i.Transform(transUTM33s)           # [3]
	area += i.GetArea()                # [4]
	
	i = poly.Intersection(utm34s)
	i.Transform(transUTM34s)
	area += i.GetArea()
	
	i = poly.Intersection(utm35s)
	i.Transform(transUTM35s)
	area += i.GetArea()
	
	i = poly.Intersection(utm36s)
	i.Transform(transUTM36s)
	area += i.GetArea()
    
	i = poly.Intersection(utm37s)
	i.Transform(transUTM37s)
	area += i.GetArea()    
	
	return area/1000000


# Prepare spatial references
# [5] Create spatial reference instance
# [6] Set spatial reference using Proj.4 string
# [7] Set spatial reference using EPSG code
# [8] Define coordinate transformation

srWGS84 = osr.SpatialReference()		                     # [5]
srWGS84.ImportFromProj4('+proj=longlat +datum=WGS84')        # [6]

srUTM32s = osr.SpatialReference()
srUTM32s.ImportFromEPSG(32732)                               # [7]
transUTM32s = osr.CoordinateTransformation(srWGS84,srUTM32s) # [8]

srUTM33s = osr.SpatialReference()
srUTM33s.ImportFromEPSG(32733)                               # [7]
transUTM33s = osr.CoordinateTransformation(srWGS84,srUTM33s) # [8]

srUTM34s = osr.SpatialReference()
srUTM34s.ImportFromEPSG(32734)
transUTM34s = osr.CoordinateTransformation(srWGS84,srUTM34s)

srUTM35s = osr.SpatialReference()
srUTM35s.ImportFromEPSG(32735)
transUTM35s = osr.CoordinateTransformation(srWGS84,srUTM35s)

srUTM36s = osr.SpatialReference()
srUTM36s.ImportFromEPSG(32736)
transUTM36s = osr.CoordinateTransformation(srWGS84,srUTM36s)

srUTM37s = osr.SpatialReference()
srUTM37s.ImportFromEPSG(32737)
transUTM37s = osr.CoordinateTransformation(srWGS84,srUTM37s)

#Create utm geometries
ring = ogr.Geometry(ogr.wkbLinearRing) # create ring instance
ring.AddPoint(6,0)                    # add points to ring
ring.AddPoint(6,-80)
ring.AddPoint(12,-80)
ring.AddPoint(12,0)
ring.AddPoint(6,0)                    # last point closes ring
utm32s = ogr.Geometry(ogr.wkbPolygon)  # create polygon instance
utm32s.AddGeometry(ring)               # add ring to polygon

ring = ogr.Geometry(ogr.wkbLinearRing) # create ring instance
ring.AddPoint(12,0)                    # add points to ring
ring.AddPoint(12,-80)
ring.AddPoint(18,-80)
ring.AddPoint(18,0)
ring.AddPoint(12,0)                    # last point closes ring
utm33s = ogr.Geometry(ogr.wkbPolygon)  # create polygon instance
utm33s.AddGeometry(ring)               # add ring to polygon

ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(18,0)
ring.AddPoint(18,-80)
ring.AddPoint(24,-80)
ring.AddPoint(24,0)
ring.AddPoint(18,0)
utm34s = ogr.Geometry(ogr.wkbPolygon)
utm34s.AddGeometry(ring)

ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(24,0)
ring.AddPoint(24,-80)
ring.AddPoint(30,-80)
ring.AddPoint(30,0)
ring.AddPoint(24,0)
utm35s = ogr.Geometry(ogr.wkbPolygon)
utm35s.AddGeometry(ring)

ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(30,0)
ring.AddPoint(30,-80)
ring.AddPoint(36,-80)
ring.AddPoint(36,0)
ring.AddPoint(30,0)
utm36s = ogr.Geometry(ogr.wkbPolygon)
utm36s.AddGeometry(ring)

ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(36,0)
ring.AddPoint(36,-80)
ring.AddPoint(42,-80)
ring.AddPoint(42,0)
ring.AddPoint(36,0)
utm37s = ogr.Geometry(ogr.wkbPolygon)
utm37s.AddGeometry(ring)

hist = []               # coords of all historical localities
cmax = []               # coords of possibly extant sites (current maximum)
cmin = []               # coords of known sites (current minimum)
result = []             # list of return areas (hist,cmax,cmin)

# Rules for EOO calculations
# Calculation 1: historical EOO = all points
# Calculation 2: current max = extant + uncertain
# Calculation 3: current min = extant

# open file given as first argument for reading, and populate hist,cmax,cmin
try:
	with open(sys.argv[1],'rb') as f:  
		# read csv file as dictionary, using tab as the delimiter
		locfile = csv.DictReader(f,delimiter='\t')  
		for loc in locfile:
			# Add all points to historical list, as (x,y) tuples
			hist.append([float(loc['DDE']),float(loc['DDS'])])
			if loc['LocStatus'] == "Extant":  
				cmax.append([float(loc['DDE']),float(loc['DDS'])])
				cmin.append([float(loc['DDE']),float(loc['DDS'])])
			if loc['LocStatus'] == "Uncertain":  
				cmax.append([float(loc['DDE']),float(loc['DDS'])])
except IndexError, e:     #IndexError is raised when there are no arguments
	print "No locations file was supplied."
	raise SystemExit
except IOError, e:        #IOError is raised when there's a problem opening file
	print "Error reading locations file."
	raise SystemExit
	
# Create geometry for historical points
if len(hist) > 2 :                             # enough points for a polygon
	hist_hull = chull.convexHull(hist)         # get points defining convex hull
	ring = ogr.Geometry(ogr.wkbLinearRing)
	for point in hist_hull:
		ring.AddPoint(point[0],point[1])       # create ring from convex hull
	hist_poly = ogr.Geometry(ogr.wkbPolygon)   # instantiate polygon
	hist_poly.AddGeometry(ring)		           # add ring to polygon
	result.append(CalculateArea(hist_poly))    # add polygon area to result
	#outfile.writerow(['Hist',CalculateArea(hist_poly)])
else:
	result.append("")         # add empty string if impossible to calculate area

# Create geometry for current maximum points
if len(cmax) > 2 :
	cmax_hull = chull.convexHull(cmax)
	ring = ogr.Geometry(ogr.wkbLinearRing)
	for point in cmax_hull:
		ring.AddPoint(point[0],point[1])
	cmax_poly = ogr.Geometry(ogr.wkbPolygon)
	cmax_poly.AddGeometry(ring)
	result.append(CalculateArea(cmax_poly))
	#outfile.writerow(['CMax',CalculateArea(cmax_poly)])
else:
	result.append("")

# Create geometry for current minimum points
if len(cmin) > 2 :
	cmin_hull = chull.convexHull(cmin)
	ring = ogr.Geometry(ogr.wkbLinearRing)
	for point in cmin_hull:
		ring.AddPoint(point[0],point[1])
	cmin_poly = ogr.Geometry(ogr.wkbPolygon)
	cmin_poly.AddGeometry(ring)
	result.append(CalculateArea(cmin_poly))
	#outfile.writerow(['CMin',CalculateArea(cmin_poly)])
else:
	result.append("")

# prefix supplied filename with eoo_ and open it for writing as csv file
try:
	with open(sys.argv[2],'w') as fw:
		outfile = csv.writer(fw,delimiter='\t')
		outfile.writerow(['Hist','CMax','CMin'])    # first line contains titles
		outfile.writerow(result)       # write the three results to the csv file
except IOError, e:
	print "Error writing to output file."
	raise SystemExit
