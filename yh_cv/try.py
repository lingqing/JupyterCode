import cv2
import numpy as np
import sys
import copy


def estimating_atmospheric_light(image, dark_channel):
    i = dark_channel.shape
    num_sum = dark_channel.shape[0] * dark_channel.shape[1]
    print("image has " + str(num_sum) + " points")
    num = int(num_sum * 0.001)
    print("0.1% has " + str(num) + " points")

    pixels = []  # 储存全部的像素值
    for i in range(dark_channel.shape[0]):
        for j in range(dark_channel.shape[1]):
            pixels.append(dark_channel[i][j])

    pixels_sorted_id = sorted(range(len(pixels)), key=lambda k: pixels[k])  # 像素值排序，储存升序后的id
    # pixels_sorted = sorted(pixels)
    # print(pixels_sorted)

    value_threshold = pixels[pixels_sorted_id[len(pixels)-num]]
    print("dark channel value >= " + str(value_threshold) + " belong 0.1%")

    max_value = 0
    r = 0
    c = 0
    for i in range(dark_channel.shape[0]):
        for j in range(dark_channel.shape[1]):
            if dark_channel[i][j] > value_threshold:
                value = int(image[i][j][0]) + int(image[i][j][1]) + int(image[i][j][2])
                if value > max_value:
                    max_value = value
                    r = i
                    c = j

    return r, c


def dark_channel(img, size=15):
    r, g, b = cv2.split(img)
    min_img = cv2.min(r, cv2.min(g, b))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    dc_img = cv2.erode(min_img, kernel)

    return dc_img


def guidedFilter(p, i, r, e):
    # 1
    mean_I = cv2.boxFilter(i, cv2.CV_64F, (r, r))
    mean_p = cv2.boxFilter(p, cv2.CV_64F, (r, r))
    corr_I = cv2.boxFilter(i * i, cv2.CV_64F, (r, r))
    corr_Ip = cv2.boxFilter(i * p, cv2.CV_64F, (r, r))
    # 2
    var_I = corr_I - mean_I * mean_I
    cov_Ip = corr_Ip - mean_I * mean_p
    # 3
    a = cov_Ip / (var_I + e)
    b = mean_p - a * mean_I
    # 4
    mean_a = cv2.boxFilter(a, cv2.CV_64F, (r, r))
    mean_b = cv2.boxFilter(b, cv2.CV_64F, (r, r))
    # 5
    q = mean_a * i + mean_b
    return q


def dehaze(image):
    dark_prior = dark_channel(image)

    print(dark_prior.shape)
    a_row, a_col = estimating_atmospheric_light(image, dark_prior)
    cv2.imshow("dark channel of origin", dark_prior)

    A = image[a_row][a_col]
    print("A at: [" + str(a_row) + ", " + str(a_col) + "], value: " + str(A))

    t = image / A
    t_min = dark_channel(t)

    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype('float64') / 255
    # t_min = guidedFilter(t_min, img_gray, 225, 0.0001)
    cv2.imshow("transmission", t_min)

    t_x = [[0 for i in range(t_min.shape[1])] for i in range(t_min.shape[0])]
    for i in range(t_min.shape[0]):
        for j in range(t_min.shape[1]):
            t_x[i][j] = 1 - 0.95 * t_min[i][j]

    image_noHaze = copy.copy(image)
    for i in range(image_noHaze.shape[0]):
        for j in range(image_noHaze.shape[1]):
            # image_noHaze[i][j][0] = (image[i][j][0] - A[0]) / max(0.1, t_x[i][j]) + A[0]
            # image_noHaze[i][j][0] = max(min(image_noHaze[i][j][0], 255), 0)
            # image_noHaze[i][j][1] = (image[i][j][1] - A[1]) / max(0.1, t_x[i][j]) + A[1]
            # image_noHaze[i][j][1] = max(min(image_noHaze[i][j][1], 255), 0)
            # image_noHaze[i][j][2] = (image[i][j][2] - A[2]) / max(0.1, t_x[i][j]) + A[2]
            # image_noHaze[i][j][2] = max(min(image_noHaze[i][j][2], 255), 0)
            # if t_x[i][j] > 0.1:
            image_noHaze[i][j][0] = max(min((int(image[i][j][0]) - int(A[0])) / max(0.1, t_x[i][j]) + int(A[0]), 255), 0)
            image_noHaze[i][j][1] = max(min((int(image[i][j][1]) - int(A[1])) / max(0.1, t_x[i][j]) + int(A[1]), 255), 0)
            image_noHaze[i][j][2] = max(min((int(image[i][j][2]) - int(A[2])) / max(0.1, t_x[i][j]) + int(A[2]), 255), 0)

    image_noHaze = np.uint8(image_noHaze)

    return image_noHaze, a_row, a_col


if __name__ == '__main__':
    image_origin = cv2.imread('data/R-C2.jpeg')
    # image_origin = cv2.resize(image_origin, (600, 600*image_origin.shape[0]//image_origin.shape[1]))[:,:,[2,1,0]]
    image_origin = cv2.resize(image_origin, (600, 600*image_origin.shape[0]//image_origin.shape[1]))
    print("origin image shape: " + str(image_origin.shape))
    result, row, col = dehaze(image_origin)

    u = col
    v = row
    cv2.circle(image_origin, (u, v), 10, (255, 0, 0), 1)
    cv2.imshow("origin", image_origin)
    cv2.imshow("result", result)
    cv2.imwrite('defog.jpg', result)

    while True:
        k = cv2.waitKey(1)
        if k == 27:  # esc键
            break
    sys.exit(0)



