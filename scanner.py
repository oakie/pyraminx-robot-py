import cv2
from math import *
import numpy as np
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


def get_best_triangle(candidates):
    min_err = 9999999999
    best_candidates = []
    for x1 in range(0, len(candidates)):
        for x2 in range(0, len(candidates)):
            if x2 == x1:
                continue
            for x3 in range(0, len(candidates)):
                if x3 == x1 or x3 == x2:
                    continue
                v1 = (candidates[x1][0] - candidates[x2][0], candidates[x1][1] - candidates[x2][1])
                v2 = (candidates[x2][0] - candidates[x3][0], candidates[x2][1] - candidates[x3][1])
                v3 = (candidates[x3][0] - candidates[x1][0], candidates[x3][1] - candidates[x1][1])

                peri = dist_between(v1, v2) + dist_between(v2, v3) + dist_between(v3, v1)
                if peri < 600 or peri > 1000:
                    continue

                a = 180 * angle_between(v1, v2) / pi
                b = 180 * angle_between(v2, v3) / pi
                c = 180 * angle_between(v3, v1) / pi

                err = (a - 60) * (a - 60) + (b - 60) * (b - 60) + (c - 60) * (c - 60)
                print a, b, c, peri, ' : ', err
                if err < min_err:
                    min_err = err
                    best_candidates = [candidates[x1], candidates[x2], candidates[x3]]
    if len(best_candidates) != 3:
        print 'No triangle candidates found!'
        return None
    c = center_of(best_candidates[0], best_candidates[1], best_candidates[2])
    best_candidates.sort(key=lambda p: atan2(p[1] - c[1], p[0] - c[0]))
    print 'best triangle candidate: ', best_candidates
    return best_candidates


class PyraminxScanner(object):
    def __init__(self, camera_url):
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
        self.ranges = {
            YELLOW: [(25, 100, 100), (35, 255, 255)],
            BLUE: [(90, 100, 100), (120, 255, 255)],
            GREEN: [(50, 100, 100), (70, 255, 255)],
            ORANGE: [(0, 100, 100), (25, 255, 255)]
        }
        self.colors = {
            YELLOW: (0, 255, 255),
            BLUE: (255, 0, 0),
            GREEN: (0, 255, 0),
            ORANGE: (0, 100, 255),
            UNDEFINED: (127, 127, 127)
        }
        self.img = None
        self.warped_vertices = []
        self.warped_facelets = []
        self.warped_centers = []
        self.facelet_colors = []
        self.facelet_colors_hsv = []

    def calibrate(self):
        requests.get(self.base_url + 'parameters', params=self.params)
        sleep(5)
        requests.get(self.base_url + 'parameters?focus=1&exposure=1')
        requests.get(self.base_url + 'parameters?torch=0')

    def grab_image(self):
        requests.get(self.base_url + 'parameters?torch=1')
        sleep(0.5)
        response = requests.get(self.base_url + 'photo')
        requests.get(self.base_url + 'parameters?torch=0')
        img = np.asarray(bytearray(response.content), dtype='uint8')
        return cv2.imdecode(img, cv2.IMREAD_COLOR)[0:400, 0:480]

    def warp(self, warped_anchors):
        warp_mat = cv2.getAffineTransform(np.float32(self.anchors), np.float32(warped_anchors))
        warped_vertices = [tuple(v) for v in cv2.transform(np.array([self.vertices], dtype=np.float32), warp_mat)[0]]
        warped_facelets = []
        for f in self.facelets:
            warped_facelets.append([(int(v[0]), int(v[1])) for v in cv2.transform(np.array([f]), warp_mat)[0]])
        warped_centers = [(int(v[0]), int(v[1])) for v in cv2.transform(np.array([self.centers]), warp_mat)[0]]
        return warped_vertices, warped_facelets, warped_centers

    def classify(self, hsv):
        for color in self.ranges.keys():
            if cv2.inRange(np.uint8([[hsv]]), self.ranges[color][0], self.ranges[color][1]):
                return color
        return UNDEFINED

    def draw(self):
        for f in self.warped_facelets:
            cv2.line(self.img, f[0], f[1], (255, 255, 255), 3)
            cv2.line(self.img, f[1], f[2], (255, 255, 255), 3)
            cv2.line(self.img, f[2], f[0], (255, 255, 255), 3)

        for p, c, hsv in zip(self.warped_centers, self.facelet_colors, self.facelet_colors_hsv):
            cv2.circle(self.img, p, 5, self.colors[c], 10)
            cv2.circle(self.img, p, 10, (255, 0, 255), 1)
            if c is not UNDEFINED:
                cv2.putText(self.img, c, (p[0]+10, p[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))
            else:
                cv2.putText(self.img, str(hsv), (p[0] + 10, p[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))
        cv2.imshow('Result', self.img)

    def scan_face(self):
        self.warped_vertices = []
        self.warped_facelets = []
        self.warped_centers = []
        self.facelet_colors = []
        self.facelet_colors_hsv = []

        self.img = self.grab_image()
        height, width = self.img.shape[:2]

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        candidates = []
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.2 * peri, True)
            if len(approx) != 3:
                continue
            m = cv2.moments(c)
            candidates.append((int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])))

        tri = get_best_triangle(candidates)
        if tri is not None:
            self.warped_vertices, self.warped_facelets, self.warped_centers = self.warp(tri)
            for p in self.warped_centers:
                mask = np.zeros((height, width), np.uint8)
                cv2.circle(mask, (p[0], p[1]), 5, 255, 10)
                bgr_mean = cv2.mean(self.img, mask)
                hsv_mean = tuple(cv2.cvtColor(np.uint8([[bgr_mean]]), cv2.COLOR_BGR2HSV)[0][0])
                color = self.classify(hsv_mean)
                self.facelet_colors_hsv.append(hsv_mean)
                self.facelet_colors.append(color)

        self.draw()
        cv2.waitKey(0)
        return self.facelet_colors


if __name__ == '__main__':
    from pyraminx import Pyraminx
    pyraminx = Pyraminx()
    scanner = PyraminxScanner('http://192.168.0.17/')
    scanner.calibrate()

    while True:
        facelets = scanner.scan_face()
        print facelets
        pyraminx.set_bottom_face(facelets)
        scanner.draw()
        cv2.waitKey(0)
