import cv2


def make_video(images, output_path, fps=1, size=(640, 640), is_color=True):
    """
    Makes video using xvid codec. Increase FPS for faster timelapse.

    :param images: List of the image paths to be added as frames to the video
    :param output_path: Path to output video, must end with .avi
    :param fps: Desired frame rate.
    :param size: Size of the video frames.
    :param is_color: If it is True, the encoder will expect and encode color frames, otherwise it will work with grayscale frames.

    :return: The function does not return anything. It directly saves the video at the position indicated in output_path.
    """
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    vid = cv2.VideoWriter(output_path, fourcc, fps, size, is_color)
    for image in images:
        vid.write(cv2.imread(image))
    vid.release()
    cv2.destroyAllWindows()
