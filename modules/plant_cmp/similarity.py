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
    height, width,channel = image.shape
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

def extractImage(imagePath):
    image = ResizeImage(cv2.imread(imagePath, 0))
    keypoint, descriptor = sift.detectAndCompute(image, None)
    return keypoint, descriptor


def calculateSimilarityRaw(imagePath1, imagePath2):
    '''
    @params: 图像文件路径
    @return: 相似度 > 1 可认定为同一株植物
    '''
    keypoint1, descriptor1 = extractImage(imagePath1)
    keypoint2, descriptor2 = extractImage(imagePath2)

    matches = match(descriptor1, descriptor2)
    return 500 * (len(matches) / min(len(keypoint1), len(keypoint2)))

def calculateSimilarity(cv2img1, cv2img2):
    '''
    @params: 图像
    @return: 相似度 > 1 可认定为同一株植物
    '''
    keypoint1, descriptor1 = sift.detectAndCompute(ResizeImage(cv2img1), None)
    keypoint2, descriptor2 = sift.detectAndCompute(ResizeImage(cv2img2), None)

    matches = match(descriptor1, descriptor2)
    return 500 * (len(matches) / min(len(keypoint1), len(keypoint2)))