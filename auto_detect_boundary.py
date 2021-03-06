import get_corners
import snap_points

import cv2
import numpy as np
import matplotlib.path as mplPath
import urllib2
import json


def get_points_near_line(x0, x1, m, c, img, dist):
    """
    """
    points = []
    for x in range(x0, x1+1):
        y = m * x + c 
        for i in range(-dist, dist+1):
            shifted_y = int(y)+i
            if shifted_y>=0 and shifted_y<img.shape[0] and img[shifted_y, x]>0:
                points.append([x, shifted_y])
    return np.array(points)
    
    
def get_best_fit_line_h(p1, p2, img_orig):
    """
    """
    # check if the line is more horizontal or vertical
    
    if abs(p1[0]-p2[0])>abs(p1[1]-p2[1]):        
        horizontal = True
        img = img_orig
        
    else:
        horizontal = False
        p1 = (p1[1], p1[0])
        p2 = (p2[1], p2[0])
        img = img_orig.copy()
        img = np.transpose(img)
        
    if p1[0]>p2[0]:
        p_temp = p1
        p1 = p2
        p2 = p_temp
    m = (float(p2[1])-p1[1])/(p2[0]-p1[0])
    c = p1[1] - m * p1[0]
    
    data = get_points_near_line(p1[0]+7, p2[0]-7, m, c, img, dist=7)
    if len(data) > 30:
        x = np.hstack((data[:,0:1], np.ones((len(data),1))))
        y = data[:,1:]
        m, c = np.linalg.lstsq(x, y)[0]    
        
        data = get_points_near_line(p1[0]+2, p2[0]-2, m, c, img, dist=2)
        
    if len(data) > 30:    
        x = np.hstack((data[:,0:1], np.ones((len(data),1))))
        y = data[:,1:]
        m, c = np.linalg.lstsq(x, y)[0]
        m = m[0]
        c = c[0]
    
    if horizontal:
        return (m,c)
    else:
        if abs(m)<1e-9:
            new_m = np.inf
            new_c = c
        else:
            new_m = 1/m
            new_c = -c/m            
        return (new_m, new_c)
    
    
def refine_contours(cnt, img):
    """
    """
    lines = []
    for i in range(len(cnt)):
        p1 = (cnt[i][0][0],cnt[i][0][1])
        if i > 0:
            p2 = (cnt[i-1][0][0],cnt[i-1][0][1])
        else:
            p2 = (cnt[-1][0][0],cnt[-1][0][1])
            
        (m, c) = get_best_fit_line_h(p1, p2, img)
        lines.append([m, c])
    new_cnt = []    
    for i in range(len(cnt)):    
        m1 = lines[i][0]
        c1 = lines[i][1]
        if i > 0:
            m2 = lines[i-1][0]
            c2 = lines[i-1][1]
        else:
            m2 = lines[-1][0]
            c2 = lines[-1][1]
            
        if m1 == np.inf:
            x = c1
            y = m2*c1 + c2
        elif m2 == np.inf:
            x = c2
            y = m1*c2 + c1
        else:            
            x = (c2-c1)/(m1-m2)
            y = m1 * x + c1
          
        new_cnt.append([[x,y]])
        
    return np.array(new_cnt)


def get_property_contours(img_color):
    """
    """
    
    img_color = img_color[:-50, :, :] # remove the google text at the bottom
    img = cv2.cvtColor(img_color,cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img,(5,5),0)
    diff = img-img_blur
    (ret, diff) = cv2.threshold(diff,127,255,0)
    kernel = np.ones((3,3),np.uint8)
    dilation = cv2.dilate(diff,kernel,iterations = 1)
    dilation = cv2.erode(dilation,kernel,iterations = 1)
