import cv2
import numpy as np
import get_corners
import matplotlib.path as mplPath
import urllib2


def get_property_contours(img_color):
    """
    """
    
    img_color = img_color[:-50, :, :] # remove the google text at the bottom
    img = cv2.cvtColor(img_color,cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img,(5,5),0)
    diff = img-img_blur
    kernel = np.ones((3,3),np.uint8)
    dilation = cv2.dilate(diff,kernel,iterations = 1)
    dilation = cv2.erode(dilation,kernel,iterations = 1)
    #cv2.imshow("dilation", dilation)
    
    ret,thresh = cv2.threshold(dilation,127,255,0)
    (im2, contours, hierarchy) = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #cv2.imshow("diff", diff)
    
    # remove short contours and contours that do not have a big enough area.
    min_perimeter = 100
    min_area = 1
    max_area = 400000
    min_area_perimeter = 20 # acts as a size constraint as well as somewhat of a shape constraint
    
    contours_keep = []
    centroids = []
    contours_with_child = []
    for (i, cnt) in enumerate(contours):
        if hierarchy[0][i][2]==-1:
            perimeter = cv2.arcLength(cnt,True)
            M = cv2.moments(cnt)
            area = cv2.contourArea(cnt)
            #print(str(i) + ":  " + str(perimeter) + "  " + str(M['m01'])+ "  " + str(M['m10']))
            if perimeter>min_perimeter:
                if area>min_area and area<max_area and (area/perimeter)>min_area_perimeter:
                    epsilon = 0.005*perimeter
                    approx = cv2.approxPolyDP(cnt,epsilon,True)
                    contours_keep.append(approx)
                    centroids.append([M['m10']/M['m00'], M['m01']/M['m00']])
                    #print(area/perimeter)
        else:
            perimeter = cv2.arcLength(cnt,True)
            if perimeter>min_perimeter: 
                contours_with_child.append(cnt)
    
    #cnt = contours[13]
    #M = cv2.moments(cnt)
    
    """
    for cnt in contours:
        img_copy = img.copy()
        img_new = cv2.drawContours(img_copy, [cnt], -1, (0,255,0), 1)
        cv2.imshow("boundaries", img_new)
        key = cv2.waitKey()
        if key==27:
            break
    """
    #cv2.drawContours(img_color, contours_with_child, -1, (0,0,255), 2)
    #
    return (contours_keep, centroids)
    
def property_coords(filename, center, width_deg, height_deg, 
                    mapWidth, mapHeight, existing_properties, 
                    all_lines):
    """
    """    
    new_properties = np.zeros((0,2))
    img_color = cv2.imread(filename)
    (contours_keep, centroids) = get_property_contours(img_color)
    # Get the distance to the properties already found
    centroids = np.array(centroids)
    lat_mult = 1000*2*6371*np.pi/360
    lng_mult = lat_mult * np.cos(np.pi * 26/180.0)
    keep_list = []

    # Convert pixel postions to lat and long, check if the the properties already exist
    for (cnt_iter, centroid_iter) in zip(contours_keep, centroids):
        cnt = cnt_iter[:,0,:]/2.0        
        x_deg = center[1] + width_deg * (centroid_iter[0]/2 - mapWidth/2)/mapWidth
        y_deg = center[0] - height_deg * (centroid_iter[1]/2 - mapHeight/2)/mapHeight        
        
        if len(existing_properties)>0:
            dx = lat_mult * (y_deg - existing_properties[:,0])
            dy = lng_mult * (x_deg - existing_properties[:,1])
            dist = np.sqrt(dx*dx + dy*dy)
            keep = np.min(dist) > 2
        else:
            keep = True

        keep_list.append(keep)
            
        if keep:
            new_properties = np.vstack((new_properties, [y_deg, x_deg]))
            all_lines.append("99 Nowhere Rd, Edenvale, 1613, South Africa")            
            #print(all_lines[-1])            
            all_lines.append("[" + str(y_deg) + ", " + str(x_deg) + "]")
            #print(all_lines[-1])
            for (x, y) in cnt:
                x_deg = center[1] + width_deg * (x - mapWidth/2)/mapWidth
                y_deg = center[0] - height_deg * (y - mapHeight/2)/mapHeight
                all_lines.append("(" + str(y_deg) + ", " + str(x_deg) + ")")
                #print(all_lines[-1])
