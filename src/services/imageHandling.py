import tempfile
from fastapi import UploadFile
from pathlib import Path
import shutil
from typing import Callable
from typing import Tuple
from PIL import Image as imageMain
from PIL.Image import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import math
from PIL import ImageFont, ImageDraw

# scikit-image
from skimage.exposure import is_low_contrast
# brisque score
import imquality.brisque as brisque

import uuid
from matplotlib import pyplot as plt
import sys

class OptionWatermark:
    def __init__(self, text: str):
        self.text = text

class ImageHandling:
    tempfile.tempdir = "/tmp"
    
    #constructor
    def __init__(self):
        pass

    def getImageFromTmp():
        pass

    def saveImageToTmp(upload_file: UploadFile) -> Path:
        try:
            suffix = Path(upload_file.filename).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(upload_file.file, tmp)
                tmp_path = Path(tmp.name)
        finally:
            upload_file.file.close()
        return tmp_path

    # clean up 1 image
    def cleanSingleImage(self, filePathWithName: str):
        try:
            isDeleted = False
            if os.path.exists(filePathWithName):
                os.remove(filePathWithName) 
                isDeleted = True
        except os.error as e:
            print("Cannot delete certain image file with error: {}".format(e))
        return isDeleted
    
    # clean up 1 directory
    def cleanSingleDirectory(self, directoryPath: str):
        try:
            isDeleted = False
            if os.path.exists(directoryPath):
                shutil.rmtree(directoryPath)
                isDeleted = True
        except os.error as e:
            print("Cannot delete directory with error: {}".format(e))
        return isDeleted

    # create 1 directory
    def createSingleDirectory(self, directoryPath: str):
        try:
            isCreated = False
            if os.path.exists(directoryPath) is False:
                os.mkdir(directoryPath)
                isCreated = True
        except os.error as e:
            print("Cannot Create directory with error: {}".format(e))
        return isCreated

    def cleanTmpFolder():
        folder = '/tmp'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                print("Clean tmp/ folder completed!")
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        pass

    def handleUploadFile(
        self,
        upload_file: UploadFile, handler: Callable[[Path], None]
    ) -> None:
        tmp_path = self.saveImageToTmp(upload_file)
        try:
            handler(tmp_path)  # Do something with the saved temp file
        finally:
            tmp_path.unlink()  # Delete the temp file

    def printTmpDir():
        return tempfile.gettempdir()

    # TODO: Refactor for images handling, image rotation, paint over border, extract contours
    def openImagePil(imagePath: str) -> Image:
        return imageMain.open(imagePath)

    def convertPilImageToCvImage(pilImage: Image):
        return cv2.cvtColor(np.array(pilImage), cv2.COLOR_RGB2BGR)

    def convertCvImagetToPilImage(cvImage) -> Image:
        return imageMain.fromarray(cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB))

    def openImageCv(imagePath: str):
        return ImageHandling.convertPilImageToCvImage(ImageHandling.openImagePil(imagePath))

    def cvToGrayScale(cvImage):
        return cv2.cvtColor(cvImage, cv2.COLOR_BGR2GRAY)

    def cvApplyGaussianBlur(cvImage, size: int):
        return cv2.GaussianBlur(cvImage, (size, size), 0)

    # Extracts all contours from the image, and resorts them by area (from largest to smallest)
    def cvExtractContours(cvImage):
        contours, hierarchy = cv2.findContours(cvImage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)
        return contours

    # Apply new color to the outer border of the image
    def paintOverBorder(cvImage, borderX: int, borderY: int, color: Tuple[int, int, int]):
        newImage = cvImage.copy()
        height, width, channels = newImage.shape
        for y in range(0, height):
            for x in range(0, width):
                if (y <= borderY) or (height - borderY <= y):
                    newImage[y, x] = color
                if (x <= borderX) or (width - borderX <= x):
                    newImage[y, x] = color
        return newImage

    # Rotate the image around its center
    def rotateImage(cvImage, angle: float):
        newImage = cvImage.copy()
        (h, w) = newImage.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        cv2.imwrite("../../test-data/hoho.png", newImage)
        return newImage

    def removeBackground(imagePath) :
        image = cv2.imread(str(imagePath))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        result = cv2.bitwise_and(image, image, mask=thresh)
        result[thresh==0] = [255,255,255]
        strUUID = uuid.uuid4().hex
        bg = '%s/%s.png' % (tempfile.gettempdir(), strUUID)
        cv2.imwrite(bg, result)
        return bg

    def isBlur(self, filePath, size=60, thresh=10, vis=False):
        image = cv2.imread(str(filePath))
        # is blur
    	# grab the dimensions of the image and use the dimensions to
        # derive the center (x, y)-coordinates
        (h, w, _) = image.shape
        (cX, cY) = (int(w / 2.0), int(h / 2.0))
        # compute the FFT to find the frequency transform, then shift
        # the zero frequency component (i.e., DC component located at
        # the top-left corner) to the center where it will be more
        # easy to analyze
        fft = np.fft.fft2(image)
        fftShift = np.fft.fftshift(fft)
        # check to see if we are visualizing our output
        if vis:
            # compute the magnitude spectrum of the transform
            magnitude = 20 * np.log(np.abs(fftShift))
            # display the original input image

            (fig, ax) = plt.subplots(1, 2, )
            ax[0].imshow(image, cmap="gray")
            ax[0].set_title("Input")
            ax[0].set_xticks([])
            ax[0].set_yticks([])

            # display the magnitude image
            ax[1].imshow(magnitude, cmap="gray")
            ax[1].set_title("Magnitude Spectrum")
            ax[1].set_xticks([])
            ax[1].set_yticks([])
            
        # zero-out the center of the FFT shift (i.e., remove low
        # frequencies), apply the inverse shift such that the DC
        # component once again becomes the top-left, and then apply
        # the inverse FFT
        fftShift[cY - size:cY + size, cX - size:cX + size] = 0
        fftShift = np.fft.ifftshift(fftShift)
        recon = np.fft.ifft2(fftShift)
        # compute the magnitude spectrum of the reconstructed image,
        # then compute the mean of the magnitude values
        magnitude = 20 * np.log(np.abs(recon))
        mean = np.mean(magnitude)
        # the image will be considered "blurry" if the mean value of the
        # magnitudes is less than the threshold value
        return (mean <= thresh)

    def isNoise(self, filePath):
        image = cv2.imread(str(filePath))
        # Convert image to HSV color space
        rgb2bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        bgr2hsv = cv2.cvtColor(rgb2bgr, cv2.COLOR_BGR2HSV)

        # Calculate histogram of saturation channel
        s = cv2.calcHist([bgr2hsv], [1], None, [256], [0, 256])

        # Calculate percentage of pixels with saturation >= p
        p = 0.05
        s_perc = np.sum(s[int(p * 255):-1]) / np.prod(bgr2hsv.shape[0:2])

        # Percentage threshold; above: valid image, below: noise
        s_thr = 0.5
        return s_perc > s_thr

    def isLowContrast(self, filePath):
        img = cv2.imread(str(filePath))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return is_low_contrast(gray, fraction_threshold=0.3)

    def badImageFilter():
        # nudity images
        pass

    def isInWrongSkew():
        pass

    def brisqueScore(self, filePath):
        img = cv2.imread(str(filePath))
        brisqueScore: float = brisque.score(img)
        return brisqueScore

    # Adaptive histogram equalization
    def AdaptiveHistogramEqualization(self, img):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl1 = clahe.apply(img)
        return cl1

    def addWatermark(imgPath: str, op: OptionWatermark):
        try:
            path = os.path.dirname(__file__)
            # --- original image --- 
            originalImage = imageMain.open(imgPath).convert("RGBA")
            width, height = originalImage.size

            # --- text image ---
            filePath = os.path.join(path, '../../fonts', 'impact.ttf')
            font = ImageFont.truetype(filePath, 40)

            # calculate text size in pixels (width, height)
            textSize = font.getsize(op.text) 

            # create image for text
            textImage = imageMain.new('RGBA', size=textSize, color=(255,255,255,0))
            textDraw = ImageDraw.Draw(textImage)

            # draw text and color on images
            textDraw.text((0, 0), text=op.text, fill=(255, 255, 255, 129), font=font) # fill="#F5F5F5"

            # rotate text image and fill with transparent color
            rotatedTextImage = textImage.rotate(45, expand=True, fillcolor=(0,0,0,0))

            rotatedTextImageWith, rotatedTextImageHeight = rotatedTextImage.size

            # calculate top/left corner for centered text
            parts = 6
            offsetX = width//parts
            offsetY = height//parts

            startX = width//parts - rotatedTextImageWith//2
            startY = height//parts - rotatedTextImageHeight//2

            for a in range(0, parts, 2):
                for b in range(0, parts, 2):
                    x = startX + a*offsetX
                    y = startY + b*offsetY
                    # image with the same size and transparent color (..., ..., ..., 0) 
                    watermarksImage = imageMain.new('RGBA', size=(width, height), color=(255,255,255,0))
                    # put text in expected place on watermarks image
                    watermarksImage.paste(rotatedTextImage, (x, y))
                    # put watermarks image on original image
                    originalImage = imageMain.alpha_composite(originalImage, watermarksImage)
                    
            originalImage = originalImage.convert('RGB')
            originalImage.save(imgPath)

            return imgPath
        except:
            print("Errors addWatermark: {}".format(sys.exc_info()))
