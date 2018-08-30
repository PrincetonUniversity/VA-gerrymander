"""
continuous_measures: Functions to calculate compactness measures, and
components of compactness measures, in Euclidean space. 

From Voting Rights Data Institute, 2018, https://github.com/gerrymandr/VRDI_DC

"""

import geopandas as gpd
import random
import math

def make_circle(points):
	# Convert to float and randomize order
	shuffled = [(float(x), float(y)) for (x, y) in points]
	random.shuffle(shuffled)
	
	# Progressively add points to circle or recompute circle
	c = None
	for (i, p) in enumerate(shuffled):
		if c is None or not is_in_circle(c, p):
			c = _make_circle_one_point(shuffled[ : i + 1], p)
	return c
	
# One boundary point known
def _make_circle_one_point(points, p):
	c = (p[0], p[1], 0.0)
	for (i, q) in enumerate(points):
		if not is_in_circle(c, q):
			if c[2] == 0.0:
				c = make_diameter(p, q)
			else:
				c = _make_circle_two_points(points[ : i + 1], p, q)
	return c


# Two boundary points known
def _make_circle_two_points(points, p, q):
	circ = make_diameter(p, q)
	left = None
	right = None
	px, py = p
	qx, qy = q
	
	# For each point not in the two-point circle
	for r in points:
		if is_in_circle(circ, r):
			continue
		
		# Form a circumcircle and classify it on left or right side
		cross = _cross_product(px, py, qx, qy, r[0], r[1])
		c = make_circumcircle(p, q, r)
		if c is None:
			continue
		elif cross > 0.0 and (left is None or _cross_product(px, py, qx, qy, c[0], c[1]) > _cross_product(px, py, qx, qy, left[0], left[1])):
			left = c
		elif cross < 0.0 and (right is None or _cross_product(px, py, qx, qy, c[0], c[1]) < _cross_product(px, py, qx, qy, right[0], right[1])):
			right = c
	
	# Select which circle to return
	if left is None and right is None:
		return circ
	elif left is None:
		return right
	elif right is None:
		return left
	else:
		return left if (left[2] <= right[2]) else right


def make_circumcircle(p0, p1, p2):
	# Mathematical algorithm from Wikipedia: Circumscribed circle
	ax, ay = p0
	bx, by = p1
	cx, cy = p2
	ox = (min(ax, bx, cx) + max(ax, bx, cx)) / 2.0
	oy = (min(ay, by, cy) + max(ay, by, cy)) / 2.0
	ax -= ox; ay -= oy
	bx -= ox; by -= oy
	cx -= ox; cy -= oy
	d = (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) * 2.0
	if d == 0.0:
		return None
	x = ox + ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
	y = oy + ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
	ra = math.hypot(x - p0[0], y - p0[1])
	rb = math.hypot(x - p1[0], y - p1[1])
	rc = math.hypot(x - p2[0], y - p2[1])
	return (x, y, max(ra, rb, rc))


def make_diameter(p0, p1):
	cx = (p0[0] + p1[0]) / 2.0
	cy = (p0[1] + p1[1]) / 2.0
	r0 = math.hypot(cx - p0[0], cy - p0[1])
	r1 = math.hypot(cx - p1[0], cy - p1[1])
	return (cx, cy, max(r0, r1))


_MULTIPLICATIVE_EPSILON = 1 + 1e-14

def is_in_circle(c, p):
	return c is not None and math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] * _MULTIPLICATIVE_EPSILON


# Returns twice the signed area of the triangle defined by (x0, y0), (x1, y1), (x2, y2).
def _cross_product(x0, y0, x1, y1, x2, y2):
	return (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)

    
def _discrete_perimeter(geo, geo_cell):
    """Not implemented"""
    
    return None

def _continuous_perimeter(geo):
    """returns geo.length"""
    
    return geo.length

def _discrete_area(geo, geo_cell):
    """Not implemented"""
    
    return None

def _continuous_area(geo):
    """returns geo.area"""
    
    return geo.area

def perimeter(geo, geo_cell = None):
    """
    Return perimeters of geometries in GeoSeries as Series of floats.
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
        
    This function calculates continuous or discrete perimeter. 
    
    Continuous (Euclidean) perimeter is calculated if only geo argument is 
    provided. Currently this function just returns GeoSeries.length. 
    Future improvements could include:
        
        * Checking for lat-long coordinate system and performing geodetic
        measurement
        * Determining appropriate local CRS (most likely a State Plane or UTM
        zone) and performing calculation in that CRS.
        
    NOT YET OPERATIONALIZED: Discrete perimeter is calculated if a second
    geographic argument is provided that represents the "cells" or "building 
    blocks" of the first, larger geography.
    """

    if geo_cell == None:
        # Continuous perimeter
        return _continuous_perimeter(geo)
    else:
        return _discrete_perimeter(geo, geo_cell)

def area(geo, geo_cell = None, convex_hull = False):
    """
    Return areas of geometries in GeoSeries as Series of floats.
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
        convex_hull -- Calculate area of convex hull of geo
        
    This function calculates continuous or area. 
    
    Continuous (Euclidean) area is calculated if only geo argument is 
    provided. Currently this function just returns GeoSeries.area. 
    Future improvements could include:
        
        * Checking for lat-long coordinate system and performing geodetic
        measurement
        * Determining appropriate local CRS (most likely a State Plane or UTM
        zone) and performing calculation in that CRS.
        
    NOT YET OPERATIONALIZED: Discrete area is calculated if a second
    geographic argument is provided that represents the "cells" or "building 
    blocks" of the first, larger geography.
    """

    if geo_cell == None:
        # Continuous area
        if convex_hull:
            return _continuous_area(geo.convex_hull)
        else:        
            return _continuous_area(geo)
    else:
        return _discrete_area(geo)
    
def polsby_popper(geo, geo_cell = None):
    """
    Returns Polsby-Popper (1991) compactness of geo as float
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
    """
    
    return 4 * math.pi * area(geo, geo_cell) / (perimeter(geo, geo_cell) ** 2)

def schwartzberg(geo, geo_cell = None):
    """
    Returns Schwartzberg (1965) compactness of geo as float
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
        geo_cell -- GeoSeries or GeoDataFrame representing units used to build
            geo (the "container"); does not have to nest cleanly
    """

    return polsby_popper(geo, geo_cell) ** -0.5

def c_hull_ratio(geo):
    
    return area(geo) / area(geo, convex_hull = True)

def reock(geo):
    """
    Returns Reock (1961) compactness of geo as float
    
    Keyword arguments:
        geo -- GeoSeries or GeoDataFrame
    """
    
    mbc_area = geo.convex_hull.apply(lambda x: math.pi * make_circle(list(x.exterior.coords))[2] ** 2)
    return geo.area / mbc_area

