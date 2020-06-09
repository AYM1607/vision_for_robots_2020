import cv2
from core import save_config_value

checkpoints = {}
points_counter = 0

def mouse_callback(event, x, y, _flags, _params):
    global checkpoints, points_counter
    if event == cv2.EVENT_LBUTTONUP:
        if points_counter == 0:
            checkpoints["top_left"] = (x, y)
            points_counter += 1
            print("Click top right")
        elif points_counter == 1:
            checkpoints["top_right"] = (x, y)
            points_counter += 1
            print("Click bottom left")
        elif points_counter == 2:
            checkpoints["bottom_left"] = (x, y)
            points_counter += 1
            print("Click bottom rihgt")
        elif points_counter == 3:
            checkpoints["bottom_right"] = (x, y)
            print("Done. Press 'q' to continue")

def set_checkpoints():
    global checkpoints
    
    base_image = cv2.imread("./media/parking_base.jpg")
    cv2.namedWindow("parking")
    cv2.setMouseCallback("parking", mouse_callback)
    print("Set checkpoints method!!")
    print("Click top left")

    while True:
        for key in checkpoints:
            cv2.circle(base_image, checkpoints[key], 2, (0, 255, 0), 4)
        cv2.imshow("parking", base_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cv2.imwrite("./media/checkpoints.jpg", base_image)
    print("Saving checkpoints to the config file")
    save_config_value("checkpoints", checkpoints)
    cv2.destroyAllWindows()
    return 0

set_checkpoints()