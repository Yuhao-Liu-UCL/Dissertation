from osgeo import gdal
import torch
import numpy
def readTif_to_tensor(img_path):
    gdal_img = gdal.Open(img_path)
    # get column
    width = gdal_img.RasterXSize
    # get rows
    height = gdal_img.RasterYSize
    # get data
    data = gdal_img.ReadAsArray(0, 0, width, height)
    data=data.astype(numpy.float32)
    if data.ndim==2:
        data=data.reshape(1,height,width)

    return torch.from_numpy(data)
if __name__ == '__main__':

    img=readTif_to_tensor('../img.tiff')
    print(img[1,1,1])




