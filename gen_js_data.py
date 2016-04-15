import numpy as np

def find_address(street, number):
    """
    Args
        street: string
        number: int
        
    Returns:
        (msg, fill_color)

    """
    street_lower = street.translate(None, ' ').lower()
    number_lower = number.translate(None, ' ').lower()
    for row in house_info_tab:
        if (row[0].translate(None, ' ').lower()==street_lower and 
                row[1].translate(None, ' ').lower()==number_lower):
            return (row[3], row[4])
            
    raise Exception(street + " " + str(number) + " not found")            

all_lines = []
#f = open('polygondata1_snapped.txt', 'r')
#new_lines = f.readlines()
#f.close()
#all_lines += new_lines

f = open(r"C:\Dev\Edenglen\data_esrc\final.txt", 'r')
new_lines = f.readlines()
f.close()
all_lines += new_lines

f = open("house_info.csv",'r')
house_info = f.readlines()
f.close()
house_info_tab = [row[:-1].split(',') for row in house_info]
house_info_tab.pop(0)
#for row in house_info_tab:
#    row[1] = int(row[1])



result = list("var polygonData = [\n")
newpoly = False

for (i, line) in enumerate(all_lines):
    if line[0]=='(':        
        [lat, lng] = line.split(',',1)
        lat = lat[1:10]
        lng = lng[1:10]
        
        if (newpoly):
            newpoly = False
            result += list("coords: [")
        
        result += list("[" + lat + ", " + lng + "],\n")
        
    elif line[0]=='[':
        pass        
        
    else:
        if (i>0):
            result[-2] = ']'
            result += list("},\n")
        newpoly = True
        address = line.split(',')[0]        
        (number, street) = address.split(' ',1)
        try:
            (msg, fill_color) = find_address(street, number)
        except:
            color_r = int(np.random.uniform(0, 255))
            color_b = int(np.random.uniform(0, 255))
            fill_color = "#" + hex(color_r)[2:].zfill(2).upper() + "00" + hex(color_b)[2:].zfill(2).upper()
            #fill_color = "#0000FF"
            msg = "No info in data base"
            
        result += list("{address: '" + address + "',\n")
        result += list("msg: '" + msg + "',\n")
        result += list("fill_color: '" + fill_color + "',\n")        
        

        
result[-2] = ']'
result[-1] = '}'
result += [']',';']

ss = "".join(result)


f = open(r"C:\Dev\Edenglen\getPolygonDataAuto.js", 'w')
f.write(ss)
f.close()
    

    
