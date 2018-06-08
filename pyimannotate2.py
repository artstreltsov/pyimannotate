"""
Author: Artem Streltsov (artem.streltsov@duke.edu)
Organization: Duke University Energy Initiative

version: 2.0.2

Description:
pyimannotate is a Python-scripted Qt application tailored for hassle-free
annotations of objects in images. Built on QGraphics architecture, it provides
a smooth annotation experience to researchers aiming to mark locations of objects
of interest. It supports input of all basic image formats (.png, .jpg, .bmp, .tif)
or a label file in .json and outputs a .json file containing coordinates of
objects, object types, respective label classes, image size and a compressed
copy of the image in bytes (optinal, default=False, checkable in the 'File' tab),
among others, plus a .csv workbook featuring the above.

Hotkeys:
E: enable drawing mode
M: moving mode (move vertices, shapes)
N: navigation mode (pan mode)
C: complete current annotation object (if a non-closed shape is sought, i.e. line or point)
K: copy selected shape
Del: delete selected/highlighted shape
Ctrl+Z: undo last action (remove last added point)
Ctrl+O: open an image
Ctrl+S: save your annotations
Ctrl+G: select pointing line color
Ctrl+H: select shape color for the active class
Ctrl+Q: close the application
I: Initialize (or edit the list of) labels
L: Set line width of all objects (retrospectively)
[: Set attraction epsilon (attracts cursor to shape's first point if epsilon close)
]: Save original image bytes (check option)
"""

from functools import partial
from base64 import b64encode, b64decode
import json
import re
import pandas as pd
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys


