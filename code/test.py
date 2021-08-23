import torch
from matplotlib import pyplot as plt
from osgeo import gdal
from torchvision.transforms import functional as F
import cv2
import numpy as np
def readTif_to_tensor(img_path):
    gdal_img = gdal.Open(img_path)
    # get column
    width = gdal_img.RasterXSize
    # get rows
    height = gdal_img.RasterYSize
    # get data
    data = gdal_img.ReadAsArray(0, 0, width, height)
    if data.ndim==2:
        data=data.reshape(1,height,width)

    return torch.from_numpy(data)

img=readTif_to_tensor('../landsat8_tt/train/img/LC81390292014135LGN00_toa_1_4')
target= readTif_to_tensor('../landsat8_tt/train/target/LC81390292014135LGN00_target_1_4')
fmask=readTif_to_tensor('../landsat8_tt/train/fmask/LC81390292014135LGN00_fmask_1_4')

print(img.shape)
print(target.shape)
print(fmask.shape)
print(fmask.numpy())
cv2.imwrite('fmaskcv1.jpg',fmask.numpy().reshape(512,512))
cv2.imwrite('band21.jpg',(img[0,:,:]/10000*120).numpy().astype(np.int))
cv2.imwrite('target1.jpg',target[0,:,:].numpy())





