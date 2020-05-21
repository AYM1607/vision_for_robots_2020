"""
This program calibrates color of an object in livefeed.
"""
import cv2
import json
from core_lib.video_feed import VideoFeed

image = None
new_color_samples = [[],[],[]]

def get_neighborhood_intensity(event, x, y, flags, param):
    """
    Get the neighborhood intensity samples of a pixel neighborhood.
    """
    global image
    global new_color_samples

    if event == cv2.EVENT_LBUTTONDOWN:
        coordinate_differences = [(-1, -1), (0, -1), (1, -1), 
                                  (-1,  0), (0,  0), (1,  0),
                                  (-1,  1), (0,  1), (1,  1)]
        height, width, channels = image.shape

        for x_offset, y_offset in coordinate_differences:
            new_x = x + x_offset
            new_y = y + y_offset
            if 0 <= new_x < width and 0 <= new_y < height:
                for channel in range(channels):
                    new_color_samples[channel].append(image[new_y][new_x][channel])

def average(channel_sample):
    """
    Get the valid unvisited neighbours for a given point.

    Arguments:
        channel_sample {array} -- List of intensity samples of a single image channel.

    Returns:
        Int - Rounded average of all intensities.
    """
    return int(round(sum(channel_sample) / len(channel_sample)))

def samples_available(samples):
    """
    Get the valid unvisited neighbours for a given point.

    Arguments:
        samples {array} -- List of color samples.

    Returns:
        Boolean - Bool indicating if samples are available for processing.
    """
    for sample in samples:
        if len(sample) == 0:
            return False
    return True

def main():
    """
    Performs the calibration by getting average of pixels clicked by user.
    Reads images directly from the webcam.
    """
    global image
    global new_color_samples

    colors = {}
    new_color = []

    cv2.namedWindow("Color calibration")
    cv2.setMouseCallback("Color calibration", get_neighborhood_intensity, 0)

    print("Starting calibration ....")
    print("Click image to get average color intensity of an object")
    print("Press 'n' to calibrate new color")
    print("Press 'q' to finish calibration")

    with VideoFeed(camera_index=0, width=450) as feed:
        while True:
            _, image = feed.read()

            cv2.imshow("Color calibration", image)

            # Append new calibrated color.
            if cv2.waitKey(1) & 0xFF == ord("n"):
                if samples_available(new_color_samples):
                    for channel in range(len(new_color_samples)):
                        new_color.append(average(new_color_samples[channel]))
                    print("New color: ", new_color)
                    colors["COLOR_{}".format(len(colors) + 1)] = new_color

                    new_color = []
                    new_color_samples = [[],[],[]]
                else:
                    print("No samples available, click image to get average color intensity of an object")

            # End the loop when "q" is pressed and export colors.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Finished calibrating")
                print(colors)
                # Dump calibrated colors to JSON.
                with open("colors.json", "w") as write_file:
                    json.dump(colors, write_file)
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
