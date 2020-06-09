import cv2
from core_lib.core import Direction, save_config_value, get_config_value
from core_lib.parking import get_scaling_factor, get_final_mapped_points

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        coords = get_final_mapped_points(x, y)
        if coords:
            print("ESTACIONAMIENTO LIBRE, presione 'q' para continuar")
            print(coords)

            cv2.rectangle(output_image, tuple(coords["corner_1"]), tuple(coords["corner_2"]), (0, 255, 0), 2)
            cv2.circle(output_image, tuple(coords["real_center"]), 1, (0, 0, 255), 2)
        else:
            print("NO ES ESTACIONAMIENTO, INTENTE DE NUEVO")


def show():
    while True:
            cv2.imshow("input image", input_image)
            cv2.imshow("output image", output_image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    cv2.destroyAllWindows()

input_image = cv2.imread('core_lib/media/parking_base.jpg')
output_image = cv2.imread('core_lib/media/route_planner.jpg')
cv2.namedWindow("input image")
cv2.setMouseCallback("input image", click)
cv2.namedWindow("output image")

show()
