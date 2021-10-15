import math, string, random, time, os,decimal,copy
from cmu_112_graphics import *
from PIL import ImageDraw, ImageFont
from PIL import Image #showing/saving/loading image files
import numpy as np #processing images as arrays and editing pixel values
from tkinter import filedialog #opening files

# contains individual functions that can be used by any layer instance

## Math Stuff ##

# functions from https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html#RecommendedFunctions
def roundHalfUp(d):
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))
def roundHalfDown(d):
    rounding = decimal.ROUND_HALF_DOWN
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

# self written
def slope(x1,y1,x2,y2):
    run=(x1-x2)
    if run==0:
        return 1
    return (y1-y2)/run
##

## Class For Each Individual Layer and All Editing Functions ##
class LayerFunctions(object):
    def __init__(self,height,width,editorHeightR,editorWidthR):
        # canvas parameters
        self.width,self.height= width,height
        self.canvasCX, self.canvasCY= self.width//2,self.height//2
        self.editorWidthR,self.editorHeightR= editorWidthR,editorHeightR
        self.imagePosCX,self.imagePosCY= self.width//2,self.height//2
        # image parameters
        self.scale= 2/3
        self.image = None 
        self.matrix= None
        self.ogImage=None
        self.ogMatrix= None
        self.editorAreaImage=None
        # other parameters
        self.mode= "noImage"
        self.crop= False
        self.currentShape= "None"


    
    # function from cmu_112_graphics.py file
    def scaleImage(image, scale, antialias=False):
        resample = Image.ANTIALIAS if antialias else Image.NEAREST
        return image.resize((round(image.width*scale), round(image.height*scale)), resample=resample)

    def loadImage(self):
        self.scale= 2/3
        # loads image using filedialog, learned from filedialog documentation:
        # https://pythonspot.com/tk-file-dialogs/
        imagePath= filedialog.askopenfilename(title ='Open Image') 
        if imagePath != "":
            loadedImage= Image.open(imagePath)
            # changes scale based on size of image and then scales image within canvas
            if loadedImage.width>self.width:
                self.scale= (1/(loadedImage.width/self.width))*self.scale
            if loadedImage.height>self.height:
                self.scale= (1/(loadedImage.height/self.height))*self.scale
            
            self.image= LayerFunctions.scaleImage(loadedImage,self.scale)
            
            # np transformations learned from numpy documentation https://numpy.org/doc/stable/index.html
            self.matrix= np.array(self.image)
            # adding alpha channel for uniformity
            if self.matrix.shape[2]==3:
                self.matrix = np.insert(self.matrix, 3 , 255, axis= 2)

            self.image= Image.fromarray(self.matrix)
            self.ogImage= self.image
            self.ogMatrix=self.matrix
            self.shapesImage= self.image
            self.editorAreaImage= self.image

            return LayerFunctions.ImageMatrix(self)


    # crops image to stay within set editor area bounds (for zooming)
    def ImageMatrix(self):
        self.matrix= np.array(self.image)
        imageCX,imageCY= self.image.width//2,self.image.height//2
        editorImageWidth,editorImageHeightR= min(self.editorWidthR,imageCX),min(self.editorHeightR,imageCY)        
        editorAreaMatrix= self.matrix[imageCY-editorImageHeightR:imageCY+editorImageHeightR,
                                        imageCX-editorImageWidth:imageCX+editorImageWidth,:]
        self.editorAreaImage= Image.fromarray(editorAreaMatrix)
        return self.editorAreaImage

    # allows for dragging of current layer (repositioning on canvas)
    def move(self,mouseDragBounds):
        self.imagePosCX,self.imagePosCY= mouseDragBounds[-1][0],mouseDragBounds[-1][1]
        return LayerFunctions.ImageMatrix(self)

    # rgb values from user input 
    # color channel manipulation learned from https://note.nkmk.me/en/python-numpy-image-processing/
    def colorFilter(self,color):
        for i in range(3):
            color_channel= self.ogMatrix[:,:,i]
            color_channel=color_channel.astype("float64") #--> to change datatype https://numpy.org/doc/stable/reference/generated/numpy.ndarray.astype.html
            colorVal= color[i]/255
            color_channel*=colorVal
            self.matrix[:,:,i]=color_channel[:,:]
            self.image= Image.fromarray(self.matrix)
        return LayerFunctions.ImageMatrix(self)

    # zooms in or out of image based on scale
    def zoom(self):
        cx,cy=self.imagePosCX,self.imagePosCY
        self.image= LayerFunctions.scaleImage(self.ogImage,self.scale)
        self.imagePosCX,self.imagePosCY=cx,cy
        return LayerFunctions.ImageMatrix(self)


    # @inprogress, rotates current layer
    # https://numpy.org/doc/stable/reference/generated/numpy.rot90.html
    def rotate(self):
        cx,cy=self.imagePosCX,self.imagePosCY
        self.matrix= np.rot90(self.matrix)
        self.image= Image.fromarray(self.matrix)
        self.ogImage=self.image
        self.imagePosCX,self.imagePosCY=cx,cy
        return self.image

    # https://numpy.org/doc/stable/reference/generated/numpy.rot90.html
    def flip(self,axis):
        self.matrix= np.flip(self.matrix,axis)
        self.image= Image.fromarray(self.matrix)
        return self.image


    # lasso crop tool using mouseDragged positions
    def lassoCrop(self,mouseDragBounds):
        if self.mode== "lasso":
            mouseYPositions= dict()
            lowesty, highesty= mouseDragBounds[0][1],mouseDragBounds[0][1]
            for x,y in mouseDragBounds:
                if x> self.imagePosCX + self.matrix.shape[1]//2:
                    x= self.imagePosCX + self.matrix.shape[1]//2
                if x< self.imagePosCX - self.matrix.shape[1]//2:
                    x= self.imagePosCX - self.matrix.shape[1]//2

                if y<lowesty: lowesty=y
                elif y>highesty: highesty=y

                if y not in mouseYPositions: 
                    mouseYPositions[y]= [x,x]
                else:
                    if x < mouseYPositions[y][0]:
                        mouseYPositions[y][0]=x
                    if x > mouseYPositions[y][1]:
                        mouseYPositions[y][1]=x

            if highesty> self.imagePosCY + self.matrix.shape[0]//2:
                highesty= self.imagePosCY + self.matrix.shape[0]//2
            if lowesty< self.imagePosCY - self.matrix.shape[0]//2:
                lowesty= self.imagePosCY - self.matrix.shape[0]//2

            for pos in range(lowesty,highesty+1):
                if pos in mouseYPositions and mouseYPositions[pos][0]==mouseYPositions[pos][1]:
                    mouseYPositions.pop(pos)

            for pos in range(highesty,lowesty,-1): 
                if pos not in mouseYPositions:
                    prevY= pos-1    
                    while prevY not in mouseYPositions:
                        prevY-=1
                    nextY= pos+1
                    while nextY not in mouseYPositions:
                        nextY+=1
                    prevLowerX= mouseYPositions[prevY][0]
                    nextLowerX= mouseYPositions[nextY][0]
                    prevHigherX= mouseYPositions[prevY][1]
                    nextHigherX= mouseYPositions[nextY][1]
                    
                    lowerSlope= slope(prevLowerX,prevY,nextLowerX,nextY)
                    higherSlope= slope(prevHigherX,prevY,nextHigherX,nextY)

                    mouseYPositions[pos]=[0,0]
                    mouseYPositions[pos][0]=prevLowerX+lowerSlope
                    mouseYPositions[pos][1]=prevHigherX+higherSlope


            cropMat=np.zeros(self.matrix.shape, dtype='uint8')
            for level in range(highesty,lowesty,-1):
                lowestX= roundHalfDown(mouseYPositions[level][0]- abs(self.canvasCX-self.image.width//2))
                highestX= roundHalfUp(mouseYPositions[level][1]- abs(self.canvasCX-self.image.width//2))
                level-=abs(self.canvasCY-self.image.height//2)
                cropMat[level,lowestX:highestX,:]= self.matrix[level,lowestX:highestX,:]

            self.matrix= cropMat
            self.ogMatrix=self.matrix
            self.ogImage= Image.fromarray(self.ogMatrix)
            self.image=self.ogImage
            self.editorAreaImage=self.image
            return self.matrix

    
    
    #rectangluar crop based on endpoints of mousedrag
    def rectCrop(self,mouseDragBounds):
        if self.mode== "rect":
            # endpoints of mousedrag
            upperCX,upperCY= mouseDragBounds[0]
            lowerCX,lowerCY= mouseDragBounds[-1] 
            # matrix center and corners
            MatCX,MatCY= self.matrix.shape[1]//2,self.matrix.shape[0]//2   
            upperMatX,upperMatY= 0,0
            lowerMatX,lowerMatY= self.matrix.shape[1],self.matrix.shape[0]
            # crop parameters automatically set to image canvas endpoint positions
            upperImageX,upperImageY= self.imagePosCX-MatCX,self.imagePosCY-MatCY
            lowerImageX,lowerImageY= self.imagePosCX+MatCX,self.imagePosCY+MatCX
            # checks bounds of mousedrag to make sure within matrix, sets crop paramters
                # matrix_bound_point= matrix_center_point - (distance from center of image to mousedrag points)
            if upperImageX<upperCX<lowerImageX:
                upperMatX= MatCX - abs(self.imagePosCX-upperCX)
            if upperImageX<lowerCX<lowerImageX:
                lowerMatX= MatCX + abs(self.imagePosCX-lowerCX)
            if upperImageY<upperCY<lowerImageY:
                upperMatY= MatCY - abs(self.imagePosCY-upperCY)
            if upperImageY<lowerCY<lowerImageY:
                lowerMatY= MatCY + abs(self.imagePosCY-lowerCY)
            print(self.crop)
            if self.crop== True:
            # matrix sliced w/ new bounds and set to image
                self.matrix= self.matrix[upperMatY:lowerMatY,upperMatX:lowerMatX,:]
                self.image=Image.fromarray(self.matrix)
                self.ogMatrix=self.matrix
                self.ogImage= Image.fromarray(self.ogMatrix)
                return self.matrix
            else:
                emptyMat= np.zeros(self.matrix.shape, dtype='uint8')
                newMat= copy.deepcopy(self.matrix[upperMatY:lowerMatY,upperMatX:lowerMatX,:])
                newImg= Image.fromarray(newMat)
                self.matrix[upperMatY:lowerMatY,upperMatX:lowerMatX,:]= emptyMat[upperMatY:lowerMatY,upperMatX:lowerMatX,:]
                self.image=Image.fromarray(self.matrix)
                self.editorAreaImage=self.image
                self.ogMatrix=self.matrix
                self.ogImage= Image.fromarray(self.ogMatrix)
                return newMat


            