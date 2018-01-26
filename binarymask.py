import pandas as pd
import numpy as np
from skimage.draw import polygon
import json
from PyQt5.QtWidgets import QFileDialog, QApplication

def produce_mask(path):
	df=pd.read_csv(path)
	img=np.zeros((df['width'][0], df['height'][0]))
	U=df['Object'].unique()
	for i in U:
		dfsubstr=df[df['Object']==i]
		cc,rr=polygon(dfsubstr['X'].values, dfsubstr['Y'].values)
		img[rr,cc]=1
	np.savez_compressed(path[:-4], img)
	return

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	dialogue=QFileDialog()
	dialogue.setNameFilter("*.csv");
	dialogue.setDefaultSuffix('csv')
	dialogue.setFileMode(QFileDialog.ExistingFiles)
	dialogue.exec()
	path=dialogue.selectedFiles()

	[produce_mask(p) for p in path]