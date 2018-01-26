import pandas as pd
import numpy as np
from skimage.draw import polygon, line
import json
from PyQt5.QtWidgets import QFileDialog, QApplication

def produce_mask(path):
	df=pd.read_csv(path)
	img=np.zeros((df['width'][0], df['height'][0]))
	U=df['Object'].unique()
	for i in U:
		dfsubstr=df[df['Object']==i]
		if dfsubstr['Type'].values[0]=='Polygon':
			cc,rr=polygon(dfsubstr['X'].values, dfsubstr['Y'].values)
			img[rr,cc]=1
		elif dfsubstr['Type'].values[0]=='Line':
			for j in range(dfsubstr.shape[0]-1):
				r0, c0 = int(dfsubstr['X'].values[j]), int(dfsubstr['Y'].values[j])
				r1, c1 = int(dfsubstr['X'].values[j+1]), int(dfsubstr['Y'].values[j+1])
				cc,rr=line(r0, c0, r1, c1)
				img[rr,cc]=1
		else: #A point
			img[int(dfsubstr['X']),int(dfsubstr['Y'])]=1
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
