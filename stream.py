#!/usr/bin/env python2
from pvapi import PvAPI, Camera
import time
# from psychopy import visual, event, core, monitors, logging, tools
from scipy.misc import imsave
import numpy as np
import multiprocessing as mp
import threading
from Queue import Queue
import sys
import errno
import os
import optparse
import hashlib

sys.path.append('/usr/local/lib/python2.7/site-packages')

# compute a hash from the current time so that we don't accidentally overwrite old data
run_hash = hashlib.md5(str(time.time())).hexdigest()


parser = optparse.OptionParser()
parser.add_option('--output-path', action="store", dest="output_path", default="/tmp/frames", help="out path directory [default: /tmp/frames]")
parser.add_option('--output-format', action="store", dest="output_format", type="choice", choices=['tif', 'png', 'npz', 'pkl'], default='tif', help="out file format, tif | png | npz | pkl [default: tif]")
parser.add_option('--use-pvapi', action="store_true", dest="use_pvapi", default=True, help="use the pvapi")
parser.add_option('--use-opencv', action="store_false", dest="use_pvapi", help="use some other camera")
parser.add_option('--write-process', action="store_true", dest="save_in_separate_process", default=True, help="spawn process for disk-writer [default: True]")
parser.add_option('--write-thread', action="store_false", dest="save_in_separate_process", help="spawn threads for disk-writer")
parser.add_option('--frame-rate', action="store", dest="frame_rate", help="requested frame rate", type="float", default=60.0)

parser.add_option('--no-camera', action="store_false", dest="acquire_images", default=True, help="just run PsychoPy protocol")
parser.add_option('--save-images', action="store_true", dest="save_images", default=False, help="save camera frames to disk")
# parser.add_option('--fullscreen', action="store_true", dest="fullscreen", default=True, help="display full screen [defaut: True]")
# parser.add_option('--debug-window', action="store_false", dest="fullscreen", help="don't display full screen, debug mode")

(options, args) = parser.parse_args()

# acquire_images = True
# save_images = True
acquire_images = options.acquire_images
save_images = options.save_images
# fullscreen = options.fullscreen
if not acquire_images:
    save_images = False

output_path = options.output_path
output_format = options.output_format
save_in_separate_process = options.save_in_separate_process
frame_rate = options.frame_rate

use_pvapi = options.use_pvapi

save_as_tif = False
save_as_png = False
save_as_npz = False
if output_format=='tif':
    save_as_tif = True
elif output_format == 'png':
    save_as_png = True
elif output_format == 'npz':
    save_as_npz = True

# Make the output path if it doesn't already exist
try:
    os.mkdir(output_path)
except OSError, e:
    if e.errno != errno.EEXIST:
        raise e
    pass


import cv2
          
cv2.namedWindow('cam_window')
import numpy as np
r = np.random.rand(100,100)
cv2.imshow('cam_window', r)



# -------------------------------------------------------------
# Camera Setup
# -------------------------------------------------------------

camera = None

if acquire_images:

    print('Searching for camera...')


    # try PvAPI

    camera = None
    cameras = []
    cam_info = None

    if use_pvapi:

        pvapi_retries = 50

        # get the camera list
        
        print('Getting camera driver..')
        
        n = 0
        camera_driver = None
        while camera_driver is None and n < pvapi_retries:
            try:
                camera_driver = PvAPI(libpath='./')
            except Exception as e:
                print('.')
                time.sleep(0.1)
                camera_driver = None
                n += 1

        print('Connecting to camera...')

        n = 0
        cam_info = None

        # Let it have a few tries in case the camera is waking up

        while cam_info is None and n < pvapi_retries:
            try:
                cameras = camera_driver.camera_list()
                cam_info = cameras[0]
                n += 1
                print '\rsearching...'
                time.sleep(0.5)

                if cameras[0].UniqueId == 0L:
                    raise Exception('No cameras found')
                time.sleep(0.5)
                camera = Camera(camera_driver, cameras[0])

                print("Bound to PvAPI camera (name: %s, uid: %s)" % (camera.name, camera.uid))

                camera.request_frame_rate(frame_rate)

            except Exception as e:

                # print("%s" % e)
                cam_info = None

    else:

        import flycapture2 as fc2
        print fc2.get_library_version()
        camera = fc2.Context()
        print camera.get_num_of_cameras()
        camera.connect(*camera.get_camera_from_index(0))
        print camera.get_camera_info()
        # c.set_video_mode_and_frame_rate(fc2.VIDEOMODE_1280x960Y16,
        #         fc2.FRAMERATE_7_5)
        m, f = camera.get_video_mode_and_frame_rate()
        print m, f
        # print c.get_video_mode_and_frame_rate_info(m, f)
        print camera.get_property_info(fc2.FRAME_RATE)
        p = camera.get_property(fc2.FRAME_RATE)
        print p
        camera.set_property(**p)
        # camera.start_capture()


    if camera is None:
        try:
            import opencv_fallback

            print "Trying opencv fallback..."
            camera = opencv_fallback.Camera(0)

            print("Bound to OpenCV fallback camera.")
        except Exception as e2:
            print("Could not load OpenCV fallback camera")
            print e2
            exit()