#Application icon bytes to load from
iconbytes=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00^\x00\x00\x00R\x08\x06\x00\x00\x00\xdd\x10c\x15\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00!tEXtCreation Time\x002018:05:27 14:32:54M_Yo\x00\x00(\xddIDATx^\xed\x9d\t\x90&Wq\xe7\xb3\xbe\xfa\xce\xbefzFs\xa3\x0b\xa1\x03Y\x16\x92\x90\x02IF`\x10\x06\x83\r\x02\tq\xd8\x12+\x0c\x06\x04\x18X\xee\xc0\xb0\x08\x1f\xa0\r\xe3\x00F\x04\xd8Dl,\xebe#X\x8c\xbd`\xc0\x02dY\x88\xf0:\xb0\xd0\x81\x90\x84Nvt\xcch\xee\xa3\xaf\xef\xae\xaa\xfd\xfd\xf3Uu\x7f\xdd\xd3\x83\xe8\xee\xb1CD(G\xd9\xef\xd5\xabw\xe4\xcb\xcc\x97\x99\xefU}\xa5(\x03\x0c\xd0_\xcf,\x02Q\x94g\x16@h\xf9\xcb\x83w\xb3\xc4\xbe\x8e4\xf6\x11\xe1?d\x1e\xe9\xc0<Jy\x1a`\xb0\xaf\xa8\xc8Sw\xe1\xd8\x03\x8c\xa73\xeb\x83\xeaHy\x01\xf9(\xa5]9\xbfVy1P\x9a\x0f2Pw\xc1\xfd\xc3\xf2"\xc0\xaf\x8b\xba\x82\x90\x9f#x~\xbb(\xd2\xd8\xf3\xeb\x0e\xde_\x98\x0f\xf3(\xca\x95\n\xc8\x1f\xd5y\xf4\xe9\xab(\x9f\x8f\x83\xf3\x08s\xcd\xfb\xf5y\xcc\x813\xbe\xd7m[\xa5Z\xe5\xb2\x1bJ\x8b\xca\xde\x19\xf9E\x99\x02DE\xbe(\x1f\xbc\xbfX\x9e\xd4\xfb*\xea\n\xf2\xfca}\t\x06\xf3\x8b\xc1\x91\xea\x16y\xa5\x82<\x7f\x94\xe6\x919\x9fz`\xc5\xaf\x85Q&\xc6\x96,M\xfa\x96\xa5}\x8b+eO\xa3R\xb8o\x91\xf8[\xf4#\xc6\xa7s2\x92$\x9f\x82\'\x86\xcc-\x8300[i\x943U\xdc\x0c\x9a\xce}V\x99\x84\xd5o\xcfX\xb9\xbe\x8a\xfc\x9c\xd6G\xedf\x92\xc51\x8d$\x948/]\x08\x0b\xec\xd3,\xcc\x89\xec\x97\x87\xa3\xd9\xd7R\xe1(\x8d\x9d\xd1\x8fX:\xd8\x9d\xe7\xd5O\xa2\x0cl\xef5\xad\x04_\xcb\x95\xaa\xdf\x8bfWU\x80\xa8\xdb\xcc\xb2~o\xd2\x1ey\xf4a\xebg\x8bs>;\x02e\xd1\x11g\xb28\x84^\x8eN_\xcb\x81\xa31\x8f\xc0t\xfa)\x9ad23\xf4\xa0\x1b\x02\xb4<\xcb\x12\x93.c\xc4\xadZk\xd8q\'\x9cd5L\xf9\xe0(Q\xaf\x9de\xf7\xfc\xe4G\xf6\xbe\x8f\xfc\xa5\xed>\xd0RQ\xb83\x00\x8b\x93\xbbX\xcd\'\x86\xc5\xfaZN?\xcb\x81\xa31\x0f\xf5!L\xa5\xa3)\x0cOKV\x12\xd3\xc5\xfcRd\xd5rl\xbd\xb4\x8d\xf5@\xf5\x11\xc0o\x9c\xff,\xfb\xd8\xc7\xdfc\x1b\xd6m\x1a\xb0\xf0\x8c\x99t\xb3\xec\xae\xdbo\xb17\\\xf51;4\x1d\xd3W\xae\xf5\xf4\x1e\r\xc6C\xb3\x10q+\xf3\x92\x01\xef\xf0\xcb\x01\x8d\x0e\x9fd\xe8O\xff\x1d\tT#\xcf\x04\x18\xac\xbb\xa0C\xa7\xac\xa8>K\x7f\x01\x87\x8f\x1e\x00\n\n\x8d\xcdaa\xdb\xd9\xfb$\n\r\xc5\xe4\x14V\xa6\x94\x175\xb3$\xb3V\xd2\xb3QXX+e6\xd3m\xda\xf9\xcf=\xc7>\xff\xc5\x0f\xd8\xc6c6\xd9\xa0=)uq\xce)\xf6\'\xa9U\xacG\xda.Um&\xaa[;\xaeY;\xc5\x92A\x00\xee\x81\x7f\xa9\xb5\x19\xa8\x899j\xe3\xc1;t\xd3&DZ\x14q"\xad\x05\xa8\xb2\x1eT\xe3\xf3I\x15\x17D\xb3\xfd\xb5\xb2J\x8eU\xc7fZsT\xde\xfbb\xbc6\xe3\xf5\x98d\x1f\xec\xb2\xbc\xdb\xb4\x9bIJ\xd6B\xf5\xba\x8c)W\x97\x12A(\xdf&\x82\x98\xe9\x97\xa0\xb1L\xdd\xc8\x128\xd5gn\x1a\xbf\xcb\x98\x05*(TJLG\x1b\xc6\xcfQs\xf0\xb6(\xa1\xda\xf8\\\x9d\x8e\nt\xd5\xadi\xd0\xc5\xb8m\xb4\xbd\x0b\x8b\xe07\x82!\x03\xb3k\x98\x96v<l\x13\xd0\x1f\xc5u\xf3\xa0f\x11y\x97\xe2\x06\x81\x91DV+c\x97\x14\x0e\xc5V\xea\xc5H/\xb2!\xa4\x1aEM\xcaE\x1a\xf6J\xb6\x0b5\xaf\xe0A*Y\xdf\xaf+9\x96\x11R\xb9\xc8CD\x95iy=p6O\x9b\nS\xad`\xfb\x84u!\xf7b\xecb\x8c\x80Yo\x9e/G\xd4-Q\xeem\xd4Wb\xb5\x94\xf1\t\xcf*\x8e\x895J\xb1\xd5`\x0c\x0b\xdd\x92$A j\x87\xbeSO}EQ\xcf\x1a\x19a_\xda\xa2]\x87~\xdaV\xf3q\xa1[\xf4\x88\x16G\xcd\x8br\xa7#\x83\xbd\x99\x8f\xa7\xeb*s\x86\xfdV\x03\xebQ\xd7\xef\x97D+c\xc5\xb4\xd5Xe\xd2z\xd6\xb1j\xd4bLL\x0ce\xe2a\x96\xd4\xa8[\x01\xfb\xc8C\xaex>D\x1d\xc2\xc9;n\xb9\xcd\xde\xf8\xb6kl\xcf^*\x94W\xd9\x18\xc3Nv\xa7\xec\xcc3\xd6\xdb\xfe\xe6N\x1b\xae3\xc1\x84N\x90\xb6lZ\xa60\x89\x0e\xd3\x92:\x0c\x0bM\x0ej\xceyI\xc4\x0b\xf3JA4p\xe1]]y\x9f\xcay\x9f\n\r\x98$Z\x1d%u\xf2R\x1b\xd6\n\x95\x99;\xb7\x10c\xbfl\xf7m{\x9c\x8b\xd8\xc6F\x86\xad\xdbO\x10@\xc7V\x95\xfb\xb6\xe6\xd8Q\x8bY\xd7)\xccO\xa5\x10x\xba>\xdd\xc6\xcc\xab\x84\xa6J\xc4l`\xe8\x8f\xce\x187+\xc9\x1e\x13\x10\xfa\xbd0\x93\x94\xb2L\xe1\xb5\x0f\xa8D\xf7+T\x979\x16\r\x122\x8e\x95|\x1ac\x13\xa8\xdf\xef\x95lrw\xc7\xf6\xed\x8f\x10V\xc5*\x8d\xb6=\xe7\xfc\xe3m\xeb\x17?h\xeb\x8f\xd9\xc2\xa8s0\xcb\xf87\xbf\xfdOl\xff^\x96\xffT\x19B#\xdb\xbcy\xc4\xbe\xfa\xf5?\xb3-\'mF\x82\xd4t\x1e3\xf8 \x0f\xfdb\x11\xa0\xf8\x08w\x0e\xbf\xa1\xbe\n\xf0\xbcv\xabJ\x83\xdd\xcd0+\x0b!\x88\xc8\xec\x8f\xdf\xfbi\xbb\xfe[7\xbb)\xeb\xf6R\x1b\x19\xaa\xdb[\xde\xf4b{\xcb\xd5W\xd8\xf0X\r\xe1\xd0%}\xb18\xc2\x1c\x04\x8b\x11\xa6!\x16\x96\xeb\x9a\xb6\x81\x16F\x94\xd4\x85\x03\x90\xc9\xb9*\x03\x1f\xb4\x9d\xda\xf1\xe8\x03\xf6\xb67\xfeW\xbb\xef\xa1CV\xee"\xe6z\x17\xe7\xfat\xdb\xfa\xa5\xf7\xdb1\x0b\x18?7+4F\xce\xb2V-\xb3\x8b\xc5n&-\x1b\x1e\xc1L \x84\xa1j\x86\xd6G6\x82Y\x1avL\xb9\xeeR\x9e\xf8\xbd\x858\\\xcbldQ\xa4\x0f\xf53\x88*\xf3{\x89\x8dT{\x8e\xc3\x15\xa1\xfa\xef\xd9PM\xd8rl\x80u\xbff\xcf\x08\xcet\xf6X\x82)\xa9c\x9a\xea\xf5\x8a\xa5\xfd\x9e%\x1d\xea\xa1\x81\r\xcc\xe4\x10\xb4\x0fW"\xab\x93\x1f\xaej\x1e \xe3\xcd\xc7\xcc\x1a\x8c\xd7\xf0\xb9p\r\xaa\xcd\x08\xe9\x88\xe6\xe2\xb4\xcc\xd0\xbe\xc9\xbc: \xd7\x9e\xb6\xa0\xb9\x0f\x1f,\xf4C\xfdz9\xb2J\x05s\x85 *\xe52\xf2\x80\xbd\xe0bA\xc8,\xe3\xb3J\xc9*\x10:\xddo\xb3lq-\xb2\xd5\x88H\x12\x95\xfb)g\xd8z\xecY\t\xbbY\xca\xa6Yz3\x16kk\xccR>\x1cY\xd6\x8b!\xedclmH\x17 \xcb6N\xf13i5\xc7:c\x92bb\xe4&K6\x95\xe3\x0c4\xe1k\xa0\xab\x1c\xe3\xcc\xca%\x9b\xee\xc8]3A\x02\x822f\xa8\xccD\x15\xcd\xe1&\x88\x97\xa9\xd8)h\xd08\xcc#\x9d\x1e@\xcd\x0b7\x0f\r%\xd1N\x1b\xb5\x0b\x88\x07\xa1L\x0c\xd4\xe2\x96\xad\x0e\x88=\xcf&@\x85\x07\xe2\x07\x9d\x8b\xb9p8\xeduX%\x98\x1d6\xa9\x18:L\x16\x1c\x9c\xbfP\x1c\xe6\x18\xdf\xd7\x04q\x14ht\xbdBG\xd8J\xc6d\x82\n\x9a4\x03.\x94\xaa\t\x11B\xc4\x1a\x8c\x88~t\xf0\xb4\x10C\xb7\x8b!\xe0\xfeAg\x1d\xeaK\xa0\xfa\xc59\xc6\xfc\xba\xa27\xb6!j\x0c\x93\x0e\x93\xd6H\x85\xec\x08\xb9\xdbk\xcayf6Z\xadA\x7f\x8a\xb6\x8b\xcb\xeaW\xa8C*h\xc7g\x08\xfd`\xab\xd4\x04aZ\x89\x98\xca\x91y\x94\xd0L\xe6\x11\x13\t\x954/\x8d;\x8fQ\xa8t6DZ\xa0|\xce(\xf5\xc6}\xfe\xa2=\xa3]\x90\x0c\r+1\xfe\x05\x87\x8f\xc3\xee\xa4]\xcb\xca\xbe\xdd:\x0cJ\x1aD\x88\xdf\xa0\x034\t-\xc2\xa3\x91\x87p:\x0bnN\xcc\x11j R\x11\x92\x8d\x90\x07\x9c\xd2\x90\x9d\xcd\x1f\t\x9d\xa19\xa3\xfd\xd0H\xf9\x00)D\xa6\xac\xa4\xc4\xf6\xe2\xbcv\x80\x8fB\xc3\x0e\xc69\x04\x12-0\x11mH\xb4\xfa\xd0q4\xeb\xa0\r\x0f\xa5(\xf3\x14\x11\xd0\xa4\xc5\xed\xfd6^\x9d\xa1\xeb\xbd\x96\xc4\xdb\x98\xf0#\x96V\x1ff\x88\x9d\x96\x96\xb9\x8e\x1e\xa1\xef\x9d0d\x1f\xa3M\xe1\x88Y%\xac\xac\xb4\x9f3/\x17\xf6 \x14\xc1H\xc6jL\x08]\x91\xb1\xf5 #!\xbcMp\xfa}\xd4\xba\x87\x8c\xfb\x94\'\xd4\xf5\xb0\x92P\x14\xeeY\x86\xf9\xa9b\xb2"\x94\xb8p/\x83\x10\xb1\x7fr\xe7\xfa\x9f\xde\xf1Qk\xed7l\xbb\x96jbc\xe3e\xfb\xde\r[\xed\x98\xf5\xc7\xe3\x9f\x15\xedB\x98N\xe0\n\xf193\x0b\xad\x15\x88\xf0\x9cR@\xd5\x9c\xd7\x80v\x02a%\xe4\xe5\xb2}\xba\x99WRT\x9f\xd9Ak\xb7w\xd9\x1d\xb7}\xdf\xda\xdd\xfd(@\x0f\x879\xc3N\x10c\xee\x155\x96\x14B\r\x15\xf4\xd5\xec\xdb7\xdcj\xf7\xdd\xaf\xc8\x06\x06\xe2\xf8\xca\xf8\xa73\xcfXm\xbfy\xe1IV-\xd5\x88d0_\xdc\xeb\x13nVku\x1b\x1f_g\x9b\xb6\x9cbc\xab\x8e\xc3\x14\xad\xa3\xbbqV\xc3\x90E\xacn\xd1x\xd8\x1c)\xc3h\xa0\x98\x04\x96\x9a\x1a\xb7\xf7\xef\x9a\xb6\x07\xee\xfd\xb1m\xfb\xf9\xa36q\xa8\t\x8d=c\xeb\xc3^!\xb5\xfd\x13-\xfb\xc6\xb7\xef\xb0\xc9\x83)!z\xc9\xea\xc9\xb4=\xe7\xa2\x93\xec\xba\xeb>d\x1b\xd7>\rZ\xe6`\x80\xf1\x1fs\xc6\xf7\xa4\xfa\x84\x00\xe3\xe3\xb13~\xdd\xba\xe3\x89\x8f\xc5x\x11$\xc2\xd4*`\x86\xf6\r2\xfb\x89a@\xcb\x8b~\x1c&\xb9\xdcm\x13\xadm\xf6\x85/\\\xc3\x8e\xef\x11\x1b\x1am\xa3\x8d\x18g\xec\x9dW\xcb\xc3:\x81r3(w\x8d\x85W\xc2\xa1\xf5P7i\x9d\xf2n\xec0!\x998\xe5M\xd0Vv\x89qm\x8cp/\xb6\x13\xb6\xfc\xba\x9d\xfd\xeb/\xb2g\x9d\xf9Jl\xfb\xf1\xd6\xeb\xd6q\xd4m\xaajK\xa7\xd6R \x01}\xb2\n\xc5\xd5~\x86I\xc5\x9c\xfc\xfc\xfe\x87\xecK\x7f\xf57v\xe3M\xb7[\xefP\x86o\x91y&\xeegZ\x19\xce\xc1\x85\x839\x9a\x8e\x10fS\xc2n\xd9y\xe7\x1fg\x7f\xfd\x85?&\x9c<v\x1e\xe3\x8bQ\x00\xac\xb9v\xa4\xa0Rz\xf2\xb9\xaa\x82W\xd2$|"s\x90\xf3?\xc7\xdc>\x1e\x96_X\x06#\xe9\xc7\xf3J\xf3\xbc\xb4\xb9\xce\xaa/\xc58\xbbh\x8f\xb5f&\xac\xd9\xea\xb0\x02\xd1|!>\xa8O\xd4\xd2G\xc3\x92n\x97HD\x1b\x9a\xc4:\xd3\xac\xfd.\x1b!\xccb\xd6N\x90\x93\xe2\xe9.&\x81z\xdak\xb0y\xa2\x14]:\x84\xef\xdbg?\xdfv\x93\xfd\xf3\x0f\xbffw\xddy\xbdu\xba\xdb1\xa7M\x1f]\xda\xae}uP$\xf9 \xcc\x9b\xec\xb6\xaf\xae\xc8\x1e{\xf8a\xfb\xc0\x07\xff\xdc\xfe\xcf\xff\xfe\xa1\xed\xdc\xd5\xb5\xfd\x98\x99ny\xd8z\x15\xf6\x10\x04\x01=\x02\x83\x84\x94\xed!\xe6\x1e$\xa6\xc7v\xb0\xf2\xe0e\x98\xe0<\x98e|DL\xda\x85\xd9\x19\xbb\xae\x14{Vb\x99\xfa\xe1\x8f\x13"\x82\xc0\xd9\x0e\n\xe2\xa4\xc1\xbf\x08e?\x83\r\r\xa8~X%\xf3L\x14\xf2\x84\xe0\x94\xd5\x94`D{]\x85\xb5r\x88\x915Fp|\x84\xb6\x11X"\xea\x8a\x88`t\xd4\x1a\xcb\x89\tP\xb1\x1a!\x8c\xa2\xb1\x12\xf9z\x8d\xe5M\x1d\x91\xa7\xad\xbav\xe2\x11\xce\xae\xd2@\xd7<\xc5=\x8f\xc4\xb6\xf7\xc0\xddv\xd7\xcf\xfe\xd9&\xa7\xb7\xd1\xdfA\xa6%6\x88N9O\xe5\x85\xd8}\xed@QB\xe4n\x7f\xfb\xd5o\xd8\x83w\xe2s\xe2U\x98\xb4Q\x16\x7f\r\x9aa4\x1b*\x1d)hS\'V\xb3\xb6\xac\xdc\xc4\xbe#\x08\xd9\xffR\x1f;\xcf\xdc\x16\xf2^#\x00\x14\xcb\x81\xe8\x12f{\xe0\x91kwh\xa0\x021K\xcc\x06<\xc2\x01\xdd\xf4hu\x14f(\xcf\xd3\x17\x1e-\x94\r\xe6\xbdO\x99\xa7\x9c\xf1\xbavT\x1d\x98\x9b\xd5\x18O\x13\xd0\xd6\x9c"\xed.15\xc2T\x9e\x8b\xc8\xc5\xf3\x08Ht\xf5av\x89:\xb4\x0e\xc2\xe0^\xd2\xa6oL\x8f\xe8O{\x08\x11\x94[(\xda\xc9G4\x1a\x89=\xb6\xf3\x1e\xdb\xbb\xe7g\xccE\xf4\x88\xb6\x9cv\xccJ\x88bt\xce\x82\xc9\xe0\xde\xee\xed\x0f\xda\x8f\xfe\xf5>\x16V\xd5\x9a\x1dv\xcd\x84\xad\t\xe3e\x84\xd6\x95\x12\xfb\n\xb1;\xc5Y\xb3s\xae\x83Ii\x86\xd8\xa3g\x95\x84\xd0\x19\xbe\xc9\xc4\x04>\xce\xc1\xdc\x91\xc1;\xfe\xc4\x0e\xecS\x18\xc4P\xd0\xbe\x0e\xe7z\xc3\x8d\x9f\xb6u\x1b\x8ec\xc1\x88\xd19\xd3\x89\xafY\x0e\xf9uN,\x90E\x87pb-\x06Z\xcb \xd2n@\x02r\xa6\x92W ]0\\\xf7]\x089\x10\x95\x186\xfe`\xf3>\xfb\xeb/\xe1k\xbaw\xa3\xa1h\t\xda\x9d)\\\x00\\\x19\x94j72\xb0#Q\x99\x98\x19\x9c\xee\xdc\xfdL\x9a\xafk\x04V\xdc\x93\x0e(R\xd1U\x1c\x0f\xdbK.z\x9b\x9d{\xf6;\xf1\t\x1b\xb8\xc1<\xb8\x11z\x0ecj\xd7\xac\xdc\xdd?\xb9\xc5\xde\xf3\xae\xad\xf6\xd0\xb6\x03\xd6*\x8fP\xce\x0e\x7fz\xc2\xdex\xc5\x0b\xed\xf9\xcf\xfb5\x04=\xe9&\xa5\x8fb\xf8\xdc1Q%$\x9f\xa4m\xdb\xb2i\xa3\x9dq\xd6\x056:\x8a0\x03\x19\x0e\x81:\x87\x0c\xa6\x05\xc2\xc3\x19\x86&\xa3ry\xfc\x81j9q*\xeba[1\xbb\xbe5O\xd3)&\xa3\xcd\x03\x1b\x1c\x8f\x97\xd9dE\xfbC>\xc6q)\xef8\x05\x1e\x08\xf7\xbd\x1e\xe1\xa2\x1d\xa0\xbf&\x1a\xd6\xe3\x9e\xfac\x04f\x9cJ\xa3Ic\x98\'\xcdv\xa6\nT)\xc7A\x86\x17L\x0f%s\xe0\xf7\xd0x\t\xc1\x81\xe9h\x13\xa6\x8d\xce\xac\xb3G\xb2\xba+F\xe7\xb5fA\xfd\xa9L\xfc\x10CUk\xddH\xd5\xce=\xf7\x14{\xd9+^f\x97\xbd\xe6\xf5\xf6\xca\xcb.\xb7K/}\xad\xbd\xea\xd5\xaf\xb2W\xbe\xfaR{\xc5\xe5\x97\xd9+^}\xb9=\xfb\xfc\xe7\xdb\xf0\xc8|\xa6\x0b\x068\xbat\x88\xf1\xf81\x1b\x84N\xf71\xdb\xf1\xf8=\xb6k\xcf=\xb6{\xff\x8fm\xc7\xce\x1f\xd8\xf6\x9d7\xd9\xf6]?\xcc\xd3\x1bC~\xd7\xbf\x807S\x96\x97?.\xfc\x17\xea\xdfn;w\xdfe\xfb\xf6<\x083\x10\x9e\xf7\x1dp\x96\xd9O"\xd0\xe6QK\'\xc3\x91\xc7\xb9\xdcD\xa5\xf6Q\x8e\xba-?\xc5\x04\x14\xe2\xe6\xba1\x0f\x06L\xcd\'lb\x7fLhF)b_?^\xb5\xef\xdf\xf8\x17\xb6~\xfdf\xb9\x0b\x98![\x08`\x03\xc3I\xa2\xcc\xc3\x04U\xdb\xf6\xd0C\xb7\xd8\xf7n\xfa\x92ML\x8bq\xb8\x18\r\xe6\xfbu\xc8\x91}G\xbb\xb4\xfcD\x9d\x9f\xf0\xe1\x942\x9cQ!w\xd9\xca~6i\x15\xac\xd8\xde=\x13\xac\x1c\xb5E\'\x13\xec1eKb~\xae\xf1\xe9\x80\xa9q\xa0<\xa5O\xa1\x98Sf\xd7\xf9\x92\xe7\xbd\xcd\x9e}\xd6\xfb05k\xa9\xe0\x9e\xc55\xde#/o\x12\xae\xef\xc1\xd4\xbcK\xa6\xe6\xe1\x03\x1e\xc9d}\xbca:c\x9f\xfc\xf37\xda\x15W\xbd\x16\xaf\xc4\xeaa\x9enY\xd5\x9e)\xeb\x19\x86\xef_4W\xa6S\xd6t\x07 P\xb7,PS\x11\xc8\x00\xec8\x0fL<`\x9d\xce>H\xd8o\xd33;mrj/Q\xc3~\xd2]\xb3\xf9\xa9\xa9}61\xf5\xb8\x1d\x9a~\xd8&f\x1e\x04\xefGX\xf7\xd9ds\x9b\xcd4\xf7\xdb\xa1\x03\xfb\x89d2\xb0b\xf5\xe1\xb2\x8d\xac\xce\xd5\xe9I\x04R\x82\x18\xa1\x8e\x11%\x95\xab\xf0\x00N\xa7)<\xc0\xdeJ\xa0\x8a\xa6t\x9df\x98Q\xf8#\xd1\xe9\x88z!\xac\x80\xf1U\x88\xd8\xc2(k\x18t\x88\xa8\xa3\xee\x87j\t\xe1\xa0tGQ\x86L\x85\x14O\x0f(\x94\xd7\x06\xa7D\x81#D;\xd6\x88fHcBA\x852z\xbf\xaa=\xd3\xb3^\x8b\xd8}\x06\xdf\xb0\x14m\xff\x0f\x02EK=\x9d\xe6\xe2\xf8q\x1d\x1e\x81\xc9\xe4\xc8q\xeb\x9a\xbfh\xbf$\xa2c\x10\xed%\xbcp\x1e\xe4\x8c_\xee\xe4\xb4\x9d\xee e9\xcf\x83\x1eIdp\xd8SzV\xaf\x8e\xfc\x11Q\x1eQ\xc8\xc9\x89\x10\xd12\x802\t\xb1\xe2q.Q&\x04\x86\xe0\xc2z\xe7\xcf\xd1\x83`\x83\x83\xd1U\xd7!\xb7D\x10a\xb4\x95\xe6\xeb\xd9\x85w\x87\x9d\xf1\x84\xfeclM\x1c\x13\x16\xeb\x00\x8e%\xe0\xaf\xcf,\x00/Y\xde\xd4\n\x8ea\xc0J8\xc4L\xdbn.=4\x1a@\x81\x12M8\xcf\xfa\xc9\xa6R\x95\xe5\xa8\xc9(\x95p|\xbd\xc2\x15o]\xf4\xb1B\x10m\x83\xf3\x9c\xcbk\xf0\xa5AA\xd2\xacN\x0ct\xec\xf7\x06H\xf6 h\x11X\xfa\xa8\xb3\xa0\xb5\xa5\x8d\xc60\xe9\\\\.S\xe1\x14\xc9\xa9\t}\xc9\xc1D\xc5\xb8\xaeby\x08X\x8c\xac\xfc Jp\xe2\xbb\xaf\x1aPe\xbf\n\xa0%\xbe\x00~\x11\xe5\xcbf|0\n\xe2P\x1d\x86\x06\'X\x82\xd1\xb3\x889\x11\x8a\xd9\xbe-P\x1b1^BP\xb9\x04A=O\x17\xa2\xca\x85\xde\x966\xbf\x12\x90\xb3\xd2\xc9\xd5\x11\xc1/f\xed\xb2\x19\xef K\xa3\x14\xce\x16\xda\\0\xd8S\xddS\xaa\x8c\xcc\x87ku(sP\x1ba\xbe*\x0e\xc3\xe2\xfe\x93\x08\xb4\x02\x15f\xea\xe1\x87\x1fo;(\x05\x0bR=\x952\xe6\xe5\x8b\xc0\xe2\xa5\xbf,\xf8\xd1A8{\xc9\xf4DYcc*f\xcd\x04\xa8\x17\x7f\x82\xdb\x0f\xe5.\x80\x05\xe8\xf2X\x0c5\x862O\x12\x08;\xf9\xc0\xfc<\x13\xd2A\xa6\xcf\x03\xca\x05\x8b\xdc\xf3;\xcb\x9b\x9a6\x08 \x92/\x97\xc7m\xcb\x86\x0bm\xed\xaa\xd3l\xfd\xeaS\xc1Sl\xed\x9aSl\x1dx\xcc\xda\xd3m\xcd\xda_\x0b\xe5\xabN\xb5u\xe3\xcf\xcc\x91\xbc\xea\x8c\x87:\xc7\xac}\xa6m\xd8p\xb2\xf5t\xa8\x8d\x80\xb4\xd1\x91\xe0\x96\x0c\x83\x93\x94^\xe4\xabF\x0e]\x0c\xd3\xe3>\x1d\xbe\xb9B8Th\xa2\xa3\xdf\xc0<\xed\xf3\xfc48\x07e\xf5B\x94w\x05\xa7\xa2R\xbe\xf1c\xdez\xc3H\xe0m\xb5{\xf2\x8d\x1f\xd7\xa0"\xf8P\x8f\xf2\x05\xa7\xb1\x82\x15\xec\\\x89Q\x89cKqj33\x8f\xd8\xc1C\xdb)#\xbaa\xc7\x1ayh"\xd0\xe4\x8a%WL\xb4H{\xa0\x0e\xdat\xad\t\xf4\xad\x93=l\xff\xe3+\xd7X\xb9\xde\xb7D\xa7\x8a\x94.\x190QRH\xdf\xb9j\xce\n]\x01_\x81*\x03\x12\xfcH\xa5\\\xb7\xdf\xba\xf0mv\xee\xb3>jqu\xcc\xc7*|\x91hQ\xe3,\xaaZ\x87\xe6\xf7\xdcu\xab\xbd\xfb=[m\xdb\xb6\t\xa2\xb6U\xd6\xee\xcd\xd8H\xda\xb4\x8f\x7f\xf2\xad\xf6\xba\xdf\xbf\x84\xf0W\xa2\xd3S4\x9d\xf7\xc0\x1f\xe6+\x16\xe8\xe5\'\x7f\xc9I\x84\xd8\x88$4;\xfd@\xc9\xb2@o\x9e\rA\xec\x88\r\x0f\x9dlO\xdb\xf2\x1bv\xec\x96\x0bl\xcb\xa6\xf3l\xd3\xe6s\xc0\xb3\xc0\xb3\xc13sT\xfe\xd9\xa0\xee\x85\xfb\x1b\xbd\xec\x1c\xdbL\xf9\xe6\xcd\xe7\xda\xc6Mg\xd2\xefZK\xda=\xb6\xd81\xc4C\xe9Rm\xfc\x80\xb4f\x1d\xb3$!@\x08)L\xaf\xd7\xa5\x0c\xb1U\xabl\xfa*h\x1a;\xef\xcc\x9f\x82\x81\x99p\x8a\xfc\x0cu\xf2\x87$\xce@\xbd\xc1\xd6\xb3v\xe7\x10r\x99\xb2\xc6p\xcb*u\xbd=&6\xb7\xd9\xb5\xef\xcf7J\xb9\xc0\xc9\xa5}\x04\xe0\x81\x87\xca\xc3j(\xf2+`<\xcd\xa5\xb4\x02\xc2\xc9~\x17\xec\x8d\xb2\n\xc6\xe9\x7f3\x1d\x17\xb8\x05\xd4\x9b\xb2\x1b\xc0u9\xeaZ+Ie\xda\xfdn`\xc7;\n\xa3Fq\x05#\xcepi|Bds4`^H\xaa\xa8\x89\xfe\xbb\xcd\x0efm\xca\xba\xbd]\x8c\xd9\xf5U]B\xc3\xa3\x92\xb0\x01C\x87aZ]\xa7\xd3,\x11\x98\xd5c\x93\x08ce\x86j\xd4kOb\xbaZ\x81\x97:6\xa9\xd5\xaa("L\x86\xbf\xc5\x82\xd7nVC\xfb{\x95\xbe\x8a\xc2JR\xba\x02\xc6C\x84\x84\x99C\\\xaeb\xeb\xeb\x10\xaf%\xc5r#\xc6\x17\xe1z\xba\x14\x10;Z c\x87<\xfb\x00\x7f-P\xafV\x0c#<\x11\xaa\xd7\xe8D|f\xd5FN\xf9\x12\xc1}C>y\x07\xcdR\xa8q\xe9W&\xb2Zg\xcc\n\xcc\xacL0\xde~h\x11\x92\x97\xb6g3\x9e\xa6\xba\xd6a f\xa5Z\xeb\xb2K\x9d\xb6Fg\xca\xaa\xb4\xefv\t&\xfaz\xb8\'\x90\x89\xe9\xa2(\xfba\x04\x93`\xacBe<\xac\xf4\x1db\xc1|\xa5\x08w%6^\x92\xd6\x13|1+.\xe9\xd1\x19dh\xc4\xc3x\xa5\xfa\x05\x8a\x08\x91\x9b_k)\xd2F\xe7\xf13\xbd\xdb\xed\xba/\\m\xdd\xe4>w\x80\x02\x7f\xf7e)\xe6F\x8eSIP\xb5P\x84mW?:?\xea6\xb1\xc5NFl\'\x1e\x7f\xa6\x9d\xf8\xb4\xb3,K\x82I)\x9cl\xe8\x01\xea0#\xe5\xb8f;v\x1e\xb0\x1b\xff\xe9.;p\xa0mq:b\xad.\xdc\xe8\xa6\xf6\xe6\xab~\xd7~\xeb\xe2\x17\xd9\xd8\xe8\x88U*zIu\x94\xbeFP\xc8u\x10\x9e\xf3"\x83O\xf2{>\xefb\xee\xd0\xb3|\xc6\x8b\xd8)\xca\xd5Q\x88\x0c\x124!\xe2\xbe\xb4?@\xce\xdcYI\x0b\x162^\x02\x13L\xdbt\xf7v\xfb\x8b\xcf^\t\xa1;,\xd6+y\xf4\xa7w\xce\x97\xc5\xf8p\xe5\x90\xc9_\x90&\x1d\x94\x84\xfbe\tB\xaf)6a\x08\xe6C\xd7p\x8d\xa6\xe1\xe8X\x95=2!\x04N!\x9d;0\xb6\xe4\xed\xf5\xc2HW\xa6\x06\xc6\xd7\xab0<m\xd8\xda\xb1\xf5\xb6zh\xdcN8\xe1T|\xd6i\xb6f\xfd\x8966\x0c\xdf\xca\r7_%\xed\xeeM\xaf\xa9\x14\xcaYr.\xac\x00\xe4<D\'D\xa1\xf9\xee\xc91l^6\x88\xd4\x9c\x87\x03eE&\xd3\x03v=8@\xc3\x9cq\x98\x041}E0\xd0\\\xe1d\\\x8b\xfdq\xa2D\xae\xb0U\xa7\xa5:[\x12\x93\xc5\xf4\xd9\xea"\x80r\xe9\x97\xec\xb4\xea\xf5a\xb4\xda\xeb\xa5\xafR\xa5c\xd5Q\x1c\\\xe9 \xa6\xeaq;4q\xab\xed:x\x93\xdd\xf4\xaf\xd7\xd9W\xbf\xf9.\xfb\x9f\x7f\xffV\xfb\xfa\xf5\xef\xb0[\xee\xf8\x9cm\xdf~\xb3M\xb7\x1e\xb0$\xdb\xeb\xa6+I\'H\xf5\xba\xcc\xb2AZ\xab_\xb2\xe9u\xb6!B\xefQB\xb41\xb44t)\xda\xb5\xbc\xfc]\x15l|\x84\xb4\xf5<2\xa0VP\xc8\xf3\'\x00\xa6 \xe9\xd1\x02\x93%&\xa5]T\rf,I\xdbs8\xac\x89\x98\n\xfa\x03s\x1dM\xa3\xed\xa1,\xd4E\xc6\x8e\xca\xbb#\xe5"\xea{t\xceb\xd5\x91\xb6\xcc\x0f\xb7h\xaf 7\x81\xe62\xfeGG\xd9\xeaS\xc2\xec\xb1\x1a\x14\x89\xe9\xc7\x11\x07\xf6\xed\xb4\xfb\x7f~\x8b]\x7f\xe3\x97\xed\xeb\xdf\xb9\xd6n\xbcy\xab\xdd{\xef\r\xd6\xeclcE\xed\xa2\xaf\xdd+15\xa9\xe9}\xa38\xd7p\x85R:\xfe\xd4\x06v\x96\x99\x83 \xcaU\xae\xd4\x81>\xd4On\xe3\xf5>\xe5L\xf76\xfb\xec\xe7\xafF\x1b\xef\xc2\xdcH\x1b\x15\x0f\xab\xdeb\x1d\x1e\x01 f\xde0\x80\xef\xa4\xe9\xa6\x0f\x93b\xbdV\'FRo\xd3\xba\x13\xd8\xc4=\xc3\x05\x1d\x80{\x19\x13\xd0+\x8c\xbe.R?w?4\xd9\xb2\x7f\xbb\xe3\x01\xebv\xcaV\xad\xa0d#\x13(\xc8\x94\xadY5l5\xf8\x914q\xc2I\x0b\x93E;\xd1\xac\xfe\xf4J\ni\xd6\xe93\x9f\xb2\x8d\r\x9dn\'\x1cw\xaa]\xf4\xbcKl\xf3\xba\xd3V\xc6\xf8\xf0XO\x80mw\xf5\x90wW=\xae\xdd\xae\xeb~\xb1\xa8\x8a\xba\x02\xe5U\x0f\xc9\xd1{JT\x93\xf4\x0fZ/\xfe\x7f\xf6\x99\xcf\x8a\xf1\xf7\xba\t\x906\x95H\x97\xc3xi\x9e\xaf\x16\xa9\xb2\xec7}D\xd8i]\xf6\xdb\x84\x7fCU{\xe1\x85/\xb7s\xcez\xa7\xd5\xe2\xcd\xb4\xd1\n\x84\xd6\xd9\xf3\x17\xcdE\x02,\xdbO\xee\xb8\xdd>\xfc\xd1\xcf\xd8=\x0f\xec\xb6v_\x81Dj\xa3\x98\xeb\x8f\xbc\xff\xd5\xf6\xe2\x97\\`S\x13\x0f\xda\xbe\xbd\xf7\xe3\x84\x1f\xb0=\x13;l\xb2\xb9\xdbZD?\x95\xb8\x83\xa0\xc3N\xb9\xd7\xd2^\xb6lCCO\xb7\x17_\xfc\xcaY\xae,\x03R\x96\x9e\x9e\xae\xe81\x17\xa1\x17\xcb\'\xb3\x1d\xe4\x1f\'}\x9c\xeb=\xa4ZV\xc2"\xaf:\xa1\x9e\xd2\xa2NT\xda\xc9\xeeq\x9aU\x8e\xcd\x8cg\xfc\xc5%M:\xd6\x13\x91\xa50] -\x83\xe9\xce\xc3\xa2\xad\xb8\x8d\tq\xe7\xaa*\xb2\xeb\t\xa6B{\x89\xe4X\xc6\xda\x04-\xeb\x90\xd9:\x84%\xdc\x80\xd2o! \xd9\xe2\xf9Ji\x83\xf5\x0eR\xde\xdab\xe5\xec\x19V\x9a9\xd9v\xef\xddL<\x7f\x86mb\xe3x\xda\xe9/\xb4\xe7=\xff\rv\xe9\xe5\x1f\xb6\xd7]\xf6\t{\xd5o\x7f\xc4\x9e\xff\x9c\xdfgE)b\x1a\xf6\x13\xd7\xf2\x10\xeaK\xa4-{\xff\x0f\xdf\xfd\xd2\xca\xc2I7\x03h\xed\xde\xbd\xf7\xdac\xdbo\xb3V{\xbfU\xaa\xb2\x9dZ\xaa\xb2\xcf\x9a\xa6l\x8fPu\x07\x99\xa8p\x01\x07\x05O\x82\xadgWY\xdak\xdf\xba\xfeold5\xbd\xb6\xd8\xbd\xb2\\\xdd\x86Js\x97\x02b\xbeV\x8a\xda\xcaf\xe7\x90I\xf3)\xef\xf7\xf4\xc3\x81\x11{\xe9E\xefA\xe3\xff\xb3\xaf\x04\xcdCo\x82I+\x83\xd6+%R\xa3\xf9]w\xddn\xef~\xfbg\xec\x81\x1d\x93\xa6\xd7\x97j\xd3\xac\xc6Z\xc7>\xfd\xe97\xd9e\xaf{1V\x05eJ\xa7YX,\x83l\x0c\xa1\xc7\xfe\xe6\xc5\xc4\xd4\x03\xf6\xe8c7\xdb\xadw~\x8f\x95\xb0\xcd\x7f\xb5\xa2\xa7l\x99\x14`\xc5\xa6&:d\x0f>\xf8-\xfb\xca\xdf}\x0c\xcd}\xcc5\xd5_(`\xde:\xfb\xd0\xd2\x17\xf8\xa1\x944\xf0HLT\xb1\xaa\x889\xd2\xd8\x1c\xbcx)\x8c\xa7.\xdd\x1c~V\xa32\xddq\xdf\x01\xe2\xec\x7f\xfb\xa2\xab\xed\xbc\xb3?\xec{\x900\x82\xc6\rc\xcb\xec\xf8\xeb\xd9\xe4\xef\xb93\xbce\xf0\xf3G\x0eZ\xabDh\x98\xd2:\x99\xb6O]\xfbf{\xdd\x95\x97\xb0\n\x9at\xab\xf1P x\xa2\x17X-\x9a\xa6\xe5\x14\xa8\xed\xfd!\xbb\xe1\xe6k\xed\xff\xfe\xe8\xdbX\t"\xa2\x86\xde\xf0_\x01h\x82\xd2\xda\xac\xa4\x97\x91\x1ew\x87\x12\xe9\x897&B\xa1\xa1R9H=\xdc\xd6=\xdf\x7f\xab<Gw\xa0\x05\x8a\x19\xa4\x0eb\xb4\x18\x08\xd3\x96\x13\xd5\xcc\x02\xc3\xb8\xb0\x0b\x93\xa3De\x9e\r\xa2\x08\x8c\tQ\x96v\x94\x18\x05\xee\x04S\xe7\x0b6o*\x90Cf\r\x12i\xea\xd7\x80\xf2aj\xab\x0e\xb5:\xd0v\xcc\x97 4Q\x7f\xe3\xd0\x7f\x1c\xf8t\xbb\xf0\xfc\xb7\xda\xe5\x97|\xc46m8\xd7Z3+\x8a\xe3%U\x11\xae\x95 "D(KP=\x82\xee\xccr\x06\xfaa\x97\xaa\xb2\xf4\xdd\xde\xe6\xe8\xb7\xd5n\x01\x16\x8c\x9f\xcd?\xc9`V\x16\x0b\xb97O\xb0\xc2\xa2\xc2\x905\xaaO\xb3g\x9c|\xb1\xbd\xe8\xf9\xaf\xb7M\x1bO[\t\xe3C\x18\x19$\x9b\xbf\xad\xa3\x021\x18\xf4%\x9e3\xcf\xeb\xe5K\xde#\x0c\xb4}\x16\xe5H\x8f\x84\n\xfb\x06\xcc\xce\x93\x05\x8a\x95\xe0\xe9,\xe4\xf3\x13\xf8Y\xfd h\xf7z\xbcUK\xc7\xd9\xd3Oz\x81\xbd\xfc\xa5\x7f\xb8\x12\xc6\x0b\xd4\\\xa8\xd7\x99\xbd \xc0\xbc\x8b\x1c\xf2"\x8f4f\x9b\x91/LA\x81\xbf*\x10\x1c\x18\x98kZ\xc1\xf8yS\xc8\xcbT\xad_\'\x8ce\xc3\xd9[o\'ly\xeeJ\x18_\x98\x1a\x99\x19\xf5\x1c\xac\xa6@g\x1cI\xae\xb1\xfe*\x87\x88\x91\xa6\x17\x8c-\xe8\x94\x80\x06\xd1\xa3\x10PG\xb7~|\x1b\xf0\xc9\x0b\x9aq\xce\xc2EtFw\xbd\x1c\xd4\xf4Jz\x18\x92\xea\xe8|\xcdJ\x18\x0fD\xc4\xf00^!_V\x1a\n\x9d\xc9v\x17\x82\xa6\xc0C\xb8\x9c\xe9\xe1z\x00U\x07t\xabD\x1f:\x14\xab\xd4q[\xbaV\xb9S~t \x9f\xbf\x0b\\Nr\xf6\xba\xd0\xca\xa5\x006\xa6B\xc8\xa8\xf7D\x9dF?\x89\x94\xe9\xd5\xa1^\xa8"(\xe6\xa7\x81\xa2r\x9b \xa3\xcf\xeev\xc4\x92\xee\xf8\xca4>\xf3pI/2\xe9\xdd\xc1\x8e3/\xd6V\x99^}\x1b.\x1b\x9d\xdbk\x8fZT6\x889\xf8\xae\x97\xfb\xbd>\xce\x99\xac\xa3V\x8b"\xa1\x81zG\x03\xe6\xc9\x92\xae\x97#[1X\x1f\xd8hw\xb4\x81\x9c\xebA\x1b?\x8f*\xbd\x88\xbcGK\x81\xc5\x91\x0e\xd4b\xf1\xab\xef{\x88\x150^\xdb\xfdCt\xac\xdf\x8d"\xc9\xda\x90?\x91\xd2\xa35I]\xab\xc0\xf3l\x1a\x84:\'\xf1k\xfd\xd4\x86\rD\xd6ae\xf4\x10J\x87\x95\xd0\x15&V-g\xfe<\xb4\\\x83\xe1h\xa5N\x04g\xcd\xd3\x93\x04DOR*[\x19-o\xd4\x1a\xbe!\xd2a\x80\xe8\xd6\xbc\xf5+\x15\xcdSa\xa9+\x90\xaf0\tX\xd6A\xb1=\xe6Sz\xb7\xfc\rT\xdb\x12\xfd\xe83n\xda\xce\xc7\xef\xb3\x9f\xde\xf3\xf7\xd6\xcf\xf6\x10\x9eKK\x19\xc9_\xfa\xd7\xf9\xb7\x98\xc8H%\xea\xaaL6F;Y/\x07\x05\x08\xaeTj[\x97M\xc9mw\xfe\x14\xc2\x0f\x85\x97Xu\x0b\x81-\tr3\xf2\xef\xfa\x9a6]6\x92\xa6}\xe2\xcf\xfe\xc0~\xef\r\x97\xb2a$\xaeg\xe3\xa4\xf7$}4\xfa\xef%z\x90\xaf\x07\xffu\x7fqW\xbf\xd9\xd5^!\xd3O<IW\xc0x\xb2\xfd0\xb94k[\xb3\xfb\x08KH\x04+\xb4\x14C\xd5\x91\x06\xd7\x03\x00\xd5\x9b\x81(m8\x98\xb8_\x17\xa8\xe3\x05\x84\xc8\x0exz\xe6Q\xfb\xef_\xfe4\xe9\x03\xfe\x831\xc9\xe8\xc9\xc8x\xfdRE_\xd2\xf9\xe4\xa7\xdeb\xaf\xbf\xf2\x15V\xa1o\xdf\x12\x11gh8\xbd\x01"\x9d\x17\xa8\xdc\xcf\xf2KS\x16\x97k0^\xc7\xe3a\xe69\xe8r)\xd0\x85Ym\x1f *Wmtx\xc8?\x92S\xab\xae\xb5zm\x0b\xf84p\xb3\xd5\xab\xc7\x83\'\xfau\xa3v"x:\xf93\xc13@\xe5\x9fI\xd9f\x1b\xaen\xb0U\xe3\x1bq@e\x1cl\xd8\xaa\xf7\xba\x98#\xad\xcb\xa3\x04+\xeb\xab\x10\xa0\x18[aN\xfa:Hj3S-\xebv\x9a\xd6mO\xb3#\x9d\xb6~?\xe4{\x9d\xb6uZ\xd3\xd6nN[\x99\x1d{\x1c\xaf\nL\x17\xc7\xc1Y\x8d\xbf\xea\xed\x7fj\x07\x0f\x94pp%+\x13]\xac_\x13\xdb\r\xff\xf4\x97v\xccF\xfd\xf8L!\xa3\xb4\x97\x16\xda\x1a\x13\xcd\x84_c\x87\xa3NAf\x13\xfc\x95\xa6\x8c\x92jS%\x89\xab\x9d\x0e\x8e4\x92V\x8c\xca\xb8\xa73x\xef\x8bD\xbc\x88\x9a\xdcy\xcc\xa6\xbb\x0f\xd9g?\xfb~\x98\xfe !ip\xc8\xae\xc14\xd3o\xa0\x04\xfe\xde\xb9R\xd0\x7f\xfdGF?\xcd\x94#g*T\x07\xb9Wl\xbc\xb4{\x96\xd3\xf3{TV\x00\xa0G}z6\xfa;/x\x87\x9ds\xd6\x1f\xe0\xd77\xd1\x00\xba4\x9c\xcf3h\xab\xe8L\x98\xdf\xbdw\xdff\xef~\xcfgl\xdb\x83\x07l*kXT\xa9Z\x0f\xa6^p\xe6\xd3\xed\xa4S\x8e!\x8a\x9ba\xd5\xe8\x17,4I*\x1e\xd5U+1\xd1\xd9\x8c\x9dy\xfaI\xf6\xda+.\xb7\xb1\xd5k\xbc\\\x96X\xbe P\'\xe2\xa0\xd6\x17i\xaa;s\x9b\xdd\xf0rRaf\xc4\xd0\x00\xaa\x11\x98\xae\x9a\xf2\xe0\xab\xc0q\xf2E\x1d\x95\xe7y7M\xaa+A  \xff\x88D\x0e\xce%\x9d\x85\xebdP\xbf\x1d\x8d\xd1$\xd1\xc3\xf2\x15W\x9d\xb3")\xe4}4\xee\x95A})\xa4\x04\xf3\xf5\x01\t\xfdX@QS\\\xd5Y\x8b\xfa\xa4\x0f\x04\xe7\x11\x95\x10Az_\xd4\xef\xb7z\xb6j\xe8D[\xbb\xfa$\x8ar&\x0b\x98\xab\xe6\x1bLM\xea\xaf\x7f\x90\xb1u(\xdf\x86\rk\x9c&\xa2\x06\x02\x82\x8e\x95ju\xbb\xe5\xee\xed\xf6\xb5\x7f\xb8\xdd\xbe\xf5\xed\x9f\xd9?~\xfb\xa7\xf6\x9d\x7f\xbc\xcb\xbe\xf6\xdd\xbb\xed\xeb\xdf\xbc\xdf\xfe\xf6\xeb\xf7\xdb\xdf}\xf3^\xfb\xc1\xcd?\xb3\xb6">\r\xaf\x9f\xee\xeb\xad2X\xa1yx\xe7z\x0fR~8#\xb2\xc8b&\x82$\xf4%"\x9f\x84\xcf\\LT\xaakM\x0eMvT\xb9p\xe1u\x81bx\x81\xba\xaf\x07\xbfJ\x01\x8d\xeb(\xc1\xf6X\xc2}\xabVa^\x05\x86\xc1$\xb1D\xd1\x91\x8ef\xfd\xd1\x1d\x8c\x96\xe8d\x86Z0[\x1eC\xbf7\x8d\x86\x11\x1c\xd8\x83\xd1\xee\xd2P\x1c\xf9*oO\xbb.Q\x94\x1e\xc4K\x18\xb5F\x990\xb0j\xc7n9\xc3\xd6\xac=\x95\x19m\xa0\x16t\x8a\x0eg\xc7\xdc\x1c\xca\x95Q5\xb1\xc6\xf0:{\xd9\xef>\xd7\x86\x86b\x1b\xab\xa2\x1e\xfa\x05\x8b\x8e\xbe}\xe5\xe0\xbd\xfa}\x9b\xec\xf5\xad\xc5\x18\xfa\xbe\x9bV\x84\x08Q\xf4\xd3\xcby\x1b\xf8(\xd0\x0c\xc2H^\xa8\xcf\\\xe9w\xc9\xfe\xdbdU\xf4OC\x05c"\x91\xb8q\xca[\x8b\x98\xa5C1\xa9\xa1\xd9~\x1c\\\xb8}\xebe\x1d\xff \x83\x96k\x82\xb9\x93v\xf5\xdbh1\xcd\xd4\xb2x\x196\xc5^&:\x01\xd5\x0f\xdc\x86k\x04\xb3%\x9b\xc2y\xcd\xa0\x89MVJ\x9fv\nG\xfdA6\xed|\x82\x08/\x8eXI-\x82\xdf\x99Q;\xfd\xa4\x8b\xed\xbcg]\x82_z\x06B\rG\xc2\xf3\xa6\xe4\xa6\xb0\x8c\x8d\xd6\xef\x98\x08\x0f\x1af/{\xf9k\xec\x85/=\xdf\x1a\xe5\x1e+f\xca*i\xc7\xaahr\x03>\xad\x86\xa6Qx]\'\xb8\xd07\xca\xd2\na\x04\x91Z5F\xe0RbW\x81\x02B>\xfe\xd8\xc7\xaf\xb9f\xe7\x8e\x1d\xf6\x8d\xebo\x820\xd9H-\xe7\xd4\xeaC\x91]q\xe5Kmhd51\x8a\x9e\xdch\n\xae\x16\xbeb\xf3\xec\xf2\xa0h?\xdb\x87~\xd2\xd3\xb5n\xb7e\x0f\xdd\xff3\x98\xdd\xb0\x91\xd1U\x10>\xc6dV[\xad\xb2\n-\x1b\x05G\xb0\x9d\xa3V\xa9\xaeF\x1b\xd7\xda\x14\x0b\xa5\xd9+\xc3\xf0:i\x03\x95\xa9\xb1\xa3\x1c\xb2\xf1\x91\xb56T]c\x95\x88\xb68\xfbri\xdc\x86\x876\xdb\xa6u\xa7\xd8\xd9g\xfc\xa6\x9d\xf7\xecW\xda\xe6-gc\x01\x8fA\xc0\x08\x90\xa9I\xc54\xb1\xc1iU\xe4@\xd1b\x9d\xaeV\x10\xe4\xf9\x17\\h\xc7\x9f\x88I%|l\xb0\xb9[\x05\x0e\r\xc76<V\xb1\xea*\x84\xc5\xaa+\xb73k"E\xf5W\x8b{\xb6\xf9\xf8q{\xe9\xcb\x9e\xcb\xf8c\xce\xd7\xb0\xffa\x1c9\xd7\xdbo\xf9\xb1]\xf5G\x1f\xb7\xf6>\x96%\xceA\xcbh\xd5\x9a\xb2}\xf7\xfb[m\xdd\xfacY\x05\xc5\xd7;\x84\xde\x0e\x1c\x94\xe2/\x0by\x1b\xf5\xa3>\n5\xa3\xaf\x8c\xcdE?\xd9g\xbbv>DA\x8b(@\x1f\x84\xd0\x0f\x8ee\x9a\x04\x85\x91\x91\t\xaaX\'\x89\xec\xba/~\xd9n\xfe\xc1O\xa1.f\x89\xc7\xd6\xa87\xec\x92\xdf9\xcd\xde\xf0\xea\x8b\xadVn`fP\x97\xa8J?}\xfa+[\xb5V\x83Q\xe3DQkQ\xb0c\xe8\x0eS\xa2\xf8\xbb\xea\x06\x8a\x9eQ\xdb\xc192\x92\xb6 \t\xed\xfb\t\x1c\xa8\x94\xad\xd5Lm\xea\xd0v\xa2\x99Ik\xb7\xd0n\xf9\x04\xcc\xb3\x8e\xc3w\xed\xddo\x1f\xfc\xd0\x97m\xf7\xae\x16\xbdU\xac\x91N\xdbs\x9ew\xb2}n\xeb\x07m\xe3Z}\x93L\xe3\xe8}$Vt\x88j`\xfc;?n3{\x91GZ!.e\xf9\x10\xd5\x84\xef\xd5\x88\xf1M\xaaJ-\xf4\xd3\x1b\xc0_;\x1ep\x90\x0eZ\x11\x850\x8a\xbcRA\x91\x1f\xbc\xafI\x16\xf7\xb9\x83\x9d\xd4\xc7\x82\xca5\xd9W\x9c\x90>\x0e\xa4:}\xbd\n\xc8\x90\xaa*\x13\x08#|\xa7Hz\xf5\x9b?`\xdf\xfd\xce\x8fm\xa8\xb1\xda\xf6\xb4\xba\xb6\xba^\xb37^y\x81\xbd\xf7}\x97\xd9\xd8\xaaM\xf8\x076f\xb1\xfa\x93\x0f\xc1\xc1\x91*\xe6)Y\x83>\xb1\x1fDh\xfa\x16\x8d\x9e\xa2\x85\x177T\x96\xcf\x11\x86&\xbd\t6r\xc4\xde\x99\xe6\n\xb3\xa8\x8bk\xa1\x1e\xab\x04\x81\xb9\xee`\xf5\xe4\x0b{\x10\xf9\xc8\xc3\x0f\xd9\xd5o\xbd\xd6\xee\xbf\x7f\x9fu\xd9\'d\xed\t{\xe1\xc5\xa7\xd9g\xb6~`\x80\xf1:6\x08\xf6\x03\x80\xad\xb2\xab\xd2m<\x96>\xb0S\xec8\xbds1L\xbf\x92\xf5\t\xd08\xcb\x1fk\xa9LQ\xcfa\xa8\xf2#\xa1:T\x1d\x11\xa1\xbe\x94\x87\x024\xb2\\\xd1\xbb\x94h\x9c\xde\xa7\xccVS\xce5B\x8e\xcahI\x0cs\xa2\xfd\\3\xb6\x87\xb3P\xd3n\xa3\xd9\xb1\xb5\xf1\xa4\x95j\xc3\x9a\xb4-Gc\xb0\x85\xf0\xb07di{\x8c\xc9\xd4-\xed\xd2W\x9a?\xc4\xce\x08\xeb\xfcc\x15t\xe3\n\xa47\x85\xf5i_\xe5\x07\xe8$\x1fW\xc4t\xbd\x99\xaa\xb7\x82\xf5\xf6\xf0A\xcc\xd6\x0c>p\x12E\xd0\xe7\x02d\t\xa4\x06T\xe1\x9f\x9eN\xf5\xbb\xfa\xf6$>\xa5\xcd\xbc\xa4-\xbd\x18\x0b\xa2\xfb\xf3aV\xe5\xd40A\x03\xa3\x04I*\x16\xd5\xd7\xcc\x00}\xceD\x0e1\x8d\xd0<$\xaeO?e\x92&\xd1I\xe6e\xda\xc9\nu\xaf\xc8\x0b\x07\xef\x15\xf9\x85\xf5\xe9K\xdbl\x86\xd0\xf7&\x03\xc2\xd4YD0eP\xa9\x8e\x1b\x98\x88\xf4U(\xa87\xb4+F|h\xb6^\xd2\xd3\x93Ei\xb4\xd7Co"v\x90N>\xb3\xf6v\x8ckz\xa9Vo$\x0f\xce\xc7#-\xcc\x0e\xf3\xd45\x92\x06\xb5\x12\x88\x96"\xe2v\xad\x84y(\xbf\xc0\x00\xf9\nv!\x16\xc8\xf0\x8a\xa8\xf4\xe60\xdbI\x840\xe87D\x8cv\xf6n?r@J\n\xbd*\xfa\xec6{^6\xb9\x1e\xc6\xa9\xa7>\x03\xf5\xb1}}f\xe1Ht\xd2\x87\xc8\xb9\xf2\xa5`\xde\x87\xf7#,t\xad\xb8.\xca\x14:j\x07[\x07\xc7\xc0q\xae\x85\x1a7bU\xe2\x8f\xba\x91\xcd\xb0\xbbm\xa0\x99\xdaL%\xfd\x1e\n\x12N\x0e\x15\xc6\xa1?\xd6/Rf\xea\xfd\xfa\xd8\xd0!\xda\x1d5\x97\x11\x1c3\xfdz\xb9\x02\xdb\xe0M\xb4yJ(\x0f\xe3\xe7\xc8*L\xa8\x9fd\xba\x16m\xd0\x08\xb3\xe5\xa5t\x1cQ\xd2\xb1\x00\xf4a\xc3\xe9\x81\x1ct\xcd1^ \xd3\xc7\x8a.v\xaeoz\xe7\x9f\xda\x81=\xb8\xb5)\xbd\xb0S\xb2M\x1b\x87\xed\x8b\xff\xed\xbd\xb6~C\xd8\xe6\xca\x97Jz.W\x89u\xb9P4\x1d\xa4\xa6\xc8\xd3\xafn{\xd4$\xd0\x85\x8f9\x1f4\x15\xbd\xeew\xed\xa7\xbef7\xde\xf8o\x1eFN\xe3#\xd6\x8d\x0c\xd9\x15\xbf\xf7\x02\xbb\xf2\xca\x8b\xadZg\xf2R\xabb<\xa5\x8e\x87\xf77\x07\xdc+\xea\xfb\x1c\xa1\'\xaf\xee\x89.\x84\xba\xd0}W\xcc\x80\x12\xd4\xce\xdd\xfb\xec\xfd\x7f\xf4E{\xe8\x91)+c1\xea\xf5\xae]p\xc1\x89v\xdd_}\xc0?\xf8\x19TJ\xc0\x8a\x99=${\xfb5vp/\x9aB\x087\x8cT\xa6;S\xb6aS\xd5\xba\x93;\xad\xcc\xa6F\x9f\xb8\xb5\x04{Is\xff\xf6\xa2L\x01]h\xdc\x85\xa9`\xb1|0\x030$\x9fM\xf8\x92*y\x0f\xe3\x82\x86\x08\xf4+\x8b\xe0WdA+\xdc\xd3.V\xe3\xb9.\xa1\xdd\x98\x87\xfa\x90\x1d<\xd8\x84\x0f\xfa\xdc\xa0jh\x8d\xa2w\tNvH\xcb\x19\xbd\xd5fP\x1b\x03=\x88A\xf3Jht\x88\xd1\x05\xa2Ec\x8a6\xd1\xa1\xb1d>\x02\xf8xz\x95\x8f8=|\x1f\x1e)\x12xhgMuQA^-1+q\x9f\xcd\x12\xf5\xa0\xab\xd9\xab\xd8\xe4\xb4\x9eI\xc46Ri\xdby\x17\x1eg[\xbf\xf0![\xbf\xf6\xd8\x9c\xf1a\xfc\xa8\xe7\xe1\xe4\xadD5\x9f\xb0\xc9\xbd\xf8}\xd9>\xd6\xa5~\xdbTJ&m\xb8\xa2\x0f&C$\x9d\xf6\xd9\xbd\xf6\x99\xa8\x84\xad\xd8^\xd6VS\x16\x04\x96\x84\xbc\xcfI\xcc\xcb\x19\\\xe4\x07\xb7\xe7\xb2\xb9\xb2\xcc\xeeC@\xb7\xdby\xf3Y\xf0\x81\xf4!ih\xa1\xad>\x16\xad*\x12\xbe\xbe\xac-;\xeb\xef\'j\xfb\x08\xa3\x1b8\xe8&\xb6E\x9f\xadj\xb5\x9b6\xca\x0e\xb8\x04\xf3\xaae\x82\x06\xccPx9#\xa7\x899\xe9\xdb3\x1a\xb9\x98\x89R\x81\x8b ,q\xea\xe9\xf4\xd4\xd9\xcb\x98\xfe\xe9g\xe9\x89\xcf\x89=\x9b\xb7\xac\xc2t\x17\x14\xc4\xe9\xfbd]}E\xbb\xdb\xb7F\xd4\xb4\x0b.:\xc9\xb6~\xfe\xc30^\xbf\x82\xd1\xfc\x03\xe3K\xddI\xdc\x05\n\x12\xb3\xfbKX\xd6\xa5\x84\xad\xbb\x9c\x99\xc7\xd0Uk\'5b\xd8:\x1d\xfa\xc7A\xf2 $\x04_\xd4\\\x14\xf5\xf9o\xc5\xd6\x9e\x0e\xe6\x19\xb4@\xd5\x13\x19\x8eL0\x85p}Hy\x10}\xf7L\x05\xd5\x91m\xd6\xb7\xbf\xd4\x97l\xbcf\xaf\'A\t\xb3G\x99\xc9\x8b\xe9\xa2\r]d\x0e\xb5\nL\xc2\xd6\xe8\r\x98\x19L\x91R\x8d)\xba\x85\xe1^\xe8S\xa9\xfa\xd4\xbcf\xe7\xc6x\xfa\xc0[\x97\x08\xa8\'f\xd2\xbf\xee\xf9\xd9\x15>\xc4\x0f\xdf\\g\xf4\x99s\xe2{\xf8\xd4Nu\xd6Dl\xd8o\xdb0;\\)gJ\x99\x82\x16\x89HA\xa4D\xe8\x98\x12\x80\xdey\xeb\x8f\xec\xaa?\xfc/6qH\x93\tR\x7f\n\x8e\x00p\xcd\x17\xb20\xbf(V\xb64^\x877\xfa\xb6p\x99\x08\xad\xd9k\xa1\xf1\xe7\xd8\xe7\xd0\xf8\x8d\xeb\xe6\x7f\xb8?\xea\xb6\xb2l\xfb#\xf7\xd8\xff\xfa\xca\xb7lJG\x06\xf9\x8d\xa7\xe0\xc8\xa0\x15\x18\x98/\xdb\x1f\x98_\xfc\xca[+"c\x1fP.\xeb\xa5\xde\x8e\x9d|\xea\tv\xe9k.\xb5\xf1\xf1\xf9\x0f\xb8\xa3\xd6L\x92\xa9\xd2\xcc\xcc$\xbbA\xd9\x9f\xa74\xfe\x89\xc0\xbfq\xefJ\x0e\xaf\x82\xd3\xc9\x19\x1f\x8e\x93\xe5\xcb\xfc\x1d|\x1d!sO\xfb\x8dF#\xdf\x11\xe7\x10\xb5\x9b\x1d\xf60e\x7f\x8f\xdb\xc3\xaf\xa7\xe0\tA\x1a\x1f\xfe\xce1\xac\xf85\xb8\xe4!\xa7\xdb\xedN\x10\x96c\xef\xeb\x8a\xdbUw\x01\xe3\t\xb3\xf8O\xe1!\xc2\xf3\xad\xb2 t\x1d:^\x98_\xacLp\xa4\xba\x82\xe5\xb4[J]\xc1r\xda-\xa5\xae /\xf7\xa3\x06\xa1\xca\x15\xa2\xea\x88%D+\xfa\xbf\x9d\xa9X\x91O\xe0\'A\x83\x8e\xa5+\xa3\xa1n\x0e8\xe7$\xd3\x03\x86\xf0\xa4\xac\xe8\xec\x17\r\xbc0\xbf\xb0\xae\xe0H\xed\x96RW\xb0\x9cvK\xa9+XN;\xa2>\xe7\x95@\x1a-\xc8\x19/\xdb\x82\xf6\x8b\xf1\xf3\xfb\xd1\x11D\xd1\x8f3\xde\xff\xd7,\x80\n\xe7n<\x05G\x0213h\xf2\x1c\xcf@i\xbc3\x1bX,B)\xee\xe5\x903^\xbbBI\xee)\xc6/\x17\xc4\xd7\x82\xdf\x0bx\xbc(<\xc5\xe9\xa3\x04\x83J\xae\xfcB\\\x089\xe3\xc3\xa1\xbe`PZ\x8b\xe5\x9f\xe8\xbe`0_\xc0R\xda-\xa5\xee ,\xa5\xddR\xea\x0e\x82\xcaf\x11\x8e.\x9a\x1f\xc0\xc5\xc1\xec\xff\x03\xc4I0\x9eev\xf5\x17\x00\x00\x00\x00IEND\xaeB`\x82'

class LineWidthDialog(QDialog):
    '''A window with a slider to set line width of annotations
    '''
    def __init__(self, allshapes=None, scene=None, parent=None):
        super(LineWidthDialog, self).__init__(parent)
        self.setWindowTitle("Line width editor")
        self.scene=scene
        self.allshapes=allshapes
        self.lwidth=allshapes[0].point_size
        
        self.form=QGridLayout(self)
        
        self.form.addWidget(QLabel("Please set line width"), 0, 0)

        self.slider=QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBothSides)
 
        self.slider.setMinimum(0)
        self.slider.setMaximum(10)
        self.slider.setValue(self.lwidth)
        self.form.addWidget(self.slider, 1, 0)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)

        self.form.addWidget(self.buttonBox,2,0)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)
        
    def extractInputs(self):   
        self.size = self.slider.value()
        if self.size != self.lwidth:
            self.scene.point_size=self.size
            for shape in self.allshapes:
                shape.point_size=self.size
        
