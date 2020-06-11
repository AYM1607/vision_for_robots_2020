import cv2

from core_lib.drawing import draw_results_ui


def main():
    while True:
        draw_results_ui([])

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
