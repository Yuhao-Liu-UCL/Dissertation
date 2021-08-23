function directories=findfiles(dire,ext)  
%the directory you want to find files  
%extension name of the files you want to find  
  
% dire=[matlabroot,filesep,'bin\win32'];  
% ext='dll';  
  
%check if the input and output is valid  
if ~isdir(dire)  
    msgbox('The input isnot a valid directory','Warning','warn');  
    return  
else  
if nargin==1  
        ext='*';  
elseif nargin>2|nargin<1  
    msgbox('1 or 2 inputs are required','Warning','warn');  
    return  
end  
if nargout>1  
    msgbox('Too many output arguments','Warning','warn');  
    return  
end  
  
%containing the searching results  
D={};  
  
%create a txt file to save all the directory  
fout=fopen('direc.txt','w');  
  
%containing all the directories on the same class  
folder{1}=dire;  
flag=1; %1 when there are folders havenot be searched,0 otherwise  
while flag  
    currfolders=folder;  
    folder={};  
      
    for m=1:1:length(currfolders)  
        direc=currfolders{m};  
%         files=dir([direc,filesep,'*.',ext]);%当前目录下的ext文件  
files=dir([direc,filesep,ext]);%当前目录下的ext文件  
          
        %the number of *.ext files in the current searching folder  
        L=length(files);  
        num=length(D);  
        for i=1:1:L  
            temp=[direc,filesep,files(i).name];  
            fprintf(fout,'%s\n',temp);  
            D{num+1}=temp;  
            num=num+1;  
        end  
          
          
        allfiles=dir(direc);%当前目录所有文件及子目录  
        %the number of all the files in the current searching folder  
        L=length(allfiles);  
        %the number of folders to be searched on this class  
        k=length(folder);  
        for i=1:1:L  
            if allfiles(i).isdir&(~strcmp(allfiles(i).name,'.'))&~strcmp(allfiles(i).name,'..')  
                k=k+1;  
                folder{k}=[direc,filesep,allfiles(i).name];%将所有一级子目录的目录名保存下来  
            end  
        end  
    end  
      
    %if there are no folders that havenot searched yet,flag=0 so the loop  
    %will be ended 当没有目录可遍历时，则查找结束  
    if ~length(folder)  
        flag=0;  
    end  
end  
  
fclose(fout);  
  
if nargout==1  
    directories=D';  
end  
clear D fout folder flag currfolders m files L num temp allfiles k i direc  
  
end  