#        else:
#            print("***DUPLICATE***")            
            
        
    #==============================================================================
    # Show the properties and centers
    #==============================================================================
    
#    for (cnt, cent, keep) in zip(contours_keep, centroids, keep_list):
#        color = tuple(np.random.uniform(0, 255, 3).astype('int'))
#        cv2.drawContours(img_color, [cnt], 0, color, 3)
#        if keep:
#            cv2.circle(img_color, (int(cent[0]), int(cent[1])), 4, color, -1)
#        else:
#            cv2.rectangle(img_color, (int(cent[0])-5, int(cent[1])-5), (int(cent[0])+2, int(cent[1])+2), color, thickness=-1)
#    cv2.imshow("boundaries", img_color)
#    cv2.waitKey()
      
    return new_properties
            
    
def get_esrc_poly():
    """ Get the coordinates of the polygon that decribes the border of the ESRC
    """
    f = open("ESRC polygon.txt", 'r')    
    all_lines = f.readlines()
    f.close()
    esrc_poly = []
    for line in all_lines:
        if len(line)>0:
            parts = line.split(',')
            esrc_poly.append([float(parts[0]), float(parts[1])])
            
    return esrc_poly
    
    
def save_image(filename, center):
    """ Save a google static map
    """
    lat = center[0]
    lng = center[1]
    
    STATIC_BASE_URL = "https://maps.googleapis.com/maps/api/staticmap"
    api_key = "AIzaSyDrkpShIXDSUW9H4r2EhU62KmEVsloMYS4"
    imageurl = (STATIC_BASE_URL + "?" + 
                "center=" + str(lat) + "," + str(lng) + "&" + 
                "zoom=18&size=640x480&scale=2&style=feature:poi|element:labels|visibility:off&style=feature:road|element:labels|visibility:off"
                "&key=" + api_key)
                            
    response = urllib2.urlopen(imageurl)
    f = open(filename, "wb")
    f.write(response.read())
    f.close()   
    

# Get the ESRC polygon
esrc_poly = get_esrc_poly()
bbPath = mplPath.Path(esrc_poly)
# get a bounding rectangle
zoom = 18
mapWidth = 640
mapHeight = 480
top_left = [np.max(esrc_poly, axis=0)[0], np.min(esrc_poly, axis=0)[1]]
centerPoint = get_corners.G_LatLng(*top_left)
corners = get_corners.getCorners(centerPoint, zoom, mapWidth, mapHeight)
width_deg = corners['E'] - corners['W']
height_deg = corners['N'] - corners['S']
top_left[0] += height_deg/2  
top_left[1] -= width_deg/2

n_rows = np.ceil(0.5 + 2*(np.max(esrc_poly, axis=0)[0] - np.min(esrc_poly, axis=0)[0]) / height_deg)
n_cols = np.ceil(0.5 + 2*(np.max(esrc_poly, axis=0)[1] - np.min(esrc_poly, axis=0)[1]) / width_deg)

existing_properties =  np.zeros((0,2))
all_lines = []
for i in range(int(n_rows)):#range(3,4):
    for j in range(int(n_cols)):#range(3,5):
        center = [top_left[0] - i*height_deg/2, top_left[1] + j*width_deg/2]
        interior = bbPath.contains_point(center)
        if interior:
            filename = "C:\Dev\Edenglen\images\map_" + str(i).zfill(2) + "_" + str(j).zfill(2) + ".png"
            print(str(i) + ", " + str(j))
            #save_image(filename, center)            
            new_properties = property_coords(filename, center, width_deg, height_deg, mapWidth, mapHeight, existing_properties, all_lines)            
            existing_properties = np.vstack((existing_properties, new_properties))
            
f = open("C:\Dev\Edenglen\data_esrc\unique_no_addr.txt", 'w')
all_lines = [line + '\n' for line in all_lines]
f.writelines(all_lines)
f.close()

            