class EpsilonSliderDialog(QDialog):
    '''A window with a slider to set attraction epsilon, i.e. pull the cursor
    to the first point of the shape if epsilon close
    '''
    def __init__(self, scene=None, parent=None):
        super(EpsilonSliderDialog, self).__init__(parent)
        self.setWindowTitle("Attraction epsilon editor")
        self.scene=scene
        
        self.epsilon=self.scene.epsilon
        
        self.form=QGridLayout(self)
        
        self.form.addWidget(QLabel("Please set epsilon"), 0, 0)

        self.slider=QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBothSides)
 
        self.slider.setMinimum(0)
        self.slider.setMaximum(2*self.epsilon)
        self.slider.setValue(self.epsilon)
        self.form.addWidget(self.slider, 1, 0)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)

        self.form.addWidget(self.buttonBox,2,0)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)
        
    def extractInputs(self):   
        self.newepsilon = self.slider.value()
        if self.newepsilon != self.epsilon:
            self.scene.epsilon=self.newepsilon
       
        


class PropertiesWindow(QDialog):
    '''A window that pops up on right click (see mousepressevent in qscene).
    Lets the user reassign an annotated ("closed") shape to a different label class.
    '''
    def __init__(self, shape=None, all_labels=[None], scene=None, parent=None):
        super(PropertiesWindow, self).__init__(parent)
        self.shape=shape
        self.points = self.shape.points
        self.objtype=self.shape.objtype
        self.label=self.shape.label
        self.all_labels=all_labels
        self.setWindowTitle("Properties editor")
        self.label_names=[label.name for label in all_labels if label is not None]
        
        self.form=QGridLayout(self)
        
        self.form.addWidget(QLabel("Object properties"), 0, 0)

        self.qbox=QComboBox(self)
        self.qbox.addItem(self.label)
        [self.qbox.addItem(label) for label in self.label_names if label != self.label]
        

        self.form.addWidget(QLabel("Type:"), 1, 0)
        self.form.addWidget(QLabel(self.objtype),1,1)
        self.form.addWidget(QLabel("Label:"), 2, 0)
        self.form.addWidget(self.qbox, 2, 1)
                
        
        button = QPushButton('Copy', self)
        button.clicked.connect(scene.copySelected)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        self.buttonBox.addButton(button, QDialogButtonBox.AcceptRole)
        self.form.addWidget(self.buttonBox,3,0)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)
            
    def extractInputs(self):
        oldlabel=self.shape.label
        newlabel=self.qbox.currentText()
        if oldlabel != newlabel:
            if oldlabel in self.label_names:
                self.all_labels[self.label_names.index(oldlabel)].untieShape(self.shape)
                newlabelclass=self.all_labels[self.label_names.index(newlabel)]
                newlabelclass.assignObject(self.shape)
        return

    
