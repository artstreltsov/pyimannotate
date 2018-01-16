# pyimannotate


### What is this tool for?
pyimannotate is a Python-scripted Qt application tailored for hassle-free annotations of objects in images. Built on QGraphics architecture, it provides a smooth annotation experience to researchers aiming to mark locations of objects of interest. It supports input of all basic image formats (.png, .jpg, .bmp, .tif) or an annotated image in .json and outputs a .json file containing coordinates of objects, image size and a compressed copy of the image in bytes among others.  

 ** Note: Readme is still under construction **

### Dependencies (Tested Version in Parenthesis):
- Python 3.x (3.6)
- PyQt5 (5.9.1, pip installed)
- the following basic python modules: functools, base64, json.

### Hotkeys:
- E: enable drawing mode
- M: moving mode
- N: navigation mode
- Y: delete selected shape
- Ctrl+O: open an image
- Ctrl+S: save your annotations
- Ctrl+G: select pointing line color
- Ctrl+H: select shape color
- Ctrl+Q: close the application

### References (related tools that influenced development)
- https://github.com/wkentaro/labelme
- https://github.com/tzutalin/labelImg
- https://github.com/tn74/MTurkAnnotationTool

Developed by Artem Streltsov of Duke Energy Initiative, Duke University
