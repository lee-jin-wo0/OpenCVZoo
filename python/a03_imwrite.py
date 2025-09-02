import cv2

def main():
    imgfile='/home/aa/OpenCVZoo/data/lenna.bmp'
    img = cv2.imread(imgfile)
    cv2.imwrite('/home/aa/OpenCVZoo/data/lenna_copy.png', img)
    cv2.imwrite('/home/aa/OpenCVZoo/data/lenna_copy2.png', img, (cv2.IMWRITE_PNG_COMPRESSION, 9))
    cv2.imwrite('/home/aa/OpenCVZoo/data/lenna_copy.jpg', img, (cv2.IMWRITE_JPEG_QUALITY, 60))

if __name__ == "__main__":
    main()
