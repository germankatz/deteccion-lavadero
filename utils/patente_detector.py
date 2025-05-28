import cv2
import numpy as np

# Principal fuente (crack): https://www.youtube.com/watch?v=9dyaI3GyUtc&ab_channel=SantiagoFiorino

def es_rectangulo(approx, tolerancia_angular=19):
    def angle(pt1, pt2, pt0):
        v1 = pt1 - pt0
        v2 = pt2 - pt0
        cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))

    if len(approx) != 4:
        return False

    pts = approx.reshape(4, 2)
    angles = [
        angle(pts[0], pts[2], pts[1]),
        angle(pts[1], pts[3], pts[2]),
        angle(pts[2], pts[0], pts[3]),
        angle(pts[3], pts[1], pts[0]),
    ]
    return all(abs(a - 90) < tolerancia_angular for a in angles)

def detectar_patente(frame_roi, umbral=145):
    gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, umbral, 255, cv2.THRESH_BINARY_INV)
    bw = cv2.bilateralFilter(bw, 11, 17, 17)

    contornos, _ = cv2.findContours(bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    aspect_ratio_objetivo = 400.0 / 130.0  # ≃3.08
    min_area = frame_roi.shape[0] * frame_roi.shape[1] * 0.01

    mejor_candidato = None
    menor_error_aspect_ratio = float('inf')

    for cnt in contornos:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if not es_rectangulo(approx):
            continue

        x, y, w, h = cv2.boundingRect(approx)
        aspect = float(w) / float(h)
        error_aspect = abs(aspect - aspect_ratio_objetivo)

        if error_aspect < menor_error_aspect_ratio:
            menor_error_aspect_ratio = error_aspect
            mejor_candidato = approx

    img_contornos = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    if mejor_candidato is not None:
        cv2.drawContours(img_contornos, [mejor_candidato], -1, (0, 255, 0), 2)

    return bw, mejor_candidato, img_contornos