# pylint: disable=invalid-name

import cv2
from core import save_config_value
from core import Direction

barriers_counter = 0
barriers_container = {}
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

sub_keys = [
    "corner_1",
    "corner_2"
]


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

    while (int(barriers_counter / 2)) < len(keys):
        for block in barriers_container:
            if barriers_counter % 2 == 0:
                cv2.rectangle(base_image, barriers_container[block]["corner_1"], barriers_container[block]["corner_2"], (0, 0, 255), 2)
        cv2.imshow("parking", base_image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
    cv2.imwrite("./media/barriers.jpg", base_image)
    print("Done!")
    print("Saving rectangles to the config file")
    save_config_value("barriers", barriers_container)
    cv2.destroyAllWindows()

set_barriers()