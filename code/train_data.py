from torch import nn
import math
from d_model import D_model
import torch
import time
from torch.utils.tensorboard import  SummaryWriter
from torch.utils.data import  Dataset, DataLoader
from read_tif import readTif_to_tensor
import os
#device
myDevice = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(torch.cuda.get_device_name())
#create model
myModel=D_model(9)
myModel = myModel.to(myDevice) # to gpu

#total epoch numbers
epoch=1000
#learning rate
learning_rate=0.1
#batch_size
batch_size=1
#loss function
loss_fn=nn.MSELoss(reduction='sum')
loss_fn = loss_fn.to(myDevice) #to gpu

#optimizer
optimizer = torch.optim.SGD(myModel.parameters(),lr=learning_rate,momentum=0.7)
#######################################################################################
class Train_datasets(Dataset):
    def __init__(self,train_dir,target_dir):

        self.train_dir=train_dir
        self.target_dir=target_dir
        self.img_name_list=sorted(os.listdir(self.train_dir))
        self.tar_name_list=sorted(os.listdir(self.target_dir))


    def __getitem__(self, idx):
        img_path=os.path.join(self.train_dir,self.img_name_list[2*idx])
        tar_path=os.path.join(self.target_dir,self.tar_name_list[2*idx])
        img = readTif_to_tensor(img_path)
        target= readTif_to_tensor(tar_path)
        return img,target

    def __len__(self):
        return int(len(self.img_name_list)/2)

train_data=Train_datasets('../landsat8_tt/train/img','../landsat8_tt/train/target')
test_data= Train_datasets('../landsat8_tt/test/img','../landsat8_tt/train/target')

print(len(train_data))
print(len(test_data))
###########################################################################################
# load data
train_dataloader=DataLoader(train_data,batch_size=batch_size,shuffle=True )# pin memory,drop_last and num_workers
test_dataloader=DataLoader(test_data,batch_size=batch_size,shuffle=True)

#begin training and test

total_train_step = 0  #record the training number
writer = SummaryWriter('../Train_logs')  #write in tensorboard

for i in range(epoch):
    print('-------------------the round {} training begin-------------------------- '.format(i+1))
    start_train_time=time.time()
    # training mode
    myModel.train()
    per_epoch_train_loss = 0  # record average loss for one round
    for i_train,(imgs,targets) in enumerate(train_dataloader):

        imgs=imgs.to(myDevice)
        targets=targets.to(myDevice)

        outputs=myModel(imgs)
        loss=loss_fn(outputs,targets)
        per_epoch_train_loss= per_epoch_train_loss + loss.item()
        # model optimazation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # output results per 100 times
        total_train_step=total_train_step+1
        if total_train_step %100 ==0:
            print('{} times optimize,Loss is {}'.format(total_train_step,loss.item()))
            writer.add_scalar('Training loss',loss.item(),total_train_step)

    print('per_epoch_train_loss is ', per_epoch_train_loss/(i_train+1))
    writer.add_scalar('Per epoch training loss',per_epoch_train_loss/(i_train+1),i)
    end_train_time=time.time()
    print('time cost per training epoch',end_train_time-start_train_time,'s')

    #test mode
    #test per two epoch
    if i %2 ==0:
        s=time.time()
        myModel.eval()
        per_epoch_test_loss = 0  # record average loss for one round
        per_epoch_test_accuracy=0
        with torch.no_grad():
            for i_test,(imgs,targets) in enumerate(test_dataloader):
                imgs=imgs.to(myDevice)
                targets=targets.to(myDevice)
                outputs=myModel(imgs)
                loss=loss_fn(outputs,targets)

                #calculate total loss
                per_epoch_test_loss=per_epoch_test_loss+loss.item()
                #calculate accuracy
                outputs=torch.sigmoid(outputs) #model output need sigmoid activation
                outputs[outputs>=0.5]=1
                outputs[outputs<0.5]=0
                per_epoch_test_accuracy=(outputs==targets).sum().item()/(512*512)+per_epoch_test_accuracy #accuracy of each image

        e=time.time()
        print('test time is ',e-s)
        #average loss
        print('per_epoch_test_loss is ',per_epoch_test_loss/(i_test+1))
        writer.add_scalar('Per epoch test loss', per_epoch_test_loss / (i_test + 1), i)
        #average accuracy
        print('per epoch test accuracy is ',per_epoch_test_accuracy/len(test_data))
        writer.add_scalar('Per epoch test accuracy',per_epoch_test_accuracy/len(test_data),i)



    #save_model
    torch.save(myModel.state_dict(),'../save_models/myModel{}.pth'.format(i))


writer.close()


