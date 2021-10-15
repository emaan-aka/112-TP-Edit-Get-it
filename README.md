TP Project: Edit & Get it

- Image Editor App

Emaan Ahmed, emaana

Description: 

A comprehensive image editing app built in the 112 Animation Framework, with various tools for quick Photoshopping on the fly. There is a workspace in the middle where the image is uploaded and edited, with the tools and functions on either side of it. These include adding shapes/text, cropping with rectangular or lasso select, dragging the image, and applying color filters. Image layers have also been implemented, such that each individual layer contains an image that is edited separately from the rest of the layers.


How to Run:

The file 'photoshop_project_actual.py' contains the Workspace Class and must be run to access the Image Editor. It imports the file 'tp_functions.py', which contains all of the functions available to each layer instance. I also included the version of the 'cmu_112_graphics.py' file I used to eliminate update errors.

Libraries:

The app is mainly built using the tkinter and PIL graphics libraries, with various submodules from within them. The numpy library will need to be installed to perform image array processing.


Shortcut Commands:

There are various keyPressed events that can be used to access most of the editing tools:

- u= load image onto layer
- c= pick and set workSpace color
- e= delete current layer
- s= save entire image
- r= rotate image
- f= horizontal flip image
- Up= zoom in
- Down= zoom out
- l= enable lasso cropping
- g= enable rectangular cropping
- b= enable rectangular select
- m= enable dragging
- d= enable drawing mode
- n= create new layer
- t= switch current layers

