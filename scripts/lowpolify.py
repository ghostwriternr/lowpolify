import time
import cv2
import numpy as np
import scipy
from scipy.spatial import Delaunay
import sys

# create a new image using the average color for each triangle


def getLowPoly(tris, highPolyImage):
    # define this in the other function so we can use the same vars
    def colorImage(tris, rv=None):
        for tri in tris:
            lowPolyImage[tridex == tri, :] = np.mean(
                highPolyImage[tridex == tri, :], axis=0)
    # subs is the subscripts of all parts of the image
    # so tridex holds, for each pixel in [r*row+c] organization, each triangle
    # for each pixel
    # it's kind of a lookup table
    subs = np.transpose(np.where(np.ones(highPolyImage.shape[:2])))
    subs = subs[:, :2]
    tridex = tris.find_simplex(subs)
    tridex = tridex.reshape(highPolyImage.shape[:2])
    pTris = np.unique(tridex)
    lowPolyImage = np.zeros(highPolyImage.shape)

    colorImage(pTris)
    lowPolyImage = lowPolyImage.astype(np.uint8)
    return lowPolyImage


def getTriangulation(im, a=50, b=55, c=0.15, debug=False):

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
    numPoints = np.where(edges)[0].size * c
    # Return the indices of the elements that are non-zero.
    # 'nonzero' returns a tuple of arrays, one for each dimension of a,
    # containing the indices of the non-zero elements in that dimension.
    # So, r consists of row indices of non-zero elements, and c column indices.
    r, c = np.nonzero(edges)
    # r.shape, here, returns the count of all points that belong to an edge.
    # So 'np.zeros(r.shape)' an array of this size, with all zeros.
    # 'rnd' is thus an array of this size, with all values as 'False'.
    rnd = np.zeros(r.shape) == 1
    # Mark indices from beginning to 'numPoints - 1' as True.
    rnd[:numPoints] = True
    # Shuffle
    np.random.shuffle(rnd)
    # Randomly select 'numPoints' of points from the set of all edge vertices.
    r = r[rnd]
    c = c[rnd]
    # Number of rows and columns in image
    sz = im.shape
    rMax = sz[0]
    cMax = sz[1]
    # Co-ordinates of all randomly chosen points
    pts = np.vstack([r, c]).T
    # Append (0,0) to the vertical stack
    pts = np.vstack([pts, [0, 0]])
    # Append (0,cMax) to the vertical stack
    pts = np.vstack([pts, [0, cMax]])
    # Append (rMax,0) to the vertical stack
    pts = np.vstack([pts, [rMax, 0]])
    # Append (rMax,cMax) to the vertical stack
    pts = np.vstack([pts, [rMax, cMax]])
    # Construct Delaunay Triangulation from these set of points.
    # Reference: https://en.wikipedia.org/wiki/Delaunay_triangulation
    tris = Delaunay(pts)
    # Return triangulation
    return tris


def preProcess(highPolyImage, newSize=None):

    # Handle grayscale images
    if highPolyImage.shape[2] == 1:
        # 'dstack' concatenates images along the third dimension
        # Similar to np.concatenate(tup, axis=2)
        # So basically, extending a gray scale image to a 3 channel image
        highPolyImage = highPolyImage.dstack(
            [highPolyImage, highPolyImage, highPolyImage])
    # Resize image. Easier to process.
    if newSize is not None:
        scale = newSize / float(np.max(highPolyImage.shape[:2]))
        highPolyImage = cv2.resize(
            highPolyImage, (0, 0), fx=scale, fy=scale,
            interpolation=cv2.INTER_CUBIC)
    return highPolyImage


def helper(inImage, a, b, c, outImage=None, show=False):

    # Read the input image
    highPolyImage = cv2.imread(inImage)
    # Call 'preProcess' function
    highPolyImage = preProcess(highPolyImage, newSize=500)
    # Read time passed since program begin (Non-essential)
    t = time.time()
    # Call 'getTriangulation' function
    tris = getTriangulation(highPolyImage, a, b, c, debug=True)
    # Print time taken for triangulation (Non-essential)
    print(time.time() - t)
    # Read time passed since program begin (Non-essential)
    t = time.time()
    # Call 'getLowPoly' function
    lowPolyImage = getLowPoly(tris, highPolyImage)
    # Print time taken for generating lowPoly image (Non-essential)
    print(time.time() - t)

    if show:
        compare = np.hstack([highPolyImage, lowPolyImage])
        cv2.imshow('Compare', compare)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if outImage is not None:
        cv2.imwrite(outImage, lowPolyImage)


def main(args):

    # No input image
    if len(args) < 1:
        print('Invalid input')
    # Input image specified
    else:
        inputImage = args[0]
        outputImage = None
        # Output destination specified
        if len(args) == 2:
            outputImage = args[1]
        # Call helper function
        helper(inImage=inputImage, a=100, b=75,
               c=0.2, outImage=outputImage, show=True)

if __name__ == '__main__':
    main(sys.argv[1:])
