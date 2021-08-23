import numpy

from d_model import D_model
my_Model = D_model(9)
import torch
import torchvision
from read_tif import readTif_to_tensor
import cv2
import torch.nn.functional as F
my_Model.load_state_dict(torch.load('../save_models/myModel27.pth'))
testimg=readTif_to_tensor(r'C:\Users\LYH\Desktop\dissertation\landsat8_tt\train\img\LC81390292014135LGN00_toa_1_6')
testimg=testimg/10000


min_img=torch.zeros(512,512)
# min_img[testimg[7,:,:]==testimg.min()]=0
min_img=testimg[7,:,:]*120
min_img[min_img<0]=0

min_img=torch.reshape(min_img,(512,512))
min_img=min_img.numpy().astype(numpy.uint8)

cv2.imwrite('../testimg/015min77_.jpg',min_img)

testimg=torch.reshape(testimg,(-1,9,512,512))
testimg=testimg.to(torch.device('cuda'))
my_Model=my_Model.to(torch.device('cuda'))
my_Model.eval()
with torch.no_grad():
    output=my_Model(testimg)
    output=torch.sigmoid(output)
    output[output>=0.5]=255
    output[output<0.5]=0

output = torch.reshape(output, (512,512))
output = output.cpu().numpy().astype(numpy.uint8)
cv2.imwrite('../testimg/1_5_27.jpg',output)
tar=readTif_to_tensor(r'C:\Users\LYH\Desktop\dissertation\landsat8_tt\train\target\LC81390292014135LGN00_target_1_5')
tar[tar==1]=255
tar=torch.reshape(tar,(512,512))
tar =tar.numpy().astype(numpy.uint8)
cv2.imwrite('../testimg/target_1_5.jpg',tar)

