'''Lowpolify any image using Delaunay triangulation'''
import sys
import warnings
from multiprocessing import Process
import cv2
import numpy as np
from scipy.spatial import Delaunay #pylint: disable-msg=E0611
import sharedmem

def chunk(l, n):
    '''Splits a list into n chunks'''
    for i in range(0, len(l), n):
        yield l[i:i + n]

def builder(part, tridex, lowpoly_image, highpoly_image):
    '''Generates a portion of the final image'''
    for tri in part:
        lowpoly_image[tridex == tri, :] = np.mean(
            highpoly_image[tridex == tri, :], axis=0)

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
    processes = [Process(target=builder, args=(
        chunks[i], tridex, lowpoly_image, highpoly_image)) for i in range(4)]
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

def get_triangulation(im, a=50, b=55, c=0.15):
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
    edges = cv2.Canny(im, a, b)
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
    # Construct Delaunay Triangulation from these set of points.
    # Reference: https://en.wikipedia.org/wiki/Delaunay_triangulation
    tris = Delaunay(pts)
    # Return triangulation
    return tris

def pre_process(highpoly_image, newSize=None):
    '''Preprocessing helper'''
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
            highpoly_image = cv2.resize(
                highpoly_image, (0, 0), fx=scale, fy=scale,
                interpolation=cv2.INTER_AREA)
    # Reduce noise in image using cv::cuda::fastNlMeansDenoisingColored
    # Reference: http://www.ipol.im/pub/art/2011/bcm_nlm/
    highpoly_image = cv2.fastNlMeansDenoisingColored(
        highpoly_image, None, 10, 10, 7, 21)
    return highpoly_image

def helper(inImage, c, outImage=None, show=False):
    '''Helper function'''
    # Read the input image
    highpoly_image = cv2.imread(inImage)
    # Call 'pre_process' function
    highpoly_image = pre_process(highpoly_image, newSize=750)
    # Use Otsu's method for calculating thresholds
    gray_image = cv2.cvtColor(highpoly_image, cv2.COLOR_BGR2GRAY)
    high_thresh, thresh_im = cv2.threshold(
        gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    low_thresh = 0.1 * high_thresh
    # Call 'get_triangulation' function
    tris = get_triangulation(highpoly_image, low_thresh, high_thresh, c)
    # Call 'get_lowpoly' function
    lowpoly_image = get_lowpoly(tris, highpoly_image)
    if np.max(highpoly_image.shape[:2]) < 750:
        scale = 750 / float(np.max(highpoly_image.shape[:2]))
        lowpoly_image = cv2.resize(lowpoly_image, None, fx=scale,
                                   fy=scale, interpolation=cv2.INTER_CUBIC)
    if show:
        compare = np.hstack([highpoly_image, lowpoly_image])
        cv2.imshow('Compare', compare)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if outImage is not None:
        cv2.imwrite(outImage, lowpoly_image)
        print('Done')

def main(args):
    '''Main function'''
    # No input image
    if len(args) < 1:
        print('Invalid')
    # Input image specified
    else:
        input_image = args[0]
        output_image = None
        fraction = 0.15
        # Output destination specified
        if len(args) == 2:
            output_image = args[1]
        if len(args) == 3:
            output_image = args[1]
            fraction = float(args[2])
        # Call helper function
        helper(inImage=input_image, c=fraction,
               outImage=output_image, show=False)

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    main(sys.argv[1:])