class LabelDialog(QDialog):
    '''Label editor form. Given # of new classes to initiate (nlabels) pops up
    a form with a line editor to name a class and a button to set label color.
    If nlabel=0, the form features only already initialized labels for editing.
    '''
    def __init__(self, nlabels=1, prelabels=None, parent=None):
        super(LabelDialog, self).__init__(parent)
        self.names=[]
        self.colors=[None for i in range(nlabels)]
        self.prelabels=prelabels
        self.setWindowTitle("Initialize labels")
        self.lineedits=[]
        
        
        self.form=QGridLayout(self)  
        self.form.addWidget(QLabel("Please give description of labels below:"), 0, 0)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        
        if prelabels is not None:
            self.prenames=[label.name for label in prelabels]
            self.precolors=[label.fillColor for label in prelabels]
            nprelabels=len(prelabels)
            self.colors=self.colors+nprelabels*[None]
            [self.addLabelInfo(index, prelabdata=[self.prenames[index], self.precolors[index]]) for index in range(nprelabels)]
            [self.addLabelInfo(index) for index in range(nprelabels,nprelabels+nlabels)]
            self.form.addWidget(self.buttonBox,2*(nprelabels+nlabels)+1,0)
        else:
            [self.addLabelInfo(index) for index in range(nlabels)]
            self.form.addWidget(self.buttonBox,2*nlabels+1,0)

        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)
        self.rejected.connect(self.clearInputs)

    def fillcolornone(self):
        if None in self.colors:
            ind=self.colors.index(None)
            fillcolor1=int(255*ind/len(self.colors))
            fillcolor2=int(255/len(self.colors))
            fillcolor3=255
            self.colors[self.colors.index(None)]=QColor(fillcolor1, fillcolor2, fillcolor3)
            self.fillcolornone()
        return

    def fillemptynames(self):
        indices = [i for i, name in enumerate(self.names) if name == '']
        for ind in indices:
            self.names[ind]='class'+str(ind+1)
        return

    def extractInputs(self):
        self.names=[lineedit.text() for lineedit in self.lineedits]
        self.fillemptynames()
        self.fillcolornone()
        return
    
    def clearInputs(self):
        self.names=[]
        self.colors=[None for i in range(len(self.colors))]
        if self.prelabels is not None:
            self.names=self.prenames
            self.colors=self.precolors
        return
    
    def addLabelInfo(self, labelindex, prelabdata=2*[None]):
        lineEdit=QLineEdit(self)
        button = QPushButton('Select color', self)
        labelname=QLabel('Label {} name'.format(labelindex+1))
        labelcolor=QLabel('Label {} color'.format(labelindex+1))
        
        if prelabdata[0] is not None:
            lineEdit.setText("{}".format(prelabdata[0]))
            color=prelabdata[1]
            self.colors[labelindex]=color
            palette = button.palette()
            role = button.backgroundRole()
            palette.setColor(role, color)
            button.setPalette(palette)
            button.setAutoFillBackground(True)
        
        button.clicked.connect(lambda: self.selectColor(labelindex))
            
        self.lineedits.append(lineEdit)
        self.form.addWidget(labelname, 2*labelindex+1,0)
        self.form.addWidget(lineEdit,2*labelindex+1,1)
        self.form.addWidget(labelcolor, 2*labelindex+2,0)
        self.form.addWidget(button,2*labelindex+2,1)

        
    def selectColor(self, labelindex):
        dialogue=QColorDialog()
        dialogue.exec()
        color=dialogue.selectedColor()
        self.colors[labelindex]=color
        
        button = QPushButton('Select color', self)
        palette = button.palette()
        role = button.backgroundRole()
        palette.setColor(role, color)
        button.setPalette(palette)
        button.setAutoFillBackground(True)
        button.clicked.connect(lambda: self.selectColor(labelindex))
        self.form.addWidget(button,2*labelindex+2,1)
        return


