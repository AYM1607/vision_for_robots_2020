# pylint: disable=invalid-name

import cv2
from core import save_config_value
from core import get_config_value
from core import Direction

barriers_counter = 0

barriers_container = {}

# Possible initial configurations.
keys = [
    Direction.NORTH_WEST.name + ">" + Direction.SOUTH.name,
    Direction.NORTH_WEST.name + ">" + Direction.EAST.name,
    Direction.NORTH_EAST.name + ">" + Direction.SOUTH.name,
    Direction.NORTH_EAST.name + ">" + Direction.WEST.name,
    Direction.SOUTH_WEST.name + ">" + Direction.NORTH.name,
    Direction.SOUTH_WEST.name + ">" + Direction.EAST.name,
    Direction.SOUTH_EAST.name + ">" + Direction.NORTH.name,
    Direction.SOUTH_EAST.name + ">" + Direction.WEST.name
]

# Blocks are represented as a rectangle.
# corner_1 refers to the top left corner.
# corner_2 refers to the bottom right corner.
sub_keys = [
    "corner_1",
    "corner_2"
]

def get_scaling_factor():
    """
    Indicates by how much the parking poles structure was
    scaled with respect to the original image.

    Returns:
        tuple --- the order is x_scale then y_scale
    """

    return get_config_value("x_scale"), get_config_value("y_scale")

def scale_single_point(point):
    x_scale, y_scale = get_scaling_factor()
    x = int(round(point[0] * x_scale))
    y = int(round(point[1] * y_scale))
    return x, y


def scale_barriers():
    global barriers_container
    for conf in barriers_container:
        barriers_container[conf]["corner_1"] = scale_single_point(barriers_container[conf]["corner_1"])
        barriers_container[conf]["corner_2"] = scale_single_point(barriers_container[conf]["corner_2"])
        

def mouse_callback(event, x, y, _flags, _params):
    global barriers_counter, barriers_container, keys, sub_keys
    if event == cv2.EVENT_LBUTTONUP:
        if barriers_counter % 2 == 0:
            barriers_container[keys[int(barriers_counter / 2)]] = {}
        barriers_container[keys[int(barriers_counter / 2)]][sub_keys[barriers_counter % 2]] = (x, y)
        barriers_counter += 1
        if int(barriers_counter / 2) < len(keys):
            print("Block " + keys[int(barriers_counter / 2)] + "\t" + sub_keys[barriers_counter % 2])


def set_barriers():
    global barriers_counter, barriers_container, keys
    base_image = cv2.imread("./media/parking_base.jpg")
    cv2.namedWindow("parking")
    cv2.setMouseCallback("parking", mouse_callback)
    print("Block " + keys[0] + "\t" + sub_keys[0])

    while True:
        for block in barriers_container:
            if barriers_counter % 2 == 0:
                cv2.rectangle(base_image, barriers_container[block]["corner_1"], barriers_container[block]["corner_2"], (0, 0, 255), 2)
        cv2.imshow("parking", base_image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
    cv2.imwrite("./media/barriers.jpg", base_image)
    print("Scaling barriers")
    scale_barriers()
    print("Saving rectangles to the config file")
    save_config_value("barriers", barriers_container)
    print("Done!!")
    cv2.destroyAllWindows()

set_barriers()