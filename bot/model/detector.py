import numpy as np
from tensorflow import keras

from bot.model import model_cfg
from bot.model import preprocessing
from bot.model import postprocessing

class Yolo_Detector():
    def __init__(self):
        self.model = keras.models.load_model(model_cfg.MODEL)
        self.threshold = model_cfg.threshold
        self.nms_threshold = model_cfg.nms_threshold
        self.input_w = model_cfg.input_w
        self.input_h = model_cfg.input_h
        self.anchors = model_cfg.anchors
        
        # as this model trained to detect 500 classes of objects which takes 
        # for about 40 seconds on local CPU we need to slightly modify Keras
        # model prediction (to detect only food)
        opener = open("bot/model/classes.txt",'r')
        all_classes = []
        for i in opener:
            all_classes.append(i.strip())  
        self.food_classes = []
        opener = open("bot/model/food_classes.txt",'r')
        for i in opener:
            self.food_classes.append(i.strip())  
        food_indexes = [all_classes.index(i) for i in self.food_classes]
        self.indexes = np.hstack([np.arange(0, 5), np.array(food_indexes) + 5, 
                         np.arange(505,510), np.array(food_indexes) + 510, 
                         np.arange(1010,1015), np.array(food_indexes) + 1015])
    
    def convert_classes(self, prediction):
        new_pred = [prediction[0][:,:,:,self.indexes], 
                    prediction[1][:,:,:,self.indexes], 
                    prediction[2][:,:,:,self.indexes]]
        return new_pred
    
    def run_detector(self, file_path, save_path):
        image, image_w, image_h = preprocessing.load_image(file_path, 
                                                   (self.input_w, self.input_h))
        raw_pred = self.model.predict(image)
        # store only food-related predictions
        food_pred = self.convert_classes(raw_pred)
        boxes = list() 
        for i in range(len(food_pred)):
            boxes += postprocessing.decode_netout(food_pred[i][0], self.anchors[i], 
                                                  self.threshold, self.input_h, 
                                                  self.input_w)
        boxes = np.array(boxes)
        postprocessing.correct_yolo_boxes(boxes, image_h, image_w, 
                                          self.input_h, self.input_w)
        postprocessing.do_nms(boxes, self.nms_threshold)
        final_boxes, final_labels, _ = postprocessing.get_boxes(boxes, 
                                                                self.food_classes, 
                                                                self.threshold)
        postprocessing.save_pred(file_path, save_path, final_boxes, final_labels)
        return final_labels