class ToolButton(QToolButton):
    '''Overwrite QToolButton to ensure all buttons are of same size
    '''
    minSize = (80, 80)
    def minimumSizeHint(self):
        ms = super(ToolButton, self).minimumSizeHint()
        w1, h1 = ms.width(), ms.height()
        w2, h2 = self.minSize
        ToolButton.minSize = max(w1, w2), max(h1, h2)
        return QSize(*ToolButton.minSize)

def process(filename, default=None):
    '''Return bytes for an image given its path
    '''
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default

def newAction(parent, text, slot=None, shortcut=None, icon=None,
        tip=None, checkable=False, enabled=True):
    '''Initialize an action with flags as requested'''
    a = QAction(text, parent)

    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def distance(delta):
    '''Squared euclidean distance as metric. Returns distance given an elementwise delta
    '''
    return (delta.x()**2 + delta.y()**2)

class LabelClass(object):
    '''Class to keep record of a label class characteristics with a method to
    assign shapes to it
    '''
    def __init__(self):
        self.polygons = []
        self.fillColor=None
        self.name=None

    def assignObject(self, obj):
        self.polygons.append(obj)
        obj.line_color=self.fillColor
        obj.label=self.name
        
    def untieShape(self, obj):
        self.polygons.pop(self.polygons.index(obj))


