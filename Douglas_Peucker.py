
#         --Douglas-Peucker Algorithm--
#
# Program by: Hannes Ziegler
# Date: 12/1/2013 (updated 3/24/2019)
#
# --Description--
# The Douglas-Puecker algorithm takes as input a set of
# x and y coordinates and reduces the number of vertices
# within the given set of points.
#
#-------------------------------------------------------

# -- Import Libraries -- #

import os, math, arcpy

# Set arcpy environment settings

arcpy.env.overwriteOutput = True

# -- Function Definitions -- #

class Line:

    def __init__(self, point_a, point_b):
        self._xa = float(point_a[0])
        self._ya = float(point_a[1])
        self._xb = float(point_b[0])
        self._yb = float(point_b[1])

    def __repr__(self):
        return 'Line ({!r}, {!r}), ({!r}, {!r})'.format(self._xa, self._ya, self._xb, self._yb)

    def slope(self): # Returns m (slope) of two points (xa, ya) and (xb, yb).
        return (self._ya- self._yb)/(self._xa- self._xb)

    def distance(self): # Returns d (distance) between two points (xa, ya) and (xb, yb).
        return math.hypot(self._xa - self._xb, self._ya - self._yb)

    def y_intercept(self): # Returns b (y-intercept) of a line with slope m and point (x, y).
        return self._ya - (self.slope()*self._xa)

    def slope_reciprocal(self): # Returns the reciprocal of slope, the slope of a line perpendicular to this line.
        return -1/self.slope()

    def intersect(self, other): #Returns the point where a second line (given as other) intersects this line (given as self)
        self_b, other_b, self_m, other_m = self.y_intercept(), other.y_intercept(), self.slope(), other.slope()
        point_x = (other_b - self_b) / (self_m - other_m)
        point_y = (other_m * point_x) + other_b
        return [point_x, point_y]

    def line_of_perp_offset(self, offset_point):
        self_b, self_m, perp_m = self.y_intercept(), self.slope(), self.slope_reciprocal()
        perp_b = offset_point[1] - (perp_m * offset_point[0])
        intersect_x = (perp_b - self_b) / (self_m - perp_m)
        intersect_y = (perp_m * intersect_x) + perp_b
        intersect_point = [intersect_x, intersect_y]
        return Line(offset_point, intersect_point)


# perpendicular_distances(point_list): Selects the first and last point on the line as key points,
#                                    finds the perpendicular distances of all points inbetween
#                                    the key points to the line created by the key points,
#                                    and returns the largest perpendicular distance as well as the
#                                    index of the point to which that largest perpendicular distance
#                                    corresponds in the original list. point_list must contain at
#                                    least three points.
def perpendicular_distances(point_list):
    #Create Line object from first and last point in point_list.
    trunk = Line(point_list[0], point_list[-1])
    #Create a list of perpendicular distances to trunk line from all points between first and last points in point list
    return [trunk.line_of_perp_offset(offset_point).distance() for offset_point in point_list[1:-1]]

def enumerate_max(values):
    max_val = max(values)
    i = values.index(max_val)
    return i, max_val

# Douglas_Peucker_Algorithm(point_list, tolerance): Implements the Douglas-Puecker Algorithm to reduce the number of vertices
#                                                  in a set of points.
def douglas_peucker_algorithm(point_list, tolerance):
    point_list_copy = [point_list]
    x = 0
    while x < len(point_list_copy): #Enter a while loop to iterate over the recursively expanding list of split and reduced lines.
        if len(point_list_copy[x]) <= 2: #When a line has been reduced to two points, skip over it and move on to the next line.
            pass
        else: #Otherwise ->
            perp_distances = perpendicular_distances(point_list_copy[x]) #find the perpendicular distances of all points between the first and last point.
            i, largest = enumerate_max(perp_distances) #find the largest vertical distance and note it's index in the list.
            i+=1
            if largest >= float(tolerance): #If the largest distance is longer than the tolerance, split the line at the noted index of largest perpendicular distance.
                point_list_copy.insert(x+1, point_list_copy[x][i:])
                point_list_copy.insert(x+1, point_list_copy[x][:i+1])
                point_list_copy.remove(point_list_copy[x]) # remove the initial list and (previous two statements) add the two split lines in its place.
                x-=1
            else: #If the largest distance is shorter than the tolerance, remove all the points inbetween the first and last points.
                point_list_copy.insert(x+1, [point_list_copy[x][0], point_list_copy[x][-1]])
                point_list_copy.remove(point_list_copy[x]) #remove the initial list and place the shortened list in its places.
        x+=1

    point_list = point_list_copy[0] #Re-format the raw list of points returned by the previous operation into the actual remaining points.
    for item in point_list_copy[1:]:
        point_list.append(item[-1])
    return point_list

# -- Begin Main Body -- #

infc = arcpy.GetParameterAsText(0) #input featureclass (must be a polyline)
infc_path = arcpy.Describe(infc).catalogPath
outpath = arcpy.GetParameterAsText(1) #output featureclass
outdir, outname = os.path.split(outpath)
tolerance = float(arcpy.GetParameterAsText(2)) #set the tolerance which is used to determine how much noise is removed from the line.
outfc = arcpy.management.CreateFeatureclass(outdir, outname) #create output featureclass
arcpy.management.Copy(infc_path, outfc, "Datasets") #copy output features
#arcpy.AddMessage("Tolerance: " + str(tolerance)) ##DEBUG##

with arcpy.da.UpdateCursor(outfc, "SHAPE@") as cursor:
    for row in cursor:
        for part in row[0]:
            line = [[point.X, point.Y] for point in part]
            line = douglas_peucker_algorithm(line, tolerance)
            array = arcpy.Array()
            for xy in line:
                array.append(arcpy.Point(xy[0], xy[1]))
            polyline = arcpy.Polyline(array)
            row[0] = polyline
            cursor.updateRow(row)



