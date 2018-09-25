import sys
sys.path.append('../')

from abc import ABCMeta, abstractmethod
from cv2 import imshow, line, cvtColor, arcLength, blur, approxPolyDP, inRange, COLOR_BGR2HSV, FONT_HERSHEY_SIMPLEX, \
    CHAIN_APPROX_SIMPLE, IMREAD_COLOR, transform, moments, drawContours, getAffineTransform, RETR_EXTERNAL, mean, \
    putText, imdecode, circle, bitwise_or, findContours, waitKey
from math import *
from numpy import asarray, rot90, array, float32, uint8, zeros
from imutils import is_cv2
import requests
from time import sleep

from const import *


def angle_between(v1, v2):
    len1 = sqrt(v1[0] * v1[0] + v1[1] * v1[1])
    len2 = sqrt(v2[0] * v2[0] + v2[1] * v2[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    a = dot / (len1 * len2)
    b = acos(a)
    return b if b < pi / 2 else pi - b


def dist_between(v1, v2):
    v = (v1[0] - v2[0], v1[1] - v2[1])
    return sqrt(v[0] * v[0] + v[1] * v[1])


def center_of(v1, v2, v3):
    return (v1[0] + v2[0] + v3[0]) / 3, (v1[1] + v2[1] + v3[1]) / 3


def get_best_triangle(points, reasonable_perimeter):
    min_err = 9999999999
    corners = []
    for x1 in range(0, len(points)):
        for x2 in range(0, len(points)):
            if x2 == x1:
                continue
            for x3 in range(0, len(points)):
                if x3 == x1 or x3 == x2:
                    continue

                cx = (points[x1][0] + points[x2][0] + points[x3][0]) / 3
                cy = (points[x1][1] + points[x2][1] + points[x3][1]) / 3
                if not pointing_up([points[x1], points[x2], points[x3]], (cx, cy)):
                    print('discard due to direction')
                    continue

                v1 = (points[x1][0] - points[x2][0], points[x1][1] - points[x2][1])
                v2 = (points[x2][0] - points[x3][0], points[x2][1] - points[x3][1])
                v3 = (points[x3][0] - points[x1][0], points[x3][1] - points[x1][1])

                peri = 0
                for v in [v1, v2, v3]:
                    peri += sqrt(v[0]*v[0] + v[1]*v[1])
                if peri < 0.5*reasonable_perimeter or peri > 2*reasonable_perimeter:
                    print('discard due to perimeter ' + str(peri))
                    continue

                a = 180 * angle_between(v1, v2) / pi
                b = 180 * angle_between(v2, v3) / pi
                c = 180 * angle_between(v3, v1) / pi

                err = (a - 60) * (a - 60) + (b - 60) * (b - 60) + (c - 60) * (c - 60)
                if err < min_err:
                    min_err = err
                    corners = [points[x1], points[x2], points[x3]]
    if len(corners) != 3:
        print('No triangle candidates found!')
        return None

    c = center_of(corners[0], corners[1], corners[2])
    corners.sort(key=lambda p: atan2(p[1] - c[1], p[0] - c[0]))
    return corners


def pointing_up(corners, center):
    x = 0
    for p in corners:
        if atan2(p[1]-center[1], p[0]-center[0]) > 0:
            x += 1
    return x == 2


def classify(hsv):
    for color in color_ranges.keys():
        if inRange(uint8([[hsv]]), color_ranges[color][0], color_ranges[color][1]):
            return color
    print('Undefined hsv:', hsv)
    return UNDEFINED


class PyraminxScanner(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.vertices = [
            (0, -4*sqrt(3)),
            (-2, -2*sqrt(3)), (2, -2*sqrt(3)),
            (-4, 0), (0, 0), (4, 0),
            (-6, 2*sqrt(3)), (-2, 2*sqrt(3)), (2, 2*sqrt(3)), (6, 2*sqrt(3))
        ]
        self.anchors = [(0, 2 / sqrt(3) - 2 * sqrt(3)), (2, 2 / sqrt(3)), (-2, 2 / sqrt(3))]
        self.facelets = [
            [self.vertices[0], self.vertices[1], self.vertices[2]],

            [self.vertices[1], self.vertices[3], self.vertices[4]],
            [self.vertices[1], self.vertices[2], self.vertices[4]],
            [self.vertices[2], self.vertices[4], self.vertices[5]],

            [self.vertices[3], self.vertices[6], self.vertices[7]],
            [self.vertices[3], self.vertices[4], self.vertices[7]],
            [self.vertices[4], self.vertices[7], self.vertices[8]],
            [self.vertices[4], self.vertices[5], self.vertices[8]],
            [self.vertices[5], self.vertices[8], self.vertices[9]]
        ]
        self.centers = [center_of(f[0], f[1], f[2]) for f in self.facelets]
        self.centers[6] = (self.centers[6][0], self.centers[5][1])  # adjust for claw

        self.img = None
        self.warped_vertices = []
        self.warped_facelets = []
        self.warped_centers = []
        self.facelet_colors = []
        self.facelet_colors_hsv = []

    @abstractmethod
    def calibrate(self):
        pass

    @abstractmethod
    def grab_image(self):
        pass

    def warp(self, warped_anchors):
        warp_mat = getAffineTransform(float32(self.anchors), float32(warped_anchors))
        warped_vertices = [tuple(v) for v in transform(array([self.vertices], dtype=float32), warp_mat)[0]]
        warped_facelets = []
        for f in self.facelets:
            warped_facelets.append([(int(v[0]), int(v[1])) for v in transform(array([f]), warp_mat)[0]])
        warped_centers = [(int(v[0]), int(v[1])) for v in transform(array([self.centers]), warp_mat)[0]]
        return warped_vertices, warped_facelets, warped_centers

    def draw(self):
        for f in self.warped_facelets:
            line(self.img, f[0], f[1], (255, 255, 255), 3)
            line(self.img, f[1], f[2], (255, 255, 255), 3)
            line(self.img, f[2], f[0], (255, 255, 255), 3)

        for p, c, hsv in zip(self.warped_centers, self.facelet_colors, self.facelet_colors_hsv):
            circle(self.img, p, 5, colors[c], 10)
            circle(self.img, p, 10, (255, 0, 255), 1)
            if c is not UNDEFINED:
                putText(self.img, c, (p[0] + 10, p[1] - 10), FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))
            else:
                putText(self.img, str(hsv), (p[0] + 10, p[1] - 10), FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))
        imshow('Result', self.img)

    def scan_face(self):
        self.warped_vertices = []
        self.warped_facelets = []
        self.warped_centers = []
        self.facelet_colors = []
        self.facelet_colors_hsv = []

        self.img = self.grab_image()
        height, width = self.img.shape[:2]

        hsv = cvtColor(self.img, COLOR_BGR2HSV)
        filtered = inRange(hsv, (1, 1, 1), (0, 0, 0))
        for color in [ORANGE, YELLOW, GREEN, BLUE]:
            in_color = inRange(hsv, color_ranges[color][0], color_ranges[color][1])
            filtered = bitwise_or(filtered, in_color)

        filtered = blur(filtered.copy(), (5, 5))

        contours = findContours(filtered.copy(), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
        contours = contours[0] if is_cv2() else contours[1]

        triangles = []
        for c in contours:
            peri = arcLength(c, True)

            if peri < 0.2 * width:
                continue

            approx = [a[0] for a in approxPolyDP(c, 0.2 * peri, True)]
            if len(approx) != 3:
                continue
            m = moments(c)
            center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
            if pointing_up(approx, center):
                continue
            print('append triangle ' + str(peri))
            triangles.append((c, center, peri))

        drawContours(self.img, [x[0] for x in triangles], -1, (255, 0, 255), 2)

        reasonable_perimeter = max([x[2] for x in triangles])
        print('reasonable perimeter: ' + str(reasonable_perimeter))
        anchor_triplet = get_best_triangle([x[1] for x in triangles], reasonable_perimeter)
        if anchor_triplet is None:
            return []

        self.warped_vertices, self.warped_facelets, self.warped_centers = self.warp(anchor_triplet)
        for p in self.warped_centers:
            mask = zeros((height, width), uint8)
            circle(mask, (p[0], p[1]), 5, 255, 10)
            bgr_mean = mean(self.img, mask)
            hsv_mean = (cvtColor(uint8([[bgr_mean]]), COLOR_BGR2HSV)[0][0])
            color = classify(hsv_mean)
            self.facelet_colors_hsv.append(hsv_mean)
            self.facelet_colors.append(color)

        return self.facelet_colors


class AppleScanner(PyraminxScanner):
    def __init__(self, camera_url):
        PyraminxScanner.__init__(self)
        self.base_url = camera_url
        self.params = {
            'fps': 0,
            'focus': 0,
            'flip': 0,
            'resolution': 3,
            'torch': 1,
            'stats': False,
            'camera': 0,
            'quality': 0.5,
            'wb': 0,
            'rotation': 4,
            'exposure': 0
        }

    def calibrate(self):
        requests.get(self.base_url + 'parameters', params=self.params)
        sleep(5)
        requests.get(self.base_url + 'parameters?focus=1&exposure=1')
        requests.get(self.base_url + 'parameters?torch=0')

    def grab_image(self):
        requests.get(self.base_url + 'parameters?torch=1')
        sleep(1)
        response = requests.get(self.base_url + 'photo')
        requests.get(self.base_url + 'parameters?torch=0')
        img = asarray(bytearray(response.content), dtype='uint8')
        return imdecode(img, IMREAD_COLOR)[0:400, 0:480]


class AndroidScanner(PyraminxScanner):
    def __init__(self, camera_url):
        PyraminxScanner.__init__(self)
        self.base_url = camera_url

    def calibrate(self):
        requests.get(self.base_url + 'settings/photo_size?set=960x720')
        requests.get(self.base_url + 'settings/orientation?set=portrait')
        requests.get(self.base_url + 'settings/focusmode?set=continuous-picture')

        # requests.get(self.base_url + 'settings/exposure_lock?set=off')
        # requests.get(self.base_url + 'enabletorch')
        # sleep(3)
        # requests.get(self.base_url + 'settings/exposure_lock?set=on')
        # requests.get(self.base_url + 'disabletorch')

        sleep(1)

    def grab_image(self):
        requests.get(self.base_url + 'enabletorch')
        sleep(1)
        response = requests.get(self.base_url + 'photo.jpg')
        requests.get(self.base_url + 'disabletorch')
        data = asarray(bytearray(response.content), dtype='uint8')
        img = array(rot90(imdecode(data, IMREAD_COLOR), 3)).copy()
        return img


if __name__ == '__main__':
    print('start of script')
    from pyraminx import Pyraminx
    pyraminx = Pyraminx()
    # scanner = AppleScanner('http://192.168.0.17/')
    scanner = AndroidScanner('http://192.168.0.12:8080/')

    print('scanner created')

    scanner.calibrate()

    print('scanner calibrated')

    while True:
        facelets = scanner.scan_face()
        print(facelets)
        if len(facelets) > 0:
            pyraminx.set_bottom_face(facelets)
        scanner.draw()
        waitKey(0)