class Annotationscene(object):
    '''Class to store and save outputs as .csv and .json
    '''
    def __init__(self, filename=None):
        self.polygons = None
        self.imagePath = None
        self.imageData = None
        self.filename=None
        self.lineColor=None
        self.imsizes=None
        self.object_types=None
        self.labels=None
        self.savebytes=False
    
    def shapes_to_pandas(self):
        imsize, objects, types, labels = self.imsizes, self.shapes, self.object_types, self.labels
        df=pd.DataFrame(columns=['width', 'height', 'Object', 'X', 'Y'])
        for i, obj in enumerate(objects):
            X, Y=list(zip(*obj))
            df=df.append(pd.DataFrame({'width': imsize[0], 'height': imsize[1], 'Object': i+1, 'Type': types[i], 'Label': labels[i], 'X': X, 'Y': Y}), ignore_index=True)
        return df

    def save(self):

        self.shapes=[[(point.x(), point.y()) for point in poly] for poly in self.polygons]
        self.shapes_to_pandas().to_csv(re.search(re.compile('(.+?)(\.[^.]*$|$)'), self.filename).group(1)+'.csv', sep=',')
        if self.savebytes:
            self.imData = b64encode(self.imageData).decode('utf-8')
        
            try:
                with open(self.filename, 'w') as f:
    
                    json.dump({
                        'objects': self.shapes,
                        'type': self.object_types,
                        'label': self.labels,
                        'width/height': self.imsizes,
                        'lineColor': self.lineColor,
                        'imagePath': self.imagePath,
                        'imageData': self.imData},
                        f, ensure_ascii=True, indent=2)
            except:
                pass
        else:
            try:
                with open(self.filename, 'w') as f: 
                        json.dump({
                            'objects': self.shapes,
                            'type': self.object_types,
                            'label': self.labels,
                            'width/height': self.imsizes,
                            'lineColor': self.lineColor,
                            'imagePath': self.imagePath},
                            f, ensure_ascii=True, indent=2)
            except:
                pass

 

class Shape(QGraphicsItem):
    '''The main class controlling shape's points, its color, highlight behavior
    '''
    line_color = QColor(0, 6, 255)
    select_line_color = QColor(255, 255, 255)
    vertex_fill_color = QColor(0, 255, 0, 255)
    hvertex_fill_color = QColor(255, 0, 0)
    point_size = 1.5
    hsize = 3.0

    def __init__(self, line_color=None, point_size=None, parent=None):
        super(Shape, self).__init__(parent)
        self.points = []
        self.selected = False
        self.painter = QPainter()
        self.hIndex = None
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.closed = False
        self.points_adjusted=None
        self.objtype=None
        self.label=None
        
        if line_color is not None:
            self.line_color = line_color

        if point_size is not None:
            self.point_size = point_size

    def addPoint(self, point):
        self.setSelected(True)
        if self.points and point == self.points[0]:
            self.closed = True
        else:
            self.points.append(point)

    def popPoint(self):
        if self.points:
            return self.points.pop()
        return None

    def paint(self, painter, option, widget):

        if self.points:
            self.prepareGeometryChange()
            color = self.select_line_color if self.selected else self.line_color
            pen = QPen(color)
            pen.setWidth(self.point_size/2)
            painter.setPen(pen)
            path=self.shape()
            if self.closed == True:
                path.closeSubpath()
            painter.drawPath(path)
            vertex_path=QPainterPath()
            self.drawVertex(vertex_path, 0)
            [self.drawVertex(vertex_path, i) for i in range(len(self.points))]
            painter.drawPath(vertex_path)
            painter.fillPath(vertex_path, self.vertex_fill_color)


    def drawVertex(self, path, index):
        psize = self.point_size
        if index == self.hIndex:
            psize = self.hsize
        if self.hIndex is not None:
            self.vertex_fill_color = self.hvertex_fill_color
        else:
            self.vertex_fill_color = Shape.vertex_fill_color
        path.addEllipse(self.mapFromScene(self.points[index]), psize, psize)
 

    def shape(self):
        path = QPainterPath()
        polygon=self.mapFromScene(QPolygonF(self.points))
        path.addPolygon(polygon)
        return path

    def boundingRect(self):
        return self.shape().boundingRect()

    def moveBy(self, tomove, delta):
        if tomove=='all':
            tomove=slice(0,len(self.points))
        else:
            tomove=slice(tomove,tomove+1)
        self.points[tomove] = [point + delta for point in self.points[tomove]]

    def highlightVertex(self, index):
        self.hIndex = index

    def highlightClear(self):
        self.hIndex = None
        self.selected = False

    def __len__(self):
        return len(self.points)

    def __getitem__(self, index):
        return self.points[index]

    def __setitem__(self, index, value):
        self.points[index] = value


CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT   = Qt.PointingHandCursor
CURSOR_DRAW    = Qt.CrossCursor
CURSOR_MOVE    = Qt.ClosedHandCursor
CURSOR_GRAB    = Qt.OpenHandCursor

class SubQGraphicsScene(QGraphicsScene):
    '''Overwrite QGraphicsScene to prescribe actions to mouse events, 
    collect annotated shapes and label classes, tracks which mode the program is in
    at any moment (drawing, navigating, moving)
    '''
    NAVIGATION, DRAWING, MOVING = 0, 1, 2
    POLYDRAWING, POLYREADY = 0, 1
    epsilon=30.0
    def __init__(self, parent=None):
        super(SubQGraphicsScene, self).__init__(parent)
        self.mode=self.NAVIGATION
        self.QGitem=None
        self.polys=[]
        self._cursor = CURSOR_DEFAULT
        self.overrideCursor(self._cursor)
        self.line=None
        self.lineColor=QColor(3,252,66)
        self.shapeColor=QColor(0, 6, 255)
        self.selectedVertex=None
        self.selectedShape=None
        self.polystatus=self.POLYDRAWING
        self.objtypes=[]
        self.labelclasses=[]
        self.labelmode=0 #the default class
        self.initializeClass('default', QColor(0, 6, 255)) #initialize default class
        self.point_size=1.5
        
    def drawing(self):
        return self.mode == self.DRAWING

    def navigating(self):
        return self.mode == self.NAVIGATION

    def moving(self):
        return self.mode == self.MOVING

    def polygon_not_finished(self):
        return self.polystatus == self.POLYDRAWING

    def polygonfinished(self):
        return self.polystatus == self.POLYREADY

    def vertexSelected(self):
        return self.selectedVertex is not None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()
        if event.key() == Qt.Key_K:
            self.copySelected()
        if (event.key() == Qt.Key_Z) and (QApplication.keyboardModifiers() == Qt.ControlModifier):
        	self.undoAction()

    

    def undoAction(self):
        if self.QGitem:
        	if len(self.QGitem.points) > 1:
        		self.QGitem.popPoint()
        		self.line.points[0]=self.QGitem.points[-1]
        		self.update()
        	else:
	            self.removeItem(self.QGitem)
	            if self.line:
	            	if self.line in self.items():
	                	self.removeItem(self.line)
	                
	            	self.line.popPoint()
	            self.polystatus=self.POLYREADY
	            self.QGitem = None
	            self.update()

    def refreshShapestoLabels(self, labelclass):
        labelpolygons=labelclass.polygons
        labelclass.polygons=[]
        [labelclass.assignObject(shape) for shape in labelpolygons]
        return

    def initializeClasses(self, names, colors):
        for c, name in enumerate(names):
            if (c<len(self.labelclasses)):
                self.initializeClass(name, colors[c], labelclass=self.labelclasses[c])
                self.refreshShapestoLabels(labelclass=self.labelclasses[c])
            else:
                self.initializeClass(name, colors[c])

    def updateColor(self, color):
        self.shapeColor=color
        active_labelclass=self.labelclasses[self.labelmode]
        active_labelclass.fillColor=self.shapeColor
        self.refreshShapestoLabels(labelclass=active_labelclass)
        return

    def setLabelMode(self, classindex):
        labelclass=self.labelclasses[classindex]
        self.labelmode=classindex
        self.shapeColor=labelclass.fillColor
        return
        
        
    def initializeClass(self, name, color, labelclass=None):
        ind=None
        if labelclass is None:
            labelclass=LabelClass()
        else:
            ind=self.labelclasses.index(labelclass)
        labelclass.name=name
        labelclass.fillColor=color
        if ind is not None:
            self.labelclasses[ind]=labelclass
        else:
            self.labelclasses.append(labelclass)

    def triggerClosure(self):
        self.finalisepoly(premature=True)

    def mousePressEvent(self, event):
        '''Draw, move vertices/shapes, open properties window'''
        pos = event.scenePos()

        if (event.button() == Qt.RightButton):
            if self.selectedShape:
                all_labels=[None]
                if len(self.labelclasses) > 0:
                    all_labels=self.labelclasses
                propdialog=PropertiesWindow(shape=self.selectedShape, all_labels=all_labels, scene=self)
                propdialog.move(event.screenPos())
                propdialog.exec()

        if self.drawing() & (event.button() == Qt.LeftButton):
            self.overrideCursor(CURSOR_DRAW)
            #update the tail of the pointing line
            if self.line and self.polygon_not_finished():
                self.line.points[0]=pos
                self.line.setPos(pos)
            #initialize a pointing line for a new polygon
            elif self.line==None or self.polygonfinished():
                self.line=Shape(point_size=self.point_size)
                self.addItem(self.line)
                self.line.setPos(pos)
                self.line.addPoint(pos)

            if self.QGitem:
                #attract the cursor to the start point of the polygon and close it
                if len(self.QGitem.points) > 1 and self.closeEnough(pos, self.QGitem.points[0]):

                    pos = self.QGitem.points[0]
                    self.overrideCursor(CURSOR_POINT)
                    self.QGitem.highlightVertex(0)

                self.QGitem.addPoint(pos)
                if (self.QGitem.points[0]==pos):
                    self.finalisepoly()


            else:
                self.polystatus=self.POLYDRAWING
                self.QGitem=Shape(point_size=self.point_size)

                self.addItem(self.QGitem)
                self.QGitem.setPos(pos)
                self.QGitem.addPoint(pos)
                self.QGitem.setZValue(len(self.polys)+1)
            self.update()
            event.accept()

        elif self.moving() & (event.button() == Qt.LeftButton):
            self.overrideCursor(CURSOR_GRAB)
            self.selectShapebyPoint(pos)
            self.prevPoint=pos
            event.accept()
            self.update()

        elif self.navigating():
            self.overrideCursor(CURSOR_GRAB)
            self.update()


    def mouseMoveEvent(self, event):
        '''Track the movement of the cursor and update selections/drawings'''
        pos = event.scenePos()

        if self.drawing():
            self.overrideCursor(CURSOR_DRAW)

            if self.QGitem:

                if len(self.QGitem.points)==1:  #initialize the pointing line collapsed to a point
                    self.line.points=[self.QGitem.points[0], self.QGitem.points[0]]
                colorLine = self.lineColor
                if len(self.QGitem) > 1 and self.closeEnough(pos, self.QGitem[0]):
                    pos = self.QGitem[0]
                    colorLine = self.QGitem.line_color
                    self.overrideCursor(CURSOR_POINT)
                    self.QGitem.highlightVertex(0)

                if len(self.line.points)==2: #update the pointing line
                   self.line.points[1]=pos
                else: #load the pointing line (if another shape was just created)
                   self.line.addPoint(pos)

                self.line.line_color = colorLine
                self.update()
            return

        #moving shapes/vertices
        if self.moving and Qt.LeftButton & event.buttons():
            self.overrideCursor(CURSOR_GRAB)
            if self.vertexSelected():
                if (self.selectedShape.objtype=='Line') and (QApplication.keyboardModifiers() == Qt.ShiftModifier):
                    self.moveShape(self.selectedShape, pos)
                else:
                    self.moveVertex(pos)
                self.update()
            elif self.selectedShape and self.prevPoint:
                self.moveShape(self.selectedShape, pos)
                self.update()
            return


        #update selections/highlights based on cursor location

        #check if any vertex is epsilon close to the cursor position and find the corresponding shape
        id_point=[[i for i, y in enumerate(poly.points) if distance(pos-y)<=self.epsilon] for poly in self.polys]
        id_shape=[i for i, y in enumerate(id_point) if y != []]

        itemUnderMouse=self.itemAt(pos, QTransform())
        
        #if shape/vertex combination found, highlight vertex and shape
        if id_shape != []:
            self.selectedVertex=id_point[id_shape[0]][0]
            self.selectShape(self.items()[:-1][::-1][id_shape[0]])
            self.selectedShape.highlightVertex(self.selectedVertex)
            self.update()
            return
        elif itemUnderMouse in self.items()[:-1]: #if the cursor is inside of a shape, highlight it
            self.selectedVertex = None
            self.selectShape(itemUnderMouse)
            self.selectedShape.hIndex=None
            self.update()
            return
        else:#nothing found: no shape under the cursor, no vertices in vicinity, clear all
            self.clearShapeSelections()
            self.selectedVertex = None
            self.update()
            return

        event.accept()

    def mouseReleaseEvent(self,event):
        if self.navigating or (event.button() == Qt.LeftButton and self.selectedShape):
            self.overrideCursor(CURSOR_DEFAULT)
            self.update()
        event.accept()

    def closeEnough(self, p1, p2):
        return distance(p1 - p2) < self.epsilon

    def finalisepoly(self, premature=False):
        if self.QGitem:
            if premature:
                if len(self.QGitem.points)==1:
                    self.objtypes.append('Point')
                    self.QGitem.objtype='Point'
                else:
                    self.objtypes.append('Line')
                    self.QGitem.objtype='Line'
            else:
                self.objtypes.append('Polygon')
                self.QGitem.objtype='Polygon'
            if self.line:
                self.removeItem(self.line)
                self.line.popPoint()
            self.polys.append(self.QGitem)
            if self.labelmode is not None:
                labelobject=self.labelclasses[self.labelmode]
                labelobject.assignObject(self.QGitem)
                self.QGitem.label=labelobject.name
            self.QGitem = None
            self.polystatus=self.POLYREADY
            self.update()

    def overrideCursor(self, cursor):
        self._cursor = cursor
        QApplication.setOverrideCursor(cursor) 

    def copySelected(self):

        if self.selectedShape:
            shape = self.selectedShape
            c,o,s =[shape.closed, shape.objtype, shape.point_size]
            p=[point for point in shape.points]
            
            newshape=Shape()
            
            newshape.points, newshape.closed, newshape.objtype, newshape.point_size = p, c, o, s

            self.polys.append(newshape)
            self.objtypes.append(newshape.objtype)
            
            newshape.setZValue(len(self.polys)+1)
            self.addItem(newshape)
            
            labelid=[label.name for label in self.labelclasses].index(shape.label)
            self.labelclasses[labelid].assignObject(newshape)

            print('Shape copied')
            self.clearShapeSelections()
            self.selectShape(newshape)
            self.update()
            return


    def deleteSelected(self):
        if self.selectedShape:
            shape = self.items()[:-1][::-1].index(self.selectedShape)
            if self.selectedShape in self.polys:
                self.polys.pop(shape)
                self.objtypes.pop(shape)
            self.removeItem(self.selectedShape)
            if self.line:
                self.removeItem(self.line)
                self.line.popPoint()
            labelind=self.findShapeInLabel(self.selectedShape)
            if len(labelind) > 0:
                label, shapeind = labelind[0]
                self.labelclasses[label].polygons.pop(shapeind)
            self.polystatus=self.POLYREADY
            self.selectedShape = None
            self.QGitem = None
            self.clearShapeSelections()
            print('Shape deleted')
            self.update()
            return

    def findShapeInLabel(self, shape):
        if len(self.labelclasses) > 0:
            labelpolys=[l.polygons for l in self.labelclasses]
            return ([(i, label.index(shape)) for i, label in enumerate(labelpolys) if shape in label])
        else:
            return 2*[None]            



    def selectShape(self, shape):
        shape.selected = True
        self.selectedShape = shape
        self.update()

    def selectShapebyPoint(self, point):
        """Select the first shape created which contains this point."""
        if self.vertexSelected(): # A vertex is marked for selection.
            self.selectedShape.highlightVertex(self.selectedVertex)
            return

        itemUnderMouse=self.itemAt(point, QTransform())

        if itemUnderMouse in self.items()[:-1]:
            self.selectShape(itemUnderMouse)
            return

    def clearShapeSelections(self):
        if self.selectedShape:
            self.selectedShape.highlightClear()
            self.selectedShape = None
            self.update()

    def moveVertex(self, pos):
        self.selectedShape.moveBy(self.selectedVertex, pos - self.selectedShape[self.selectedVertex])


    def moveShape(self, shape, pos):
        delta = pos - self.prevPoint
        if delta:
            shape.moveBy('all', delta)
            self.prevPoint = pos
            self.update()
            return True
        return False


class QViewer(QGraphicsView):
    '''Initializes the scene, sets images, controls wheel event
    '''
    def __init__(self, parent=None):
        super(QViewer, self).__init__(parent)
        self.scene = SubQGraphicsScene()
        self.photo = QGraphicsPixmapItem()
        self.photo.setZValue(-1)
        self.scene.addItem(self.photo)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        self.pixmap = QPixmap()



    def setPhoto(self, pixmap=None):

        if pixmap and not pixmap.isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.photo.setPixmap(pixmap)
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
            self.pixmap=pixmap
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.photo.setPixmap(QPixmap())

    def wheelEvent(self, event):
        if not self.photo.pixmap().isNull():

            factor=1.1
            if event.angleDelta().y() > 0:
                QGraphicsView.scale(self,factor,factor)
            else:
                QGraphicsView.scale(self,1/factor,1/factor)


