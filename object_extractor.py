import json
from PyQt5.QtWidgets import QFileDialog, QApplication
import pandas as pd

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    dialogue=QFileDialog()
    dialogue.setNameFilter("*.json");
    dialogue.setDefaultSuffix('json')
    dialogue.exec()
    path=dialogue.selectedFiles()[0]

    def extract_polygons(filename):
        try:
            with open(filename, 'rb') as f:
                data = json.load(f)
                imsize=data['width/height']
                objects = data['objects']
            return imsize, objects
        except:
            pass

    def shapes_to_pandas(filename):
        imsize, objects = extract_polygons(filename)
        df=pd.DataFrame(columns=['width', 'height', 'Object', 'X', 'Y'])
        for i, obj in enumerate(objects):
            X, Y=list(zip(*obj))
            l=len(X)
            width=[imsize[0] for j in range(l)]
            height=[imsize[1] for j in range(l)]
            obj_number=[i+1 for j in range(l)]
            df=df.append(pd.DataFrame({'width': width, 'height': height, 'Object': obj_number, 'X': X, 'Y': Y}), ignore_index=True)
        return df

    dialogue=QFileDialog()
    dialogue.setNameFilter("*.csv");
    dialogue.setDefaultSuffix('csv')
    dialogue.exec()
    savepath=dialogue.selectedFiles()[0]

    shapes_to_pandas(path).to_csv(savepath, sep=',')



