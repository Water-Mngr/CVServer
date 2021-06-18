'''
Copyrights: ©2021 @Laffery
Date: 2021-05-09 15:14:35
LastEditor: Laffery
LastEditTime: 2021-06-18 22:26:27
'''
import cv2

sift = cv2.SIFT_create()
bf = cv2.BFMatcher_create()

def ResizeImage(image):
    height, width = image.shape
    ratio = width / height
    maxSize = 1024
    if (ratio > 1):
        newSize = (maxSize, (int)(maxSize * ratio))
    else:
        newSize = ((int)(maxSize * ratio), maxSize)
    image = cv2.resize(image, newSize)
    return image

def ResizeColoredImage(image):
    height, width, channel = image.shape
    ratio = width / height
    maxSize = 1024
    if (ratio > 1):
        newSize = (maxSize, (int)(maxSize * ratio))
    else:
        newSize = ((int)(maxSize * ratio), maxSize)
    image = cv2.resize(image, newSize)
    return image

def match(des1, des2):
    matches1 = bf.knnMatch(des1, des2, k=2)
    matches2 = bf.knnMatch(des2, des1, k=2)
    result1 = []
    result2 = []
    for m, n in matches1:
        if m.distance < 0.7 * n.distance:
            result1.append([m])
    for m, n in matches2:
        if m.distance < 0.7 * n.distance:
            result2.append([m])

    result = []
    for match1 in result1:
        for match2 in result2:
            if (match1[0].queryIdx == match2[0].trainIdx) and (match2[0].queryIdx == match1[0].trainIdx):
                result.append(match1)

    return result

def extractImage(image):
    image = ResizeColoredImage(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    keypoint, descriptor = sift.detectAndCompute(gray, None)
    return keypoint, descriptor

def compare(img1, img2, ind1, ind2):
    bias = 0.2 if len(set(ind1) & set(ind2)) > 0 else -1
    keypoint1, descriptor1 = extractImage(img2)
    keypoint2, descriptor2 = extractImage(img1)
    matches = match(descriptor1, descriptor2)
    score = 600 * (len(matches) / max(len(keypoint1), len(keypoint2)))
    return score + bias > 1
