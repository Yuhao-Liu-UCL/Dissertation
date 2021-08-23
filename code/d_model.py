import torch
from torch import nn

class CBRR(nn.Module):
    def __init__(self,c_in_ch=64,c_padding=1,c_dila=1,c_eps=1e-05, c_momentum=0.1):
        super(CBRR, self).__init__()
        #cbr1 for the difference of input channel.
        #cbr2 is the normal convolution operation,BN and Relu activation
        self.cbr1=nn.Sequential(nn.Conv2d(in_channels=c_in_ch, out_channels=64, kernel_size=3, padding=c_padding, dilation=c_dila),
                                nn.BatchNorm2d(64, eps=c_eps,momentum=c_momentum),
                                nn.ReLU(inplace=True))  # channel of input should be specified.
        self.cbr2=nn.Sequential(nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=c_padding, dilation=c_dila),
                                nn.BatchNorm2d(64, eps=c_eps,momentum=c_momentum),
                                nn.ReLU(inplace=True))

    def forward(self,x):
        # residual construction
        x=self.cbr1(x)
        out=self.cbr2(x)
        out=self.cbr2(out)
        out=out+x
        return out



class D_model(nn.Module):
    def __init__(self,d_input_channel):
        super(D_model, self).__init__()
        # equivalent to a bp neural network with 32 hidden perceptron
        # 9  -----  32 ------1

        self.spectral_ex=nn.Sequential(
            nn.Conv2d(in_channels=d_input_channel,out_channels=32,kernel_size=1),
            nn.Sigmoid(),
            nn.Conv2d(in_channels=32,out_channels=1,kernel_size=1),
            nn.Sigmoid()
        )
        #first cbrr receive input
        self.cbrr1=CBRR(d_input_channel)
        #general cbrr
        self.cbrr_nolmal=CBRR()
        self.maxpooling=nn.MaxPool2d(2)
        self.cbrr_dilate2=CBRR(c_padding=2,c_dila=2)
        self.cbrr_dilate4=CBRR(c_padding=4,c_dila=4)
        #fusion convolution
        self.fconv=nn.Conv2d(in_channels=64,out_channels=1,kernel_size=3,padding=1)
        #general deconvolution 2x
        self.deconv=nn.ConvTranspose2d(in_channels=64,out_channels=64,kernel_size=4,stride=2,padding=1,bias=False)

        #fusion deconvolution
        self.fdeconv2x=nn.ConvTranspose2d(in_channels=1,out_channels=1,kernel_size=4,stride=2,padding=1,bias=False)
        self.fdeconv4x=nn.ConvTranspose2d(in_channels=1,out_channels=1,stride=4,padding=2,kernel_size=8,bias=False)
        self.fdeconv8x=nn.ConvTranspose2d(in_channels=1,out_channels=1,stride=8,padding=4,kernel_size=16,bias=False)
        # different scales fusion
        self.ffuse=nn.Sequential(
            nn.Conv2d(in_channels=6,out_channels=1,kernel_size=3,padding=1),
            nn.ReLU(inplace=True)
        )
        #two models combination
        self.linearcombi_active=nn.Sequential(
            nn.Conv2d(in_channels=2,out_channels=1,kernel_size=1),
            #activation function is included in BCEwithlogitsloss
        )


    def forward(self,input):
        #extraction of spectral features
        spectral=self.spectral_ex(input)

        #extration of multi-scale features

        down_512=self.cbrr1(input)

        x=self.maxpooling(down_512)
        down_256=self.cbrr_nolmal(x)

        x=self.maxpooling(down_256)
        down_128=self.cbrr_nolmal(x)

        x=self.maxpooling(down_128)
        down_64_1=self.cbrr_nolmal(x)

        down_64_2=self.cbrr_dilate2(down_64_1)
        down_64_3=self.cbrr_dilate4(down_64_2)

        #upsample processing

        up_64_1=self.cbrr_dilate4(down_64_3)+down_64_3
        up_64_2=self.cbrr_dilate2(up_64_1)+down_64_2
        up_64_3= self.cbrr_nolmal(up_64_2) + down_64_1

        x=self.deconv(up_64_3)
        up_128=self.cbrr_nolmal(x)+down_128

        x=self.deconv(up_128)
        up_256=self.cbrr_nolmal(x)+down_256

        x=self.deconv(up_256)
        up_512=self.cbrr_nolmal(x)+down_512


        #convolution and deconvolution from 64 channels to 1*512*512
        up_512=self.fconv(up_512)
        up_256=self.fdeconv2x(self.fconv(up_256))
        up_128=self.fdeconv4x(self.fconv(up_128))
        up_64_3=self.fdeconv8x(self.fconv(up_64_3))
        up_64_2 = self.fdeconv8x(self.fconv(up_64_2))
        up_64_1 = self.fdeconv8x(self.fconv(up_64_1))

        foutput=torch.cat((up_64_1,up_64_2,up_64_3,up_128,up_256,up_512),1) #6*512*512
        foutput=self.ffuse(foutput) #1*512*512

        # combination of spectral features and multi-scale features 2*512*512
        model_output=torch.cat((spectral,foutput),1)

        #leaner combination and sigmo activation
        model_output =self.linearcombi_active(model_output)



        return model_output


if __name__ == "__main__" :
    model=D_model(9)

    x=torch.randn((1,9,512,512))
    out=model(x)

    print(out.shape)