#    cv2.imshow("dilation", dilation)
    
    ret,thresh = cv2.threshold(dilation,127,255,0)
    (im2, contours, hierarchy) = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#    cv2.imshow("diff", diff)
    
    # remove short contours and contours that do not have a big enough area.
    min_perimeter = 100
    min_area = 1
    max_area = 400000
    min_area_perimeter = 20 # acts as a size constraint as well as somewhat of a shape constraint
    
    contours_keep = []
    contours_draw = []
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
                    new_approx = refine_contours(approx, diff)
                    contours_keep.append(new_approx)
                    #contours_draw.append(np.round(new_approx).astype(int))
                    centroids.append([M['m10']/M['m00'], M['m01']/M['m00']])
                    #print(area/perimeter)
        else:
            perimeter = cv2.arcLength(cnt,True)
            if perimeter>min_perimeter: 
                contours_with_child.append(cnt)
        
#    img_disp = np.zeros(img_color.shape, dtype='uint8')
#    img_disp[:,:,0] = diff
#    img_disp[:,:,1] = diff
#    img_disp[:,:,2] = diff    
#    cv2.drawContours(img_disp, contours_draw, -1, (0,0,255), 1)
#    cv2.imshow("approx polygons", img_disp)
    
   
    #cnt = contours[13]
    #M = cv2.moments(cnt)
    
    
#    for cnt in contours:
#        img_copy = img.copy()
#        img_new = cv2.drawContours(img_copy, [cnt], -1, (0,255,0), 1)
#        cv2.imshow("boundaries", img_new)
#        key = cv2.waitKey()
#        if key==27:
#            break
    
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
#TODO: At some point x and y are coming through as arrays and writing as ([xx.xxxx], [xx.xxxx])                
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
            
    
def get_bounding_poly(filename):
    """ Get the coordinates of the polygon that decribes the border of the ESRC
    """
    f = open(filename, 'r')    
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
    imageurl = (STATIC_BASE_URL + "?" + 
                "center=" + str(lat) + "," + str(lng) + "&" + 
                "zoom=18&size=640x480&scale=2&style=feature:poi|element:labels|visibility:off&style=feature:road|element:labels|visibility:off"
                "&key=" + api_key)
                            
    response = urllib2.urlopen(imageurl)
    f = open(filename, "wb")
    f.write(response.read())
    f.close()   
    
    
def get_address(lat, lng):
    """ Get the formatted address
    """
    try:
        STATIC_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"    
        url = (STATIC_BASE_URL + "?" + 
                    "latlng=" + str(lat) + "," + str(lng) + 
                    "&result_type=" + "street_address"
                    "&key=" + api_key)
                                
        response = urllib2.urlopen(url)
        result = json.loads(response.read())
        return result['results'][0]['formatted_address']
    except:
        return "99 Nowhere Rd, Edenvale, 1613, South Africa"
    
def write_poly_js(esrc_poly, filename):
    """write the bounding polygon into a javascript file for use in web display
    """
    all_lines = ["var boundingPolygonData = ["]
    for (lat, lng) in esrc_poly:
        all_lines[-1] += "[" + str(lat) + ", " + str(lng) + "],\n"
        all_lines.append("")
        
    all_lines.pop()
    all_lines[-1] = all_lines[-1][:-2] + "]"
    f = open(filename, 'w')
    f.writelines(all_lines)
    f.close() 
    

def remove_props_outside(bounding_poly, file_in, file_out):
    bounding_path = mplPath.Path(bounding_poly)
    f = open(file_in, 'r')
    all_lines = f.readlines()
    f.close()
    interior = False
    new_lines = []
    next_address = []
    for (i, line) in enumerate(all_lines):
        if line[0]!='[' and line[0]!='(':
            if interior:
                new_lines += next_address
            next_address = [line]            
        elif line[0]=='[':
            next_address.append(line)
            [lat, lng] = all_lines[i].split(',',1)
            lat = float(lat.translate(None, ' ()[]'))
            lng = float(lng.translate(None, ' ()[]'))
            interior = bounding_path.contains_point([lat, lng])
            if not interior:
                print("removing: " + next_address[0])
        else:
            next_address.append(line)
            
    f = open(file_out, 'w')
    f.writelines(new_lines)
    f.close() 
            
            
    
