import random
import sys

sys.path.append('/usr/local/lib/python2.7/site-packages')

import os
import cv2
import numpy as np

# import matplotlib.pyplot as plt
# get_ipython().magic(u'matplotlib inline')

import copy
import flycapture2 as fc2
import numpy as np


def get_data():
    """Return 3 random integers between 0 and 9"""
    # return random.sample(range(10), 3)
    return np.array(c.retrieve_buffer(fc2.Image()))

def consume():
    """Displays a running average across lists of integers sent to it"""
    running_sum = 0
    data_items_seen = 0

    while True:
        key = cv2.waitKey(1) & 0xFF

        data = yield
        # data_items_seen += len(data)
        # running_sum += sum(data)
        # print('The running average is {}'.format(running_sum / float(data_items_seen)))
        # np.array(c.retrieve_buffer(fc2.Image()))
        cv2.imshow("image", data)


        if key == ord("q"):
            break


    cv2.waitKey(1)
    cv2.destroyAllWindows()
    cv2.waitKey(1)



def produce(consumer):
    """Produces a set of values and forwards them to the pre-defined consumer
    function"""
    while True:
        data = get_data()
        #print('Produced {}'.format(data))
        consumer.send(data)
        yield

if __name__ == '__main__':
    
    print fc2.get_library_version()
    c = fc2.Context()
    print c.get_num_of_cameras()
    c.connect(*c.get_camera_from_index(0))
    print c.get_camera_info()
    # c.set_video_mode_and_frame_rate(fc2.VIDEOMODE_1280x960Y16,
    #         fc2.FRAMERATE_7_5)
    m, f = c.get_video_mode_and_frame_rate()
    print m, f
    # print c.get_video_mode_and_frame_rate_info(m, f)
    print c.get_property_info(fc2.FRAME_RATE)
    p = c.get_property(fc2.FRAME_RATE)
    print p
    c.set_property(**p)
    c.start_capture()

    cv2.startWindowThread()
    cv2.namedWindow("image")


    consumer = consume()
    consumer.send(None)
    producer = produce(consumer)

    for _ in range(10):
        print('Producing...')
        next(producer)


    c.stop_capture()
    c.disconnect()
