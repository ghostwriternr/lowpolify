'''Lowpolify any image using Delaunay triangulation'''
import random
from multiprocessing import Process

import cv2
import numpy as np
from scipy.spatial import Delaunay  #pylint: disable-msg=E0611
import sharedmem
import dlib
import face_recognition_models

# Path to predictor used in face detection model
predictor_model = face_recognition_models.pose_predictor_model_location()
# Threshold for intra-triangle variance
varhtresh = 25


def chunk(l, n):
    '''Splits a list into n chunks'''
    for i in range(0, len(l), n):
        yield l[i:i + n]


def builder(part, tridex, lowpoly_image, highpoly_image):
    '''Generates a portion of the final image'''
    for tri in part:
        lowpoly_image[tridex == tri, :] = np.mean(
            highpoly_image[tridex == tri, :], axis=0)


def PolyArea(x, y):
    '''Returns area of triangle'''
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def reduce_tail(l, index, threshold=1):
    elm = l[index]
    mask = np.linalg.norm(elm - l, axis=1) > threshold
    mask[:index + 1] = True  #ensure to return the head of the array unchanged
    return l[mask]


def my_reduce(z, threshold=1):
    z = np.array(z)
    index = 0
    while True:
        z = reduce_tail(z, index, threshold)
        index += 1
        if index == z.shape[0]:
            break
    return z.tolist()


def divideHighVariance(tris, highPolyImage):
    '''Divide triangles further if variance crosses a threshold'''
    # print(tris.points.size)
    subs = np.transpose(np.where(np.ones(highPolyImage.shape[:2])))
    subs = subs[:, :2]
    tridex = tris.find_simplex(subs)
    tridex = tridex.reshape(highPolyImage.shape[:2])
    pTris = np.unique(tridex)
    for tri in pTris:
        var3d = np.std(highPolyImage[tridex == tri, :], axis=0)
        var = sum(var3d) / 3
        if var > varhtresh:
            newPts = []
            subarr = np.asarray(np.where(tridex == tri))
            for i in range(subarr.shape[1]):
                newPts.append([subarr[0][i], subarr[1][i]])
            # x = [p[0] for p in newPts]
            # y = [p[1] for p in newPts]
            # centroid = (sum(x) / len(newPts), sum(y) / len(newPts))
            # print(centroid)
            randNewPts = [
                newPts[i] for i in np.random.randint(
                    0, len(newPts) - 1, size=int(round(0.4 * len(newPts))))
            ]
            tris.add_points(randNewPts)
            # tris.add_points([[int(round(sum(x) / len(newPts))),
            #                   int(round(sum(y), len(newPts)))]])
    # print(tris.points.size)


