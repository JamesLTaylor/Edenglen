import cv2
import numpy as np

img = cv2.imread("capture_big.PNG")
img_blur = cv2.GaussianBlur(img,(5,5),0)
diff = img-img_blur
diff = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(diff,127,255,0)
(im2, contours, hierarchy) = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.imshow("diff", diff)

# remove short contours and contours that do not have a big enough area.
contours_keep = []
for (i, cnt) in enumerate(contours):
    if hierarchy[i][2]==-1:
        perimeter = cv2.arcLength(cnt,True)
        M = cv2.moments(cnt)
        area = cv2.contourArea(cnt)
        #print(str(i) + ":  " + str(perimeter) + "  " + str(M['m01'])+ "  " + str(M['m10']))
        if perimeter>100 and M['m01']>500 and M['m10']>500:
            if M['m01']/M['m10'] < 5 and M['m10']/M['m01']<5:
                if area>1000 and area<40000 and area/perimeter>5:
                    contours_keep.append(cnt)
                    print(area/perimeter)

#cnt = contours[13]
#M = cv2.moments(cnt)

for cnt in contours_keep:
    img_copy = img.copy()
    img_new = cv2.drawContours(img_copy, [cnt], -1, (0,255,0), 1)
    cv2.imshow("boundaries", img_new)
    key = cv2.waitKey()
    if key==27:
        break

