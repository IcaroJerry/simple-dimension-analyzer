import sys
sys.path.append("./analyser/")

from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
from parameters.config import server

def _midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def _calc_image_size(imagePath, distance, pictureWidth):

	
	densidadeHorizontal= 831.7-3.702*distance+0.005146*distance**2
	densidadeVertical= 460.4-2.053*distance+0.002865*distance**2

	print('densidade: ' + str(densidadeHorizontal))
	print('densidade: ' + str(densidadeVertical))
	print('distancia: ' + str(distance))

	image = cv2.imread(imagePath)

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
	gray = cv2.cvtColor(gray, cv2.COLOR_BGR2RGBA )
	#gray = cv2.cvtColor(gray, cv2.COLOR_RGBA2BGR )
	#gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (7, 7), 0)

	# perform edge detection, then perform a dilation + erosion to
	# close gaps in between object edges
	edged = cv2.Canny(gray, 50, 100)
	edged = cv2.dilate(edged, None, iterations=1)
	edged = cv2.erode(edged, None, iterations=1)

	# find contours in the edge map
	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	# sort the contours from left-to-right and initialize the
	# 'pixels per metric' calibration variable
	(cnts, _) = contours.sort_contours(cnts)
	pixelsPerMetric = None

	# loop over the contours individually
	for c in cnts:
		# if the contour is not sufficiently large, ignore it
		if cv2.contourArea(c) < 100:
			continue

		# compute the rotated bounding box of the contour
		orig = image.copy()
		box = cv2.minAreaRect(c)
		box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
		box = np.array(box, dtype="int")

		# order the points in the contour such that they appear
		# in top-left, top-right, bottom-right, and bottom-left
		# order, then draw the outline of the rotated bounding
		# box
		box = perspective.order_points(box)
		cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

		# loop over the original points and draw them
		for (x, y) in box:
			cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

		# unpack the ordered bounding box, then compute the midpoint
		# between the top-left and top-right coordinates, followed by
		# the midpoint between bottom-left and bottom-right coordinates
		(tl, tr, br, bl) = box
		(tltrX, tltrY) = _midpoint(tl, tr)
		(blbrX, blbrY) = _midpoint(bl, br)

		# compute the midpoint between the top-left and top-right points,
		# followed by the midpoint between the top-righ and bottom-right
		(tlblX, tlblY) = _midpoint(tl, bl)
		(trbrX, trbrY) = _midpoint(tr, br)

		print("tl: " + str(tl))
		print("tr: " + str(tr))
		print("br: " + str(br))
		print("bl: " + str(bl))
		print("tltrX: " + str(tltrX))
		print("tltrY: " + str(tltrY))
		print("blbrX: " + str(blbrX))
		print("blbrY: " + str(blbrY))
		print("tlblX: " + str(tlblX))
		print("tlblY: " + str(tlblY))
		print("trbrX: " + str(trbrX))
		print("trbrY: " + str(trbrY))
		
		# draw the midpoints on the image
		
		cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

		# draw lines between the midpoints
		cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
			(255, 0, 255), 2)
		cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
			(255, 0, 255), 2)

		# compute the Euclidean distance between the midpoints
		dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
		dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

		print("dA: " + str(dA))
		print("dB: " + str(dB))
		

		# compute the size of the object
		
		#dimA = dA / (densidade / 2.54)
		dimA = (dA/(densidadeVertical)/25.4)*48
		dimB = (dB/(densidadeHorizontal)/25.4)*88

		print("dimA: " + str(dimA))
		print("dimB: " + str(dimB))

		# draw the object sizes on the image
		cv2.putText(orig, "{:.1f}in".format(dimA),
			(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (255, 255, 255), 2)
		cv2.putText(orig, "{:.1f}in".format(dimB),
			(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (255, 255, 255), 2)

		# show the output im age
		cv2.imshow("Image", orig)
		cv2.waitKey(0)


if __name__ == '__main__':
	distanceCam = 345.0
	picturePath = './analyser/client/img/345.jpg'

	_calc_image_size(picturePath, distanceCam, 1.0)
