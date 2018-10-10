import argparse
import csv
import cv2
import datetime
import fleep
import numpy
import os
import progressbar
import sys
import time


def unique_frame(path, debug):
    video = get_file(path)
    filename = os.path.splitext(path)[0]
    try:
        file_csv = open('{}-FPS.csv'.format(filename), 'w', newline='')
    except IOError or PermissionError:
        print("Error: Check that the .csv file isn't already used by another application.")
        return 0

    writer = csv.writer(file_csv, delimiter=',')
    writer.writerow(['Timestamp', 'FPS', 'Frametime (ms)', 'FPS Frametime'])
    cap = cv2.VideoCapture(video)
    fps_video = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    _, image_model = cap.read()
    _, current_img = cap.read()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    video_res_name = '{} - FPS.mp4'.format(filename)
    try:
        video_with_fps = cv2.VideoWriter(video_res_name, fourcc, fps_video, (width, height), True)
    except IOError or PermissionError:
        print("Error: Check that a previous FPS video file isn't already used by another application.")
        return 0
    total_fps = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    last_unique_frame = 0
    total_fps_counter = 0
    actual_fps = 0
    identical_frame = 1
    fps_countdown = 1000
    frame_time = 1000/fps_video
    bar = progressbar.ProgressBar(maxval=total_fps,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()],
                                  fd=sys.stdout)
    bar.start()

    while cap.isOpened() and current_img is not None:
        time_ms = int(((total_fps_counter * frame_time) % 1000) * 1000)
        time_s = int((total_fps_counter * frame_time / 1000) % 60)
        time_mn = int((total_fps_counter * frame_time / 60000) % 60)
        time_h = int(total_fps_counter * frame_time / 3600000)
        timestamp_raw = datetime.datetime(2018, 10, 8, time_h, time_mn, time_s, time_ms)
        timestamp_str = datetime.datetime.strftime(timestamp_raw, "%H:%M:%S:%f")[:-3]
        current_timestamp = total_fps_counter * frame_time
        current_ft = int(current_timestamp - last_unique_frame)
        identical = not detect_cluster(image_model, current_img, timestamp_str, debug)

        if current_ft == 0:
            fps_ft = 0
        else:
            fps_ft = int(1000 / (current_timestamp - last_unique_frame))
        if identical:
            row = compute_row(timestamp_str, actual_fps, current_ft, fps_ft, fps_countdown)
            identical_frame += 1
        else:
            image_model = current_img
            identical_frame = 1
            row = compute_row(timestamp_str, actual_fps, current_ft, fps_ft, fps_countdown)
            actual_fps += 1
            last_unique_frame = current_timestamp
        if fps_countdown <= 0:
            actual_fps = 0
            fps_countdown += 1000

        writer.writerow(row)
        add_im2vid(actual_fps, video_with_fps, current_img, width)
        total_fps_counter += 1
        fps_countdown -= frame_time
        bar.update(total_fps_counter)
        _, current_img = cap.read()
    bar.finish()
    file_csv.close()
    cv2.destroyAllWindows()
    video_with_fps.release()
    return


# Compute the difference between two black and white images
def diff2bin(image1, image2):
    diff = cv2.absdiff(image1, image2)
    return rgb2bin(diff)


# Compute the black and white image of an RGB image
def rgb2bin(rgb):
    gray_diff = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray_diff, 35, 255, cv2.THRESH_BINARY)
    return binary


# Detect cluster of white pixels in an image
def detect_cluster(image1, image2, timestamp, debug):
    diff_bin = diff2bin(image1, image2)
    if debug:
        try:
            if not os.path.exists('Debug/'):
                os.makedirs('Debug')
            cv2.imwrite('Debug/ Bin debug FPS {}.png'.format(timestamp.replace(':', '-')), diff_bin)
        except IOError or PermissionError:
            pass
    _, contours, _ = cv2.findContours(diff_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    big_cluster = 0
    for contour in contours:
        if contour.size > 100:
            big_cluster += 1
            if big_cluster > 10:
                return True
    return False


def add_im2vid(fps_ft, video, image, width):
    font = cv2.FONT_HERSHEY_DUPLEX
    image_fps = cv2.putText(image, text=str(fps_ft), org=(width-100, 50), fontFace=font, fontScale=2, color=(0, 230, 0),
                            thickness=5, lineType=cv2.LINE_AA)
    # cv2.startWindowThread()
    # cv2.imshow('image', image_fps)
    # cv2.waitKey()
    video.write(image_fps)


def compute_row(timestamp_str, actual_fps, current_ft, fps_ft, fps_countdown):
    if fps_countdown <= 0:
        return ("{}, {}, {}, {}".format(timestamp_str, actual_fps, current_ft, fps_ft)).split(',')
    else:
        return ("{}, , {}, {}".format(timestamp_str, current_ft, fps_ft)).split(',')


def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step


# Compute the MSE difference of two images
def mse(image1, image2):
    err = numpy.sum((image1.astype("float") - image2.astype("float")) ** 2)
    err /= float(image1.shape[0] * image1.shape[1])
    return err


# Checks if the parameter is a video
def check_is_video(file):
    with open(file, "r+b") as file:
        info = fleep.get(file.read(128))
    if info.type.__len__() > 0:
        return info.type[0] == 'video'
    else:
        return file.name[-3:] == ".ts"


# Checks if the parameter is a video
def get_file(file_path):
    is_file = False
    is_video = False
    instructions = "Please give the video name including its extension. E.g. \"C:\\video.avi\":\n"

    if os.path.isfile(file_path):
        is_file = True
        is_video = check_is_video(file_path)
    while not is_file or not is_video:
        if is_file and not is_video:
            file_path = input("The file isn't a video. {}".format(instructions))
        else:
            file_path = input("Incorrect path. {}".format(instructions))
        if os.path.isfile(file_path):
            is_file = True
            is_video = check_is_video(file_path)
        else:
            is_file = False

    return file_path


def main(path, debug):
    print(datetime.datetime.now())
    unique_frame(path, debug)
    print(datetime.datetime.now())
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
                    help="Path to input video file")
    ap.add_argument("-d", "--debug", required=False, default=False,
                    help='Output every difference in black and white image to a "Debug" folder')
    args = vars(ap.parse_args())
    main(args["input"], args["debug"])
