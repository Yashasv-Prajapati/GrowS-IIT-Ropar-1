import cv2
import numpy as np

# This function gives the volume of the box using Depth Sensor
# This is the code that will be used to present and calculate the volume to solve GrowSimple problem
# Here img is the colored image with green background, h is the height using depth sensor


def get_volume(img, depth=430, box_height=470, ppm=6.25):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    a_channel = lab[:, :, 1]
    # Here we convert the green background to threshhold
    th = cv2.threshold(a_channel, 127, 255,
                       cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    th = 255-th  # Here we inverse the binary image
    # cv2.imshow("plis",th)
    # We write the lab formatted image in jpeg to read it later
    cv2.imwrite("output.jpeg", th)
    # We read the jpeg formatted image to further image preprocess
    img = cv2.imread("output.jpeg")
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Applying Gaussian Blur to remove unneccessary noise like non uniformity at the edges of the object
    img1 = cv2.GaussianBlur(img1, (5, 5), 0)
    # Threshold on the blur image to find the contours
    ret, thresh = cv2.threshold(img1, 100, 255, 0)
    # Finding the contours in the binary image to find the object
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    # Forming the minimum area rectangle around the object
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # This will draw the minimum bounding box of the object of interest
    img = cv2.drawContours(img, [box], 0, (0, 255, 255), 2)
    # cv2.imshow("Bounding Rectangles", img[::2, ::2])
    # Getting the minimum area box length in pixels
    l = np.linalg.norm(box[0]-box[1])
    # Getting the minimum area box breadth in pixels
    b = np.linalg.norm(box[1]-box[2])
    h = box_height - depth  # We get the height of the object by subtracting the height of box and the distance of object from the top of box which we find using Ultrasound Depth Sensor
    l_adjusted = (l/ppm) * (depth/box_height)  # Converting the length into mm
    b_adjusted = (b/ppm) * (depth/box_height)  # Converting the breadth into mm
    # Print the adjusted length and breadth of the object
    print("length", l_adjusted)
    print("bredth", b_adjusted)
    print("height",h)
    # adding a factor of 10 mm to cater to the errors as well as add a small margin for efficient packaging
    l_adjusted = l_adjusted+10
    # adding a factor of 10 mm to cater to the errors as well as add a small margin for efficient packaging
    b_adjusted = b_adjusted+10
    h = h+5  # adding a factor of 5 mm to cater to the errors as well as add a small margin for efficient packaging. Errors due to sensor is max 0.9 cm, 0.5cm was calculated based on the samples
    ans = (l_adjusted)*(b_adjusted)*(h)
    ans = int(ans)
    ans /= 1000
    return round(ans)

# This function gives us the volume if we have two photos shot from perpendicular field of view
# This function is the implementation of the shadow method that was originally proposed in the mid evaluation


img = cv2.imread("images/IMG_0763.jpg")  # image input
asd = get_volume(img)
print("Volume = ", asd)
