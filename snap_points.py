import numpy as np

fname = "polygondata1" # excluding the extension, assumed to be .txt

f = open(fname + ".txt", 'r')
all_lines = f.readlines()
f.close()

done = []
vals = []

for (i, line) in enumerate(all_lines):
    if line[0]=='(':
        [lat, lng] = line.split(',',1)
        lat = float(lat[1:12])
        lng = float(lng[1:12])
        vals.append([lat, lng])
        done.append(False)
        
        
    else:
        vals.append([0,0])
        done.append(True)
        
        
vals = np.array(vals)
done = np.array(done)   

lat_mult = 1000*2*6371*np.pi/360
lng_mult = lat_mult * np.cos(np.pi * 26/180.0)  

L = len(done)
for i in range(0, L):
    if (not done[i]):
        ind = np.logical_not(done)        
        dx = 1000*np.ones((L,))
        dx[ind] = lat_mult * (vals[ind, 0] - vals[i,0])
        dy = 1000*np.ones((L,))
        dy[ind] = lng_mult*(vals[ind, 1] - vals[i,1])
        dist = np.sqrt(dx*dx + dy*dy)
    
        replace = dist<2.0
        print(np.where(replace))
        
        avglat = np.mean(vals[replace, 0])
        avglng = np.mean(vals[replace, 1])
        done[replace] = True
        vals[replace, 0] = avglat
        vals[replace, 1] = avglng
        
        print("replacing latitutude:")
        print(vals[replace, :])
        print("with")
        print((avglat, avglng))
        print()
        
new_lines = []
f = open(fname + "_snapped.txt", 'w')

for (i, line) in enumerate(all_lines):
    if line[0]=='(':
        f.write("(" + "{:.10f}".format(vals[i,0])+ ", " + "{:.10f}".format(vals[i,1]) + ")\n")
    else:
        f.write(line)

f.close()