import cv2
import numpy as np

img = np.zeros((300, 300, 3), dtype=np.uint8)
cv2.putText(img, "TEST", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

cv2.namedWindow("Ventana", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Ventana", 600, 400)
cv2.imshow("Ventana", img)
cv2.waitKey(0)
cv2.destroyAllWindows()