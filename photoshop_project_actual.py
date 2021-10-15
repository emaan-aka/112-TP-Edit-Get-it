# 112 Term Project: Photoshop
import math, string, random, time, os, decimal
from cmu_112_graphics import *
from PIL import ImageDraw, ImageFont
from PIL import Image #showing/saving/loading image files
import numpy as np #processing images as arrays and editing pixel values
from tkinter import filedialog
from tp_functions import *
import tkinter.colorchooser

# main file to run, displays interactive tool in canvas

def distance(pos1,pos2):
    x1,y1=pos1
    x2,y2=pos2
    return ((x1-x2)**2+(y1-y2)**2)**0.5

# from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'


## Photoshop Tool WorkSpace Display & Event Control
class workSpace(App):
    
    # all available functions per layer
    editorHeightR,editorWidthR= 275,300
    allLayers= []
    currentLayer= LayerFunctions(800,1000,editorHeightR,editorWidthR)
    currlayernum= 0
    allLayers.append(currentLayer)
    editorAreaImage= currentLayer.editorAreaImage
    Img_PosCX, Img_PosCY= currentLayer.imagePosCX,currentLayer.imagePosCY
    canvasCX,canvasCY= 0,0
    

    def appStarted(self):
        self.mouseMovedDelay= 1

        self.canvasCX,self.canvasCY= self.width//2,self.height//2
        workSpace.canvasCX,workSpace.canvasCY= self.canvasCX,self.canvasCY

        #  mode stuff
        self.shapes= []
        
        
        # shape input stuff
        self.currColor=("black",(0,0,0))
        self.text=None
        self.font= None

        # mouse stuff
        self.mouseDragBounds=[]
        self.timerDelay=1

        # creates all buttons
        workSpace.configButtons(self)

    def mousePressed(self,event):
        workSpace.configButtons(self)
        for button in MenuButton.allButtons.values():
            MenuButton.buttonFunction(button,event.x,event.y)

    # test buttons
    @staticmethod
    def loadImage():
        workSpace.currentLayer.editorAreaImage= LayerFunctions.loadImage(workSpace.currentLayer)
        workSpace.currentLayer.mode= "editingImage"
        workSpace.allLayersMatrix()
    @staticmethod
    def saveImage():
        workSpace.allLayersMatrix()
        if workSpace.editorAreaImage==None:
            print("Please Upload a File to Save")
        else:
            ImageSavePath= filedialog.asksaveasfilename(title = "Save Image",filetypes = (("png files","*.png"),("jpeg files","*.jpeg"),("all files","*.*")))
            if ImageSavePath != "":
                print(ImageSavePath)
                
                if (".jpg" or ".jpeg") in ImageSavePath:
                    workSpace.editorAreaImage= workSpace.editorAreaImage.convert("RGB")
                workSpace.editorAreaImage.save(ImageSavePath)
    @staticmethod
    def zoomIn():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.scale+=1/10
            workSpace.currentLayer.editorAreaImage= LayerFunctions.zoom(workSpace.currentLayer)
            workSpace.allLayersMatrix()
    @staticmethod
    def zoomOut():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.scale-=1/10
            if workSpace.currentLayer.scale<0.1:
                workSpace.currentLayer.scale=0.1
            workSpace.currentLayer.editorAreaImage= LayerFunctions.zoom(workSpace.currentLayer)
            workSpace.allLayersMatrix()
    @staticmethod
    def rotateImage():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.editorAreaImage= LayerFunctions.rotate(workSpace.currentLayer)
            workSpace.allLayersMatrix()

    @staticmethod
    def flipImage():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.editorAreaImage= LayerFunctions.flip(workSpace.currentLayer,1)
            workSpace.allLayersMatrix()

    @staticmethod
    def lassoCropImage():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.mode= "lasso"
    @staticmethod
    def rectangularCropImage():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.crop=True
            workSpace.currentLayer.mode= "rect"

    @staticmethod
    def rectangularSelect():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.crop=False
            workSpace.currentLayer.mode= "rect"
    
    def colorFilter(self):
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            color= self.currColor[1]
            workSpace.currentLayer.editorAreaImage= LayerFunctions.colorFilter(workSpace.currentLayer,color)
            workSpace.allLayersMatrix()
        
    @staticmethod
    def setCurrentLayer():
        prevlayernum= workSpace.currlayernum
        workSpace.currlayernum= prevlayernum+1
        if len(workSpace.allLayers)-1<workSpace.currlayernum:
            workSpace.currlayernum=0
        workSpace.currentLayer= workSpace.allLayers[workSpace.currlayernum]
        
    @staticmethod
    def allLayersMatrix():
        ImageMat= np.zeros((2*workSpace.editorHeightR,2*workSpace.editorWidthR,4),dtype="uint8")
        for layer in workSpace.allLayers:
            if layer.editorAreaImage!= None:

                newImg= layer.editorAreaImage
                newMat= np.array(newImg)
                XdistToLeftEdge= abs(workSpace.canvasCX-workSpace.editorWidthR)
                YdistToLeftEdge= abs(workSpace.canvasCY-workSpace.editorHeightR)
                newStartY= layer.imagePosCY-newMat.shape[0]//2 - YdistToLeftEdge
                newStartX=layer.imagePosCX-newMat.shape[1]//2 - XdistToLeftEdge
                newEndY= newStartY+newMat.shape[0]
                newEndX=newStartX+newMat.shape[1]

                
                matStartY= 0
                matStartX= 0
                matEndY= newMat.shape[0]
                matEndX=newMat.shape[1]
                
                if newEndY>2*workSpace.editorHeightR:
                    matEndY-= newEndY-2*workSpace.editorHeightR
                    newEndY= 2*workSpace.editorHeightR
                if newStartY<0:
                    matStartY+=  -(newStartY) 
                    newStartY=0
                if newEndX>2*workSpace.editorWidthR:
                    matEndX-= newEndX - 2*workSpace.editorWidthR
                    newEndX=2*workSpace.editorWidthR
                if newStartX<0:
                    matStartX+=  -(newStartX)
                    newStartX=0

                if ((newEndY<=0 and newStartY<=0) or (newEndY>=2*workSpace.editorHeightR and newStartY>=2*workSpace.editorHeightR) or
                    (newEndX<=0 and newStartX<=0) or (newEndX>=2*workSpace.editorHeightR and newStartX>=2*workSpace.editorHeightR)):
                    ImageMat= np.zeros(newMat.shape,dtype="uint8")

                else:
                    ImageMat[newStartY:newEndY,newStartX:newEndX,:]= newMat[matStartY:matEndY,matStartX:matEndX,:]
                # layer.editorAreaImage= Image.fromarray(ImageMat)
                workSpace.editorAreaImage= Image.fromarray(ImageMat)
                
                

    @staticmethod
    def newLayer():
        workSpace.currlayernum= len(workSpace.allLayers)
        workSpace.allLayers.append(LayerFunctions(800,1000,workSpace.editorHeightR,workSpace.editorWidthR))
        workSpace.currentLayer= workSpace.allLayers[workSpace.currlayernum]
        workSpace.Img_PosCX, workSpace.Img_PosCY= workSpace.currentLayer.imagePosCX,workSpace.currentLayer.imagePosCY

    @staticmethod
    def dragLayer():
        if workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            workSpace.currentLayer.mode="move"
            workSpace.allLayersMatrix()

    # from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#ioMethods
    def text(self):
        workSpace.currentLayer.mode= "drawing"
        workSpace.currentLayer.currentShape= "text"
        self.font= []

        fontName= self.getUserInput("Enter Font Name")
        if fontName == "":
            fontName="Arial"
        else:
            try:
                fontFile= ImageFont.truetype(f'Pillow/Tests/fonts/{fontName}.ttf', 5)
            except:
                print("Please use a PIL compatible font name, such as 'Arial','Verdana','Georgia','Zapfino', or 'AppleGothic'." )
                workSpace.text(self)
                return
        
        fontSize= self.getUserInput("Enter Font Size")
        if fontSize=="":
            fontSize=15
        else:
            try:
                sizeInt= int(fontSize)
            except:
                print("Please enter an integer.")
                workSpace.text(self)
                return
        
        self.font.append(f"{fontName} {fontSize}")
        fontFile= ImageFont.truetype(f'Pillow/Tests/fonts/{fontName}.ttf', int(fontSize))
        self.font.append(fontFile)
        
        self.text=None
        text= self.getUserInput("Enter Text")
        if text=="":
            self.text="hewwo :3"
        elif text != None:
            self.text= text
        

    @staticmethod
    def rectangle():
        workSpace.currentLayer.mode= "drawing"
        workSpace.currentLayer.currentShape= "rectangle"

    @staticmethod
    def line():
        workSpace.currentLayer.mode= "drawing"
        workSpace.currentLayer.currentShape= "line"

    @staticmethod
    def oval():
        workSpace.currentLayer.mode= "drawing"
        workSpace.currentLayer.currentShape= "oval"


    # colorchooser implementation learned from https://docs.python.org/3/library/tkinter.colorchooser.html
    def pickColor(self):
        color= tkinter.colorchooser.askcolor()
        actualColor= []
        for val in color[0]:
            actualColor+= [int(val)]
        tupColor= (actualColor[0],actualColor[1],actualColor[2])
        colorWord= rgbString(actualColor[0],actualColor[1],actualColor[2])
        self.currColor= (colorWord,tupColor)

    # PIL ImageDraw functions learned from https://pillow.readthedocs.io/en/stable/_modules/PIL/ImageDraw.html#ImageDraw.bitmap
    def shapeDrawer(self,canvas):
        if workSpace.currentLayer.mode == 'drawing' and workSpace.currentLayer.editorAreaImage!=None and self.shapes!=[]:
            shapeDraw= ImageDraw.Draw(workSpace.currentLayer.editorAreaImage)
            topCX,topCY= (self.width - workSpace.currentLayer.editorAreaImage.width)/2,(self.height-workSpace.currentLayer.editorAreaImage.height)/2
            for shape in self.shapes:
                upperShapePos,lowerShapePos,color,timing,text,font= shape[1][0],shape[1][-1],shape[2],shape[3],shape[4],shape[5]
                if timing=="while_drag":
                    if shape[0]=="rectangle":
                        canvas.create_rectangle(upperShapePos[0],upperShapePos[1],
                                                lowerShapePos[0],lowerShapePos[1],width=0,fill=color[0])
                    elif shape[0]=="oval":
                        canvas.create_oval(upperShapePos[0],upperShapePos[1],
                                        lowerShapePos[0],lowerShapePos[1],width=0,fill=color[0])
                    elif shape[0]=="line":
                        canvas.create_line(upperShapePos[0],upperShapePos[1],
                                            lowerShapePos[0],lowerShapePos[1],width=0,fill=color[0])
                    elif shape[0]=="text" and (text!=None):
                        canvas.create_text(lowerShapePos[0],lowerShapePos[1],text=text,fill=color[0],font=font[0])
                   
                    workSpace.allLayersMatrix()
                if timing=="on_release":
                    if shape[0]=="rectangle":
                        shapeDraw.rectangle((upperShapePos[0]-topCX,upperShapePos[1]-topCY,
                                            lowerShapePos[0]-topCX,lowerShapePos[1]-topCY),fill=color[1]) 
                    elif shape[0]=="line":
                        shapeDraw.line((upperShapePos[0]-topCX,upperShapePos[1]-topCY,
                                            lowerShapePos[0]-topCX,lowerShapePos[1]-topCY),fill=color[1])
                        
                    elif shape[0]=="oval":
                        shapeDraw.ellipse((upperShapePos[0]-topCX,upperShapePos[1]-topCY,
                                        lowerShapePos[0]-topCX,lowerShapePos[1]-topCY),fill=color[1])

                    elif shape[0]=="text" and (text!=None):
                        shapeDraw.text((lowerShapePos[0]-topCX,
                                        lowerShapePos[1]-topCY),text=text,fill=color[1],font=font[1])
                        
                    workSpace.allLayersMatrix()

        

    @staticmethod
    def deleteLayer():
        if len(workSpace.allLayers)>2:
            workSpace.allLayers.pop()
            workSpace.currlayernum-=1
            if workSpace.currlayernum<0:
                workSpace.currlayernum=0
                workSpace.currentLayer=workSpace.allLayers[-1]
            else:
                workSpace.currentLayer= workSpace.allLayers[workSpace.currlayernum]

    def keyPressed(self,event):
        if event.key=='u':
            workSpace.loadImage()
        elif event.key=="c":
            workSpace.pickColor(self)
        elif event.key=="e":
            workSpace.deleteLayer()
        if workSpace.currentLayer.mode != "noImage":
            if event.key=='s':
                workSpace.saveImage()
            elif event.key=='n':
                workSpace.newLayer()
            elif event.key=='t':
                workSpace.setCurrentLayer()
            elif event.key=='r':
                workSpace.rotateImage()
            elif event.key=='f':
                workSpace. flipImage()
            elif event.key=="Up":
                workSpace.zoomIn()
            elif event.key=="Down":
                workSpace.zoomOut()
            elif event.key=='l':
                workSpace.lassoCropImage()
            elif event.key=='g':
                workSpace.currentLayer.crop=True
                workSpace.rectangularCropImage()
            elif event.key=="b":
                workSpace.currentLayer.crop=False
                workSpace.rectangularSelect()
            elif event.key=='m':
                workSpace.dragLayer()
            elif event.key=='d':
                workSpace.currentLayer.mode="drawing"



    def mouseDragged(self,event):
        self.mouseDragBounds.append((event.x,event.y))
        if self.mouseDragBounds!=[] and workSpace.editorAreaImage!=None:
            if workSpace.currentLayer.mode=="move" and len(self.mouseDragBounds)>1:
                workSpace.currentLayer.editorAreaImage= LayerFunctions.move(workSpace.currentLayer,self.mouseDragBounds)
                workSpace.allLayersMatrix()
            elif workSpace.currentLayer.mode=="drawing":
                shape= workSpace.currentLayer.currentShape
                self.shapes.append((shape,self.mouseDragBounds,self.currColor,"while_drag",self.text,self.font))
            
        

    def mouseReleased(self,event):
        if self.mouseDragBounds!=[] and workSpace.currentLayer.mode != "noImage" and workSpace.currentLayer.editorAreaImage!=None:
            if workSpace.currentLayer.mode=="lasso":
                if distance(self.mouseDragBounds[0],self.mouseDragBounds[-1])<20 and len(self.mouseDragBounds)>1:
                    cropMatrix= LayerFunctions.lassoCrop(workSpace.currentLayer,self.mouseDragBounds)
                    workSpace.currentLayer.editorAreaImage= Image.fromarray(cropMatrix)
                    workSpace.allLayersMatrix()
            elif workSpace.currentLayer.mode=="rect" and len(self.mouseDragBounds)>1:
                if workSpace.currentLayer.crop==True:
                    cropMatrix= LayerFunctions.rectCrop(workSpace.currentLayer,self.mouseDragBounds)
                    workSpace.currentLayer.editorAreaImage= Image.fromarray(cropMatrix)
                    workSpace.allLayersMatrix()
                else:
                    newMat= LayerFunctions.rectCrop(workSpace.currentLayer,self.mouseDragBounds)
                    newImg= Image.fromarray(newMat)
                    newLayer= LayerFunctions(800,1000,self.editorHeightR,self.editorWidthR)
                    newLayer.mode= "editingImage"
                    newLayer.image= newImg
                    newLayer.ogImage=newImg
                    newLayer.editorAreaImage= newImg
                    newLayer.matrix= newMat
                    newLayer.ogMatrix= newMat
                    workSpace.currlayernum= len(workSpace.allLayers)
                    workSpace.allLayers.append(newLayer)
                    workSpace.currentLayer= workSpace.allLayers[workSpace.currlayernum]
                    workSpace.currentLayer.imagePosCX,workSpace.currentLayer.imagePosCY= self.canvasCX,self.canvasCY
                    workSpace.allLayersMatrix()
            elif workSpace.currentLayer.mode=="drawing":
                shape= workSpace.currentLayer.currentShape
                self.shapes.append((shape,self.mouseDragBounds,self.currColor,"on_release",self.text,self.font))
            self.mouseDragBounds=[]

    def UIdrawer(self,canvas):
        # covering editor bounds
        canvas.create_rectangle(0,0,self.width,self.canvasCY-workSpace.editorHeightR,fill=rgbString(55,55,55),width=0)
        canvas.create_rectangle(0,0,self.canvasCX-workSpace.editorWidthR,self.height,fill=rgbString(55,55,55),width=0)
        canvas.create_rectangle(0,self.canvasCY+workSpace.editorHeightR,self.width,self.height,fill=rgbString(55,55,55),width=0)
        canvas.create_rectangle(self.canvasCX+workSpace.editorWidthR,0,self.width,self.height,fill=rgbString(55,55,55),width=0)
        # title
        canvas.create_text(self.width//2,65,text="Edit & Get It",font="Rockwell 35 bold",fill=rgbString(233,233,233)) 
        # menu bars
        canvas.create_text((10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY-workSpace.editorHeightR+5,text="Editing Tools",font="Rockwell 20 bold underline",fill=rgbString(233,233,233)) 
        canvas.create_rectangle(10,self.canvasCY-workSpace.editorHeightR+30,self.canvasCX-workSpace.editorWidthR-20,self.canvasCY+workSpace.editorHeightR+4,fill=rgbString(28,88,71),width=3)
        
        canvas.create_text(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY-workSpace.editorHeightR+5,text="Current Color",font="Rockwell 20 bold underline",fill=rgbString(233,233,233))
        canvas.create_rectangle(self.canvasCX+workSpace.editorWidthR+60,self.canvasCY-workSpace.editorHeightR+30,self.width-50,self.canvasCY-150,fill=self.currColor[0],width=3)
        canvas.create_text(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY-35,text="Layers",font="Rockwell 20 bold underline",fill=rgbString(233,233,233))
        canvas.create_rectangle(self.canvasCX+workSpace.editorWidthR+20,self.canvasCY-10,self.width-10,self.canvasCY+workSpace.editorHeightR+4,fill=rgbString(19,72,97),width=3)
        canvas.create_text(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY+60,text=f"Current Layer: {workSpace.currlayernum}",font="Rockwell 15",fill=rgbString(233,233,233))
        # editor box
        canvas.create_rectangle(self.canvasCX-workSpace.editorWidthR,self.canvasCY-workSpace.editorHeightR,self.canvasCX+workSpace.editorWidthR,self.canvasCY+workSpace.editorHeightR,width=10)

        # all buttons
        for button in MenuButton.allButtons.values():
            canvas.create_rectangle(button.position[0]-button.xSize,button.position[1]-button.ySize,
                                    button.position[0]+button.xSize,button.position[1]+button.ySize,
                                    fill=button.buttColor,outline=rgbString(233,233,233)) 
            canvas.create_text(button.position[0],button.position[1],text=button.buttName,fill=rgbString(233,233,233))

    # configures all buttons to be drawn for UI
    def configButtons(self):
        self.upload= MenuButton(workSpace.loadImage,40,20,(100,65),rgbString(173,57,134),"Load Image")
        self.save= MenuButton(workSpace.saveImage,40,20,(900,65),rgbString(191,148,48),"Save Image")
        
        self.colorPick= MenuButton(workSpace.pickColor,60,20,(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY//2+80),rgbString(144,43,32),"Pick a Color",self)  
        self.colorFilter= MenuButton(workSpace.colorFilter,60,20,(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY//2+120),rgbString(144,43,32),"Apply Color Filter",self)  
        self.layerSelect= MenuButton(workSpace.setCurrentLayer,65,20,(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY+20),rgbString(19,72,97),"Active Layer Switch")
        self.layerAdd= MenuButton(workSpace.newLayer,50,20,(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY+110),rgbString(19,72,97),"New Layer")
        self.layerRemove= MenuButton(workSpace.deleteLayer,50,20,(self.width-(10+self.canvasCX-workSpace.editorWidthR-20)/2,self.canvasCY+160),rgbString(19,72,97),"Delete Layer")

        self.move= MenuButton(workSpace.dragLayer,42.5,20,(90,self.canvasCY-workSpace.editorHeightR+60),rgbString(28,88,71),"Drag")
        self.zoomIn= MenuButton(workSpace.zoomIn,42.5,20,(90,self.canvasCY-workSpace.editorHeightR+120),rgbString(28,88,71),"Zoom In")
        self.zoomOut= MenuButton(workSpace.zoomOut,42.5,20,(90,self.canvasCY-workSpace.editorHeightR+160),rgbString(28,88,71),"Zoom Out")
        self.rotate= MenuButton(workSpace.rotateImage,42.5,20,(90,self.canvasCY-workSpace.editorHeightR+220),rgbString(28,88,71),"Rotate Image")
        self.flip= MenuButton(workSpace.flipImage,42.5,20,(90,self.canvasCY-workSpace.editorHeightR+280),rgbString(28,88,71),"Flip Image")
        self.lassoCrop= MenuButton(workSpace.lassoCropImage,42.5,20,(90,self.canvasCY-workSpace.editorHeightR+340),rgbString(28,88,71),"Lasso Crop")
        self.rectCrop= MenuButton(workSpace.rectangularCropImage,60,20,(90,self.canvasCY-workSpace.editorHeightR+400),rgbString(28,88,71),"Rectangular Crop")
        self.rectSelect= MenuButton(workSpace.rectangularSelect,60,20,(90,self.canvasCY-workSpace.editorHeightR+460),rgbString(28,88,71),"Rectangular Select")
        
        self.textButton=MenuButton(workSpace.text,40,20,(self.canvasCX-150,self.height-65),rgbString(89,27,86),"Text", self)
        self.rectangle=MenuButton(workSpace.rectangle,40,20,(self.canvasCX-50,self.height-65),rgbString(89,27,86),"Rectangle")
        self.line=MenuButton(workSpace.line,40,20,(self.canvasCX+50,self.height-65),rgbString(89,27,86),"Line")
        self.oval=MenuButton(workSpace.oval,40,20,(self.canvasCX+150,self.height-65),rgbString(89,27,86),"Ellipse")
            
        

    def redrawAll(self, canvas):
        canvas.create_rectangle(self.canvasCX-workSpace.editorWidthR,self.canvasCY-workSpace.editorHeightR,
                                self.canvasCX+workSpace.editorWidthR,self.canvasCY+workSpace.editorHeightR,fill="lightgrey")
        for layer in workSpace.allLayers:
            if layer.editorAreaImage!= None:
                workSpace.shapeDrawer(self,canvas)
                canvas.create_image(layer.imagePosCX,layer.imagePosCY, image=ImageTk.PhotoImage(layer.editorAreaImage))
                workSpace.shapeDrawer(self,canvas)
        
        workSpace.UIdrawer(self,canvas)
        
        if workSpace.currentLayer.mode== "rect":
            if len(self.mouseDragBounds)>=2:
                canvas.create_rectangle(self.mouseDragBounds[0][0],self.mouseDragBounds[0][1],
                                        self.mouseDragBounds[-1][0],self.mouseDragBounds[-1][1],outline="red")
        elif workSpace.currentLayer.mode== "lasso":
            for i in range(len(self.mouseDragBounds)-1):
                canvas.create_line(self.mouseDragBounds[i][0],self.mouseDragBounds[i][1],
                                self.mouseDragBounds[i+1][0],self.mouseDragBounds[i+1][1],fill="green")

        
        

## Button Class for Interactivity##
class MenuButton(workSpace):
    allButtons= dict()

    def __init__(self,function,xSize,ySize,position,buttColor,name,params=None,active=True):
        self.functionName= function
        self.buttName= name
        self.xSize,self.ySize= xSize,ySize
        self.position= position
        self.buttColor= buttColor
        self.params=params
        self.active= active
        MenuButton.allButtons[position]= self
        super().__init__(width=1000,height=800,autorun=False)
    
    @staticmethod
    def buttonFunction(button,mouseX,mouseY):
        if (button.position[0]-button.xSize<mouseX<button.position[0]+button.xSize and button.position[1]-button.ySize<mouseY<button.position[1]+button.ySize):
            if button.params==None:
                button.functionName()
            else:
                button.functionName(button.params)


workSpace(width=1000, height=800,title="Photoshop Tool")