# -------------------------------------------------------------
# Set up a thread to write stuff to disk
# -------------------------------------------------------------

if save_in_separate_process:
    im_queue = mp.Queue()
else:
    im_queue = Queue()

disk_writer_alive = True

def save_images_to_disk():
    print('Disk-saving thread active...')
    n = 0
    while disk_writer_alive: 
        if not im_queue.empty():
            
            try:
                result = im_queue.get()

                if result is None:
                    break

                # unpack
                (im_array, metadata) = result
            except e as Exception:
                break

            # print 's1: %d, s2: %d' % (metadata['s1'], metadata['s2'])
            name = "run_%s_%d_s1_%d_s2_%d_ts_%d_%d" % (run_hash, metadata['f'], metadata['s1'], metadata['s2'], metadata['ts0'], metadata['ts1'])

            # print name
            if save_as_png:
                imsave('%s/%s.png' % (output_path, name), im_array)
            else:
                np.savez_compressed('%s/%s.npz' % (output_path, name), im_array)
            n += 1
    print('Disk-saving thread inactive...')


if save_in_separate_process:
    disk_writer = mp.Process(target=save_images_to_disk)
else:
    disk_writer = threading.Thread(target=save_images_to_disk)

# disk_writer.daemon = True

if save_images:
    disk_writer.daemon = True
    disk_writer.start()



nframes = 0
frame_accumulator = 0
t = 0
last_t = None

report_period = 60 # frames

if acquire_images:
    # Start acquiring
    camera.start_capture() #capture_start()
    # camera.queue_frame()


print('Beginning imaging [Hit ESC to quit]...')


while True:

    t = time.time()

    if acquire_images:
        # im_array, meta = camera.capture_wait()
        # camera.queue_frame()
        im_array = np.array(camera.retrieve_buffer(fc2.Image()))

        nframes += 1

        if save_images:
            meta['f'] = nframes
            im_queue.put((im_array, meta))

        im_to_show = im_array #(im_array / 2**4).astype(np.uint8)
        cv2.imshow('cam_window', im_to_show)

    key = cv2.waitKey(1) & 0xFF
        # if key is 27 or key is 113:
        #     break

    if key == ord("q"):
        break

    if nframes % report_period == 0:
        if last_t is not None:
            print('avg frame rate: %f [Hit ESC to quit]' % (report_period / (t - last_t)))
        last_t = t

    # Break out of the while loop if these keys are registered
    # if event.getKeys(keyList=['escape', 'q']):
    #     break

    # if nframes > 50:
    #     break


cv2.waitKey(1)
cv2.destroyAllWindows()
cv2.waitKey(1)


if acquire_images:
    # camera.capture_end()
    # camera.close()
    print "Closing camera..."
    camera.stop_capture()
    camera.disconnect()

if im_queue is not None:
    im_queue.put(None)

if save_images:
    hang_time = time.time()
    nag_time = 0.05

    sys.stdout.write('Waiting for disk writer to catch up (this may take a while)...')
    sys.stdout.flush()
    waits = 0
    while not im_queue.empty():
        now = time.time()
        if (now - hang_time) > nag_time:
            sys.stdout.write('.')
            sys.stdout.flush()
            hang_time = now
            waits += 1

    print waits
    print("\n")

    if not im_queue.empty():
        print("WARNING: not all images have been saved to disk!")

    disk_writer_alive = False

    if save_in_separate_process and disk_writer is not None:
        print("Terminating disk writer...")
        disk_writer.join()
        # disk_writer.terminate()
    
    # disk_writer.join()
    print('Disk writer terminated')        

