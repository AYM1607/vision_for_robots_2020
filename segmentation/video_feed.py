"""
Exports the VideoFeed class which allows reading frames from a camera.
"""
import cv2


class VideoFeed:
    """
    Allows reading frames from an arbitrary camera with built-in resize.

    Parameters:
        camera_index {integer} -- The index of the camera from which the
            frames will be read. Defaults to 0.
        width {integer} -- The target width of the captured images.
            Defaults to -1. Any negative number will keep the original
            dimension.
    """

    def __init__(self, camera_index=0, width=-1):
        self.video_feed = cv2.VideoCapture(camera_index)
        self.width = width

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.video_feed.release()

    def read(self):
        """
        Reads a single frame from the video feed.

        Returns:
            Tuple -- Contains:
                success: Whether the frame was read successfully.
                image: The image if success is True, None otherwise.

        """

        success, image = self.video_feed.read()
        if not success:
            return False, None

        # Get the target width.
        width = len(image[0]) if self.width < 0 else self.width

        # Get the target height maintaining aspect ratio.
        conversion_ration = width / len(image[0])
        height = int(len(image) * conversion_ration)

        return True, cv2.resize(image, (width, height))


def main():
    """
    Showcases the usage of the VideFeed class.
    """

    with VideoFeed(camera_index=1, width=250) as feed:
        while True:

            success, image = feed.read()

            if success:
                cv2.imshow("Test", image)
            else:
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
