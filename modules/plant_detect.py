'''
Copyrights: ©2021 @Laffery
Date: 2021-06-18 22:02:49
LastEditor: Laffery
LastEditTime: 2021-06-20 16:01:50
'''
import cv2
import numpy as np

def image_masking(img):
    CANNY_THRESH_1 = 20
    CANNY_THRESH_2 = 100

    height, width, _ = img.shape
    size = int(min(height, width) / 300)

    edges = cv2.Canny(img, CANNY_THRESH_1, CANNY_THRESH_2)
    edges = cv2.dilate(edges, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=size)
    edges = cv2.erode(edges, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=size)
    contours, __ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    contoursLength = [len(contours[x]) for x in range(len(contours))]
    top_idx = (-1 * np.array(contoursLength)).argsort()

    maxContour = contours[top_idx[0]]
    maxContour2 = contours[top_idx[1]]

    hull = cv2.convexHull(maxContour)
    hull2 = cv2.convexHull(maxContour2)
    contoursImg = img.copy()
    hullImg = img.copy()
    cv2.drawContours(contoursImg, maxContour, -1, (255, 0, 0), size)
    cv2.drawContours(contoursImg, maxContour2, -1, (0, 0, 255), size)

    polymask = np.zeros(img.shape, np.uint8)
    polymask = cv2.polylines(polymask, [hull], True, (255, 255, 255), 2)
    polymask = cv2.fillPoly(polymask.copy(), [hull], (255, 255, 255))

    polymask2 = np.zeros(img.shape, np.uint8)
    polymask2 = cv2.polylines(polymask2, [hull2], True, (255, 255, 255), 2)
    polymask2 = cv2.fillPoly(polymask2.copy(), [hull2], (255, 255, 255))

    shapeRatio = np.count_nonzero(polymask) / np.count_nonzero(polymask2)

    maskImg = cv2.copyTo(img, polymask)
    return maskImg, shapeRatio


def color_masking(img, thresh_low=20, thresh_high=60):
    height, width, _ = img.shape
    size = int(min(height, width) / 300)

    hlsImg = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    hueImg = hlsImg[:, :, 0]

    _, lowThresh = cv2.threshold(hueImg, thresh_low, 255, cv2.THRESH_BINARY_INV)
    _, highThresh = cv2.threshold(hueImg, thresh_high, 255, cv2.THRESH_BINARY_INV)

    return cv2.copyTo(img, lowThresh - highThresh)


def normalLevel(img):
    maskImg, shapeRatio = image_masking(img)
    result = color_masking(maskImg, 30, 60)
    yellowresult = color_masking(maskImg, 0, 30)

    greenRatio = np.count_nonzero(result) / np.count_nonzero(maskImg)
    yellowRatio = np.count_nonzero(yellowresult) / np.count_nonzero(maskImg)

    colorNormalLevel = 0
    shapeNormalLevel = 0

    if greenRatio > 2 * yellowRatio:
        colorNormalLevel = 2
    elif greenRatio < yellowRatio:
        colorNormalLevel = 0
    else:
        colorNormalLevel = 1

    if shapeRatio > 3:
        shapeNormalLevel = 1
    else:
        shapeNormalLevel = 0

    return colorNormalLevel, shapeNormalLevel


def detect(filepath):
    '''
    @return:
    colorNorm: 2为好，1为一般，0为差
    shapeNorm: 1为好，0为差
    '''
    img = cv2.imread(filepath)
    colorNorm, shapeNorm = normalLevel(img)
    
    return colorNorm, shapeNorm