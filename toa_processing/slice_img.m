bio_dir=findfiles('C:\Users\LYH\Desktop\dissertation\Landsat8\landsat8_train','LC8*');

for i = 1:80
    fprintf('%s\n',bio_dir{i})
    cd(bio_dir{i})

norMTL=dir('L*MTL.txt');
existMTL=size(norMTL);

if existMTL(1)==0
    fprintf('No L*MTL.txt header in the current folder!\n');
    return;
else 
    filename=norMTL.name;
end
% open and read hdr file
fprintf('Read in header information & TIF images\n');
[Lmax,Lmin,Qcalmax,Qcalmin,Refmax,Refmin,ijdim_ref,ijdim_thm,reso_ref,...
    reso_thm,ul,zen,azi,zc,Lnum,doy]=lndhdrread(filename);
Tab_ES_Dist=getES_Dist();
%toa
 % LPGS Upper lef corner alignment (see Landsat handbook for detail)
    ul(1)=ul(1)-15;
    ul(2)=ul(2)+15;
    resolu=[reso_ref,reso_ref];
    % Read in all bands
    n_B1=dir('*B1.TIF');
    im_B1=single(imread(n_B1.name));
    n_B2=dir('*B2*');
    im_B2=single(imread(n_B2.name));
    n_B3=dir('*B3*');
    im_B3=single(imread(n_B3.name));
    n_B4=dir('*B4*');
    im_B4=single(imread(n_B4.name));
    n_B5=dir('*B5*');
    im_B5=single(imread(n_B5.name));
    n_B6=dir('*B6*');
    im_B6=single(imread(n_B6.name));
    n_B7=dir('*B7*');
    im_B7=single(imread(n_B7.name));
    n_B8=dir('*B8*');
    im_B8=single(imread(n_B8.name));
    n_B9=dir('*B9*');
    im_B9=single(imread(n_B9.name));
    
    % check to see whether need to resample thermal band
    if reso_ref~=reso_thm
        % resmaple thermal band
        im_B8=pixel2pixv([ul(2),ul(1)],[ul(2),ul(1)],...
            resolu,[reso_thm,reso_thm],...
            im_B8,[ijdim_ref(2),ijdim_ref(1)],[ijdim_thm(2),ijdim_thm(1)]);
    end
    id_missing=im_B2==0|im_B3==0|im_B4==0|im_B5==0|im_B6==0|im_B7==0|im_B9==0|im_B8==0|im_B1==0;
    % ND to TOA reflectance with 0.0001 scale_facor
    fprintf('From DNs to TOA ref & BT\n');
    im_B1=((Refmax(1)-Refmin(1))/(Qcalmax(1)-Qcalmin(1)))*(im_B1-Qcalmin(1))+Refmin(1);
    im_B2=((Refmax(2)-Refmin(2))/(Qcalmax(2)-Qcalmin(2)))*(im_B2-Qcalmin(2))+Refmin(2);
    im_B3=((Refmax(3)-Refmin(3))/(Qcalmax(3)-Qcalmin(3)))*(im_B3-Qcalmin(3))+Refmin(3);
    im_B4=((Refmax(4)-Refmin(4))/(Qcalmax(4)-Qcalmin(4)))*(im_B4-Qcalmin(4))+Refmin(4);
    im_B5=((Refmax(5)-Refmin(5))/(Qcalmax(5)-Qcalmin(5)))*(im_B5-Qcalmin(5))+Refmin(5);
    im_B6=((Refmax(6)-Refmin(6))/(Qcalmax(6)-Qcalmin(6)))*(im_B6-Qcalmin(6))+Refmin(6);
    im_B7=((Refmax(7)-Refmin(7))/(Qcalmax(7)-Qcalmin(7)))*(im_B7-Qcalmin(7))+Refmin(7);
    im_B8=((Refmax(8)-Refmin(8))/(Qcalmax(8)-Qcalmin(8)))*(im_B8-Qcalmin(8))+Refmin(8);
    im_B9=((Refmax(9)-Refmin(9))/(Qcalmax(9)-Qcalmin(9)))*(im_B9-Qcalmin(9))+Refmin(9);
    
    % with a correction for the sun angle
   s_zen=deg2rad(zen);
   im_B1=im_B1/cos(s_zen);
    im_B2=im_B2/cos(s_zen);
    im_B3=im_B3/cos(s_zen);
    im_B4=im_B4/cos(s_zen);
    im_B5=im_B5/cos(s_zen);
    im_B6=im_B6/cos(s_zen);
    im_B7=im_B7/cos(s_zen);
    im_B8=im_B8/cos(s_zen);
    im_B9=im_B9/cos(s_zen);
    
     % get data ready for Fmask
    TOAref=zeros(ijdim_ref(1),ijdim_ref(2),9,'single');% Band 1,2,3,4,5,6,7,8 9
    im_B1(id_missing)=0;
    im_B2(id_missing)=0;
    im_B3(id_missing)=0;
    im_B4(id_missing)=0;
    im_B5(id_missing)=0;
    im_B6(id_missing)=0;
    im_B7(id_missing)=0;
    im_B9(id_missing)=0;
    
    TOAref(:,:,1)=im_B1;
    TOAref(:,:,2)=im_B2;
    TOAref(:,:,3)=im_B3;
    TOAref(:,:,4)=im_B4;
    TOAref(:,:,5)=im_B5;
    TOAref(:,:,6)=im_B6;
    TOAref(:,:,7)=im_B7;
    TOAref(:,:,8)=im_B8;
    TOAref(:,:,9)=im_B9;
    
    n_fmask_img=dir('*MTLFmask');
    n_fmask_hdr=dir('*MTLFmask.hdr');
    n_targets=dir('*fixedmask.img');
    fmask=multibandread(n_fmask_img.name,[ijdim_ref 1],'uint8',0,'bsq','ieee-le');
    targets_img=multibandread(n_targets.name,[ijdim_ref 1],'uint8',0,'bsq','ieee-le');
    
    %output target
    targets_img(targets_img==192)=255;
    targets_img(targets_img~=255)=0;
    targets_img(targets_img==255)=1;
    
    enviwrite('target',targets_img,'uint8',resolu,ul,'bsq',zc);
    
    zeros_toa=zeros(512);
    zeros_target=zeros(512);
    zeros_fmask=zeros(512);
    
    for i=1:floor(ijdim_ref(1)/512)
        for j =1:floor(ijdim_ref(2)/512)
            zeros_fmask=fmask((i*512-511):i*512,(j*512-511):j*512);
            if sum(sum(zeros_fmask==64))>209715
                continue;
            end
            zeros_target=targets_img((i*512-511):i*512,(j*512-511):j*512);
            zeros_toa=TOAref((i*512-511):i*512,(j*512-511):j*512,:);
            targetfilename=[filename(1:end-8) '_target_' int2str(i) '_' int2str(j)];
            toafilename=[filename(1:end-8) '_toa_' int2str(i) '_' int2str(j)];
            fmaskfilename=[filename(1:end-8) '_fmask_' int2str(i) '_' int2str(j)];
            img_path='C:\Users\LYH\Desktop\dissertation\landsat8_tt\train\img\';
            target_path='C:\Users\LYH\Desktop\dissertation\landsat8_tt\train\target\';
            fmask_path='C:\Users\LYH\Desktop\dissertation\landsat8_tt\train\fmask\';
            enviwrite([fmask_path fmaskfilename],zeros_fmask,'uint8',resolu,ul,'bsq',zc);
            enviwrite([target_path targetfilename],zeros_target,'uint8',resolu,ul,'bsq',zc);
            enviwrite([img_path toafilename],zeros_toa,'single',resolu,ul,'bsq',zc);
            
            
        end
    end
        
  fprintf('write done')
    
    
    
    
    
    

    
end