def get_lowpoly(tris, highpoly_image):
    '''Returns low poly image'''
    # 'highpoly_image.shape[:2]' returns the dimensions of the image.
    # 'np.ones(highpoly_image.shape[:2])' gives same size image, filled with 1.
    # So subs contains an array of all coordinates of new array.
    subs = np.transpose(np.where(np.ones(highpoly_image.shape[:2])))
    subs = subs[:, :2]
    # Find the simplices in 'tris' containing the given points
    tridex = tris.find_simplex(subs)
    # Array of image dimensions with mapping to the repective simplices.
    tridex = tridex.reshape(highpoly_image.shape[:2])
    # Retrieve the unique simplices from tridex
    p_tris = np.unique(tridex)
    # Split the list into multiple parts, to enable parallel processing
    chunks = list(chunk(p_tris, len(p_tris) // 4))
    # Initialize output image (3-channel)
    # lowpoly_image contains mean of all such points from highpoly_image, where
    # tridex = tri
    lowpoly_image = sharedmem.empty(highpoly_image.shape)
    lowpoly_image.fill(0)
    # Start 4 different processes to simultaneouly process different simplices
    processes = [
        Process(target=builder,
                args=(chunks[i], tridex, lowpoly_image, highpoly_image))
        for i in range(4)
    ]
    # Start each process
    for p in processes:
        p.start()
    # Wait for all process to finish
    for p in processes:
        p.join()
    # unint8 represents Unsigned integer (0 to 255)
    lowpoly_image = lowpoly_image.astype(np.uint8)
    # return low-poly image
    return lowpoly_image


def get_triangulation(im,
                      gray_image,
                      a=50,
                      b=55,
                      c=0.15,
                      show=False,
                      randomize=False):
    '''Returns triangulations'''
    # Using canny edge detection.
    #
    # Reference: http://docs.opencv.org/3.1.0/da/d22/tutorial_py_canny.html
    # First argument: Input image
    # Second argument: minVal (argument 'a')
    # Third argument: maxVal (argument 'b')
    #
    # 'minVal' and 'maxVal' are used in the Hysterisis Thresholding step.
    # Any edges with intensity gradient more than maxVal are sure to be edges
    # and those below minVal are sure to be non-edges, so discarded. Those who
    # lie between these two thresholds are classified edges or non-edges based
    # on their connectivity.
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_model)
    edges = cv2.Canny(gray_image, a, b)
    if show:
        cv2.imshow('Canny', edges)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        win = dlib.image_window()
    # Set number of points for low-poly edge vertices
    num_points = int(np.where(edges)[0].size * c)
    # Return the indices of the elements that are non-zero.
    # 'nonzero' returns a tuple of arrays, one for each dimension of a,
    # containing the indices of the non-zero elements in that dimension.
    # So, r consists of row indices of non-zero elements, and c column indices.
    r, c = np.nonzero(edges)
    # r.shape, here, returns the count of all points that belong to an edge.
    # So 'np.zeros(r.shape)' an array of this size, with all zeros.
    # 'rnd' is thus an array of this size, with all values as 'False'.
    rnd = np.zeros(r.shape) == 1
    # Mark indices from beginning to 'num_points - 1' as True.
    rnd[:num_points] = True
    # Shuffle
    np.random.shuffle(rnd)
    # Randomly select 'num_points' of points from the set of all edge vertices.
    r = r[rnd]
    c = c[rnd]
    # Number of rows and columns in image
    sz = im.shape
    r_max = sz[0]
    c_max = sz[1]
    # Co-ordinates of all randomly chosen points
    pts = np.vstack([r, c]).T
    if randomize:
        rand_offset = 50
        rand_dirs = [(0, rand_offset), (-rand_offset, 0), (0, -rand_offset),
                     (rand_offset, 0)]
        rnd_count = 0
        for point in pts:
            if random.random() < 0.3:
                rnd_count += 1
                rand_dir = random.randint(0, 3)
                point[0] += rand_dirs[rand_dir][0]
                point[1] += rand_dirs[rand_dir][1]
    # Append (0,0) to the vertical stack
    pts = np.vstack([pts, [0, 0]])
    # Append (0,c_max) to the vertical stack
    pts = np.vstack([pts, [0, c_max]])
    # Append (r_max,0) to the vertical stack
    pts = np.vstack([pts, [r_max, 0]])
    # Append (r_max,c_max) to the vertical stack
    pts = np.vstack([pts, [r_max, c_max]])
    # Append some random points to fill empty spaces
    pts = np.vstack([pts, np.random.randint(0, 750, size=(100, 2))])
    # print(len(pts))
    # pts = my_reduce(pts, 5)
    # print(len(pts))
    dets = detector(im, 1)
    # print("Number of faces detected: {}".format(len(dets)))
    if show:
        win.clear_overlay()
        win.set_image(im)
    for k, d in enumerate(dets):
        shape = predictor(im, d)
        for i in range(shape.num_parts):
            pts = np.vstack([pts, [shape.part(i).x, shape.part(i).y]])
        if show:
            win.add_overlay(shape)
    if show:
        win.add_overlay(dets)
        dlib.hit_enter_to_continue()
    # Construct Delaunay Triangulation from these set of points.
    # Reference: https://en.wikipedia.org/wiki/Delaunay_triangulation
    tris = Delaunay(pts, incremental=True)
    # tris_vertices = pts[tris.simplices]
    # for tri in range(tris_vertices.shape[0]):
    #     x_coords = []
    #     y_coords = []
    #     print(tris_vertices[tri])
    #     for coord in range(tris_vertices.shape[1]):
    #         x_coords.append(tris_vertices[tri][coord][0])
    #         y_coords.append(tris_vertices[tri][coord][1])
    # divideHighVariance(tris, im)
    tris.close()
    # exit(0)
    # Return triangulation
    return tris


def pre_process(highpoly_image, newSize=None):
    '''Preprocessing helper'''
    print('Preprocessing')
    # Handle grayscale images
    if highpoly_image.shape[2] == 1:
        # 'dstack' concatenates images along the third dimension
        # Similar to np.concatenate(tup, axis=2)
        # So basically, extending a gray scale image to a 3 channel image
        highpoly_image = highpoly_image.dstack(
            [highpoly_image, highpoly_image, highpoly_image])
    # Resize image. Easier to process.
    if newSize is not None:
        if newSize < np.max(highpoly_image.shape[:2]):
            scale = newSize / float(np.max(highpoly_image.shape[:2]))
            highpoly_image = cv2.resize(highpoly_image, (0, 0),
                                        fx=scale,
                                        fy=scale,
                                        interpolation=cv2.INTER_AREA)
    # Reduce noise in image using cv::cuda::fastNlMeansDenoisingColored
    # Reference: http://www.ipol.im/pub/art/2011/bcm_nlm/
    noiseless_highpoly_image = cv2.fastNlMeansDenoisingColored(
        highpoly_image, None, 10, 10, 7, 21)
    print('Preprocessing complete')
    return highpoly_image, noiseless_highpoly_image


def lowpolify(inImage, c=0.3, outImage=None, show=False):
    '''Helper function'''
    # Read the input image
    npimg = np.fromstring(inImage, np.uint8)
    highpoly_image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    # Call 'pre_process' function
    highpoly_image, noiseless_highpoly_image = pre_process(highpoly_image,
                                                           newSize=750)
    print('Begin thresholding')
    # Use Otsu's method for calculating thresholds
    gray_image = cv2.cvtColor(noiseless_highpoly_image, cv2.COLOR_BGR2GRAY)
    ycbcr_image = cv2.cvtColor(noiseless_highpoly_image, cv2.COLOR_RGB2YCrCb)
    for xdim in range(ycbcr_image.shape[0]):
        for ydim in range(ycbcr_image.shape[1]):
            ycbcr_image[xdim][ydim] = ycbcr_image[xdim][ydim][0]
    ycbcr_image = ycbcr_image[:, :, 0]
    clahe = cv2.createCLAHE()
    normalized_gray_image = clahe.apply(gray_image)
    if show:
        compare = np.hstack([gray_image, ycbcr_image])
        cv2.imshow('gray images', compare)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    high_thresh, thresh_im = cv2.threshold(ycbcr_image, 0, 255,
                                           cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # thresh_im = cv2.adaptiveThreshold(
    #     gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    if show:
        cv2.imshow('otsu image', thresh_im)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    low_thresh = 0.5 * high_thresh
    blurred_gray_image = cv2.GaussianBlur(gray_image, (0, 0), 3)
    sharp_gray_image = cv2.addWeighted(gray_image, 2.5, blurred_gray_image, -1,
                                       0)
    if show:
        cv2.imshow('Sharp gray image', sharp_gray_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    print('Triangulating')
    # Call 'get_triangulation' function
    tris = get_triangulation(highpoly_image, sharp_gray_image, low_thresh,
                             high_thresh, c, show)
    print('Triangulation complete. Begin rendering...')
    # Call 'get_lowpoly' function
    lowpoly_image = get_lowpoly(tris, highpoly_image)
    print('Rendering complete')
    if np.max(highpoly_image.shape[:2]) < 750:
        scale = 750 / float(np.max(highpoly_image.shape[:2]))
        lowpoly_image = cv2.resize(
            lowpoly_image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )
    if show:
        compare = np.hstack([highpoly_image, lowpoly_image])
        cv2.imshow('Compare', compare)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if outImage is not None:
        cv2.imwrite(outImage, lowpoly_image)
        print('Done')
    return cv2.imencode('.jpg', lowpoly_image)[1]