class MainWindow(QMainWindow):
    '''A window with 3 menu tabs, 2 list widgets on the right and a toolbar
    populated with buttons on the left. Initializes and defines actions, connects
    them to the scene
    '''
    def __init__(self):
        super(MainWindow, self).__init__()
        self.imageData = None
        self.imagePath = None
        self.imsizes = None
        self.viewer = QViewer(self)
        self.viewer.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setCentralWidget(self.viewer)
        self.annotationscene=Annotationscene()
        self.shapestoload=None
        self.imname=None
        self.imlist=[]
        self.currentPath=None
        self.object_types=None
        self.savebytes=False
        
        
        self.currentlabel=None
        self.modedict={0: 'navigation', 1: 'drawing', 2: 'moving'}
        
        self.labelnames=None
        self.labelcolors=None

        self.statusbar = self.statusBar()

        self.fileListWidget = QListWidget()
        self.fileListWidget.itemDoubleClicked.connect(self.imagenameDoubleClicked)
        filelistLayout = QVBoxLayout()
        filelistLayout.setContentsMargins(0, 0, 0, 0)
        filelistLayout.addWidget(self.fileListWidget)
        fileListContainer = QWidget()
        fileListContainer.setLayout(filelistLayout)
        self.filedock = QDockWidget(u'Image List', self)
        self.filedock.setObjectName(u'Images')
        self.filedock.setWidget(fileListContainer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filedock)
        
        self.labelListWidget = QListWidget()
        self.labelListWidget.itemDoubleClicked.connect(self.labelDoubleClicked)
        labellistLayout = QVBoxLayout()
        labellistLayout.setContentsMargins(0, 0, 0, 0)
        labellistLayout.addWidget(self.labelListWidget)
        labelListContainer = QWidget()
        labelListContainer.setLayout(labellistLayout)
        self.labeldock = QDockWidget(u'Label List', self)
        self.labeldock.setObjectName(u'Label')
        self.labeldock.setWidget(labelListContainer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.labeldock)


        action = partial(newAction, self)
        quitaction = action('&Quit', self.close, 'Ctrl+Q', 'quit', 'Quit application')
        openshort = action('&Open', self.handleOpen,'Ctrl+O', 'open', 'Open image')
        save = action('&Save', self.saver,
           'Ctrl+S', 'save', 'Save labels to file', enabled=True)
        linecolorselect = action('&Select drawing line color', self.setLineColor, 'Ctrl+G')
        shapecolorselect = action('&Select active class line color', self.setShapeColor, 'Ctrl+H')
        setEditing = action('&Drawing Mode', self.setEditing, 'E', 'Drawing', 'Enable drawing mode')
        setMoving = action('&Moving Mode', self.setMoving, 'M', 'Moving', 'Enable moving mode')
        setNavigating = action('&Navigation Mode', self.setNavigating, 'N', 'Navigating', 'Enable navigation mode')
        setClosed = action('&Annotation complete', self.setClosure, 'C', 'Closing shape', 'Complete current annotation')
        initLabels = action('&Edit labels', self.initLabels, 'I', 'Label classes initialized', 'Edit label classes')
        setwidth = action('&Set line width', self.openLineWidthSlider, 'L', 'Line width set', 'Set line width')
        setepsilon = action('&Set attraction epsilon', self.openEpsilonSlider, '[', 'Epsilon set', 'Set epsilon')
        saveoriginal = QAction('&Save original image bytes', self, checkable=True, shortcut="]", triggered=self.checkaction)
        #copySelected = action('&Copy', self.copySelected, 'K', 'Copy', 'Copy')
        
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')
        modesMenu = menubar.addMenu('Modes')
        
        self.actions_to_menus(fileMenu, [openshort, save, saveoriginal, quitaction])
        self.actions_to_menus(editMenu, [initLabels, setwidth, setepsilon, shapecolorselect, linecolorselect])
        self.actions_to_menus(modesMenu, [setEditing, setMoving, setNavigating, setClosed])
        
        self.toolbar=QToolBar()
        self.toolbar.clear()
        [self.addbutton(self.toolbar, action) for action in [openshort, save, setEditing, setMoving, setNavigating, setClosed, initLabels, shapecolorselect, linecolorselect, quitaction]]
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)


    def updateStatusBar(self, saving=False):
        action='LOADED'
        if saving:
            action='SAVED'
        if self.currentlabel is not None:
            self.statusbar.showMessage('{} | {} | {}'.format(action+': '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], 'LABEL: '+ self.currentlabel))
        else:
            self.statusbar.showMessage('{} | {} | {}'.format(action+': '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], ''))
        return

    def checkaction(self, checked=False):
        if checked:
            self.savebytes=True
        else:
            self.savebytes=False

    def openLineWidthSlider(self):
        polys=self.viewer.scene.polys
        if len(polys) > 0:
            dialog=LineWidthDialog(allshapes=polys, scene=self.viewer.scene)
            dialog.exec()

    def openEpsilonSlider(self):
        dialog=EpsilonSliderDialog(scene=self.viewer.scene)
        dialog.exec()
            

    def labelDoubleClicked(self, item=None):
        index=self.labelListWidget.indexFromItem(item).row()
        self.viewer.scene.setLabelMode(index)
        self.currentlabel=item.text()
        self.updateStatusBar()
        return

    def initLabels(self):
        text, okPressed = QInputDialog.getText(self, "Initialize labels", "How many NEW labels to create (type 0 to edit existing list)?", QLineEdit.Normal, "")
        if okPressed and text != '':
            dialog=LabelDialog(nlabels=int(text), prelabels=self.viewer.scene.labelclasses)
            dialog.exec()
            self.labelnames=dialog.names
            self.labelcolors=dialog.colors
            
            self.initlabclasses()
            self.populateLabelList()
            
        return


    def initlabclasses(self):
        self.viewer.scene.initializeClasses(self.labelnames,self.labelcolors)

    def addbutton(self, toolbar, action):
        btn = ToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(toolbar.toolButtonStyle())
        toolbar.addWidget(btn)
        toolbar.addSeparator()

    def setClosure(self):
        self.viewer.scene.triggerClosure()

    def setEditing(self):
        self.viewer.scene.mode=self.viewer.scene.DRAWING
        self.viewer.scene.overrideCursor(CURSOR_DRAW)
        self.updateStatusBar()
        return

    def setMoving(self):
        self.viewer.scene.mode=self.viewer.scene.MOVING
        self.viewer.scene.overrideCursor(CURSOR_GRAB)
        self.updateStatusBar()
        return

    def setNavigating(self):
        self.viewer.scene.mode=self.viewer.scene.NAVIGATION
        self.viewer.scene.overrideCursor(CURSOR_GRAB)
        self.updateStatusBar()
        return

    def imagenameDoubleClicked(self, item=None):
        path=self.currentPath+item.text()
        dialog=QMessageBox()
        dialogq=dialog.question(self, "Save image?", 'Would you like to save the current image first?', QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
       
        if dialogq == QMessageBox.Yes:
             self.saver()
        elif dialog.rejected:
            if dialogq == QMessageBox.No:
                return self.handleOpen(path=path)
            return
        
        return self.handleOpen(path=path)

    def saver(self):
        dialogue=QFileDialog()
        dialogue.setLabelText(QFileDialog.Accept, "Save")
        if sys.platform=='darwin':
            dialogue.setOption(QFileDialog.DontUseNativeDialog)
        dialogue.setNameFilter("*.json")
        dialogue.setDefaultSuffix('json')
        dialogue.selectFile(self.imname)
        dialogue.exec()
        savepath=dialogue.selectedFiles()
        if savepath:
            return self.saveFile(filename=savepath[0], polygons=self.viewer.scene.polys, object_types=self.viewer.scene.objtypes,
                                 labels=self.labelAssigner(), colors=[shape.line_color.name() for shape in self.viewer.scene.polys])
   
    def labelAssigner(self):
        if len(self.viewer.scene.labelclasses) > 0:
            shapetolabel=[]
            for shape in self.viewer.scene.polys:
                l=self.viewer.scene.findShapeInLabel(shape)
                if len(l)>0:
                    shapetolabel.append(self.viewer.scene.labelclasses[l[0][0]].name)
                else:
                    shapetolabel.append(None)
            
        else:
            shapetolabel=len(self.viewer.scene.polys)*[None]
        return shapetolabel
        
        
    def selectColor(self):
        dialogue=QColorDialog()
        dialogue.exec()
        color=dialogue.selectedColor()
        return color

    def setLineColor(self):
        self.viewer.scene.lineColor=self.selectColor()

    def setShapeColor(self):
        self.viewer.scene.updateColor(self.selectColor())
        self.populateLabelList()

    def actions_to_menus(self,menu,actions):
        for x in actions:
            menu.addAction(x)
        return

    def imageIdentifier(self, path):
        exts=['png', 'jpeg', 'tif', 'tiff', 'bmp', 'json', 'jpg']
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.split(".")[-1].lower() in exts]
        return files

    def populateLabelList(self):
        labellist = [label.name for label in self.viewer.scene.labelclasses]
        colors=[label.fillColor for label in self.viewer.scene.labelclasses]
           
        self.labelListWidget.clear()
        [self.labelListWidget.addItem(label) for label in labellist]
        [self.labelListWidget.item(i).setForeground(colors[i]) for i in range(len(colors))]
        return
    

    def populateImageList(self):
        self.imlist = self.imageIdentifier(self.currentPath)
        self.fileListWidget.clear()
        [self.fileListWidget.addItem(im) for im in self.imlist]
        return

    def handleOpen(self, path=None):
        self.resetState()
        if not path:
            dialog=QFileDialog()
            if sys.platform=='darwin':
                dialog.setOption(QFileDialog.DontUseNativeDialog)
            path = dialog.getOpenFileName(
                self, 'Choose Image')[0]
        
        if path:
            self.imagePath=path
            path_decomposed=re.search(re.compile('^(.+\/)*(.+)\.(.+)$'), self.imagePath)
            self.imname=path_decomposed.group(2)
            self.currentPath=path_decomposed.group(1)
            self.populateImageList()
            
            if path.endswith('.json'):
                self.loadjson(path, jsonfile=True)
            else:
                self.imageData = process(path, None)
                dialog=QMessageBox.question(self, "Label file?", 'Do you have a label file for this image?', QMessageBox.Yes|QMessageBox.No)
                if dialog == QMessageBox.Yes:
                    dialog=QFileDialog()
                    if sys.platform=='darwin':
                        dialog.setOption(QFileDialog.DontUseNativeDialog)
                    labelfilepath = dialog.getOpenFileName(self,
   "Select label file", path, "Label Files (*.json)")[0]
                    self.loadjson(labelfilepath)
            
            image = QImage.fromData(self.imageData)
            self.imsizes=(image.size().width(), image.size().height())
            self.viewer.setPhoto(QPixmap.fromImage(image))

            self.loadShapes(self.shapestoload, self.object_types)
            self.populateLabelList()
            self.annotationscene.imagePath=self.imagePath
            self.annotationscene.imageData=self.imageData
            self.annotationscene.imsizes=self.imsizes
            self.updateStatusBar()


    def loadjson(self, filename, jsonfile=False):
        try:
            with open(filename, 'rb') as f:
                
                data = json.load(f)
                self.lineColor = data['lineColor']
                self.shapestoload = data['objects']
                self.object_types = data['type']
                self.labels = data['label']
                
                
                if jsonfile:
                    self.imagePath = data['imagePath']
                    if 'imageData' in data:
                        self.imageData = b64decode(data['imageData'])
                    else:
                        self.imageData=process(self.imagePath, None)
                        if self.imageData is None:
                            self.imagePath = QFileDialog.getOpenFileName(self,
   "Please select corresponding image", "Images")[0]
                            self.imageData=process(self.imagePath, None)
                    
        except:
            pass

    def resetState(self):
        if self.imageData:
            self.imageData=None
            self.shapestoload=None
            self.object_types=None
            self.viewer.scene.objtypes=[]
            [self.viewer.scene.removeItem(item) for item in self.viewer.scene.items()[:-1]]
            self.viewer.scene.polys=[]
            for labelclass in self.viewer.scene.labelclasses:
                labelclass.polygons=[]
            self.viewer.scene.update()
            self.viewer.viewport().update()
            return

    def loadShapes(self, polygons, types):
        if self.shapestoload:
            
            if isinstance(self.lineColor[0],str):
                self.lineColor=[QColor(color) for color in self.lineColor]
            self.viewer.scene.labelclasses=[]
            labellist=list(zip(self.labels, self.lineColor))
            labellistuniques=[]
            [labellistuniques.append(x) for x in labellist if x not in labellistuniques]
            labellistuniques=list(zip(*labellistuniques))
            self.labelnames,self.labelcolors = list(labellistuniques[0]),list(labellistuniques[1])
            self.initlabclasses()
            labeldict={self.labelnames[c]: label for c,label in enumerate(self.viewer.scene.labelclasses)}
            
            for ps in range(len(polygons)):
                polygon=Shape()
                polygon.points=[QPointF(p[0], p[1]) for p in polygons[ps]]
                
                objtype=types[ps]
                if objtype=='Polygon':
                    polygon.closed=True
                polygon.objtype=objtype
                
                self.viewer.scene.polys.append(polygon)
                self.viewer.scene.objtypes.append(objtype)
                self.viewer.scene.addItem(polygon)
                labeldict[self.labels[ps]].assignObject(polygon)


    def saveFile(self, filename, polygons, object_types, labels, colors):
        self.annotationscene.polygons=polygons
        self.annotationscene.filename=filename
        self.annotationscene.lineColor=colors
        self.annotationscene.object_types=object_types
        self.annotationscene.labels=labels
        self.annotationscene.savebytes=self.savebytes
        self.annotationscene.save()
        self.populateImageList()
        self.updateStatusBar(saving=True)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyleSheet("QToolButton { background-color: gray; }\n"
              "QToolButton:pressed { background-color: green; }\n"
              "QToolButton:hover { color: white }\n")
    app.setWindowIcon(QIcon(QPixmap.fromImage(QImage.fromData(iconbytes))))
    #app.setWindowIcon(QIcon('icon.PNG'))
    window = MainWindow()
    window.setWindowTitle('pyimannotate')
    #window.setWindowState(Qt.WindowFullScreen)
    screenGeometry = QApplication.desktop().screenGeometry()
    x = screenGeometry.width()
    y = screenGeometry.height()
    window.setGeometry(QRect(x/10, y/10, x/1.2, y/1.2))

    if sys.platform=='win32':
        import ctypes
        myappid = 'duke.pyimannotate.2'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
    window.show()
    sys.exit(app.exec_())