def add_addresses(file_in, file_out):
    f = open(file_in, 'r')
    all_lines = f.readlines()
    f.close()

    f = open(file_out, 'w')    
    new_lines = []
    for (i, line) in enumerate(all_lines):
        if len(line)>0 and not line[0]=='(' and not line[0]=='[':
            if line.startswith("99 Nowhere Rd"):
                [lat, lng] = all_lines[i+1].split(',',1)
                lat = float(lat.translate(None, ' ()[]'))
                lng = float(lng.translate(None, ' ()[]'))
                address = get_address(lat, lng)
                print(address)
                new_lines.append(address + "\n")
                f.write(address + "\n")
            else:
                new_lines.append(line)
                f.write(line)
        else:
            new_lines.append(line)
            f.write(line)
            
    #f = open(file_out, 'w')
    #f.writelines(new_lines)
    f.close()            
                
                
def get_properties_in_poly(bounding_poly, save_maps=False):
    """ Writes a file with all the unique locations within or near the boundary of 
    the bounding polygon
    
    Args:
        bounding_poly:
        save_maps: False uses maps already saved, True loads the required maps 
            from google
    """
    bbPath = mplPath.Path(bounding_poly)
    # get a bounding rectangle
    zoom = 18
    mapWidth = 640
    mapHeight = 480
    top_left = [np.max(bounding_poly, axis=0)[0], np.min(bounding_poly, axis=0)[1]]
    centerPoint = get_corners.G_LatLng(*top_left)
    corners = get_corners.getCorners(centerPoint, zoom, mapWidth, mapHeight)
    width_deg = corners['E'] - corners['W']
    height_deg = corners['N'] - corners['S']
    top_left[0] += height_deg/2  
    top_left[1] -= width_deg/2
    
    n_rows = np.ceil(0.5 + 2*(np.max(bounding_poly, axis=0)[0] - np.min(bounding_poly, axis=0)[0]) / height_deg)
    n_cols = np.ceil(0.5 + 2*(np.max(bounding_poly, axis=0)[1] - np.min(bounding_poly, axis=0)[1]) / width_deg)
    
    existing_properties =  np.zeros((0,2))
    all_lines = []
    for i in range(int(n_rows)):#range(int(n_rows)):#range(3,4):
        for j in range(int(n_cols)):#range(int(n_cols)):#range(1,2):            
            print(str(i) + ", " + str(j))
            center = [top_left[0] - i*height_deg/2, top_left[1] + j*width_deg/2]
            interior = bbPath.contains_point(center)
            if interior:
                mapfilename = map_path + "\map_" + str(i).zfill(2) + "_" + str(j).zfill(2) + ".png"
                print(str(i) + ", " + str(j))
                if save_maps:
                    save_image(mapfilename, center)            
                new_properties = property_coords(mapfilename, center, width_deg, height_deg, mapWidth, mapHeight, existing_properties, all_lines)            
                existing_properties = np.vstack((existing_properties, new_properties))
                
    f = open(output_file, 'w')
    all_lines = [line + '\n' for line in all_lines]
    f.writelines(all_lines)
    f.close()
    
    

if __name__ == "__main__":
    #==============================================================================
    # files
    #==============================================================================
    bounding_poly_file = r"C:\Dev\Edenglen\data_esrc\ESRC polygon.txt"
    output_js_poly_file = r"C:\Dev\Edenglen\getBoundingPoly.js"
    map_path = r"C:\Dev\Edenglen\images"
    output_file = r"C:\Dev\Edenglen\data_esrc\unique_no_addr.txt"
    output_file_snapped = r"C:\Dev\Edenglen\data_esrc\unique_no_addr_snapped.txt"
    output_file_with_addr = r"C:\Dev\Edenglen\data_esrc\all_with_addr.txt"
    output_file_with_addr_final = r"C:\Dev\Edenglen\data_esrc\final.txt"
    api_key = "AIzaSyDrkpShIXDSUW9H4r2EhU62KmEVsloMYS4"
    # Get the ESRC polygon
    
    esrc_poly = get_bounding_poly(bounding_poly_file)
    #write_poly_js(esrc_poly, output_js_poly_file)
    #get_properties_in_poly(esrc_poly, save_maps=True)
    #snap_points.in_file(output_file, output_file_snapped)
    add_addresses(output_file_snapped, output_file_with_addr)
    remove_props_outside(esrc_poly, output_file_with_addr, output_file_with_addr_final)

            
