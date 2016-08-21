# Edenglen
Visualization of property boundaries in Google Maps

#Workflow

1. Create a text file where each row defines a vertex of the polgon surrounding the road closure
2. Run `auto_detect_boundary.py` to
  * write the bounding polygon to a .js file
  * get all properties in or near the boundary using images saved through the google maps api and some image processing
  * snap corners that are close to each other to the same coordinates
  * query the google maps api at the center of each property to get its address
  * remove propoerties that are outside the bounding polygon
3. create a csv with columns street,number,contributor,message,fill_color that will be attached to each property
4. run `gen_js_data.py` that combines the propoerty polygons with their fill colors and messages

# Privacy
Not all the data files are committed since there could be private information about individual residents.
