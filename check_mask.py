from face_mask import init_face_mask,detect_and_predict_mask
# from app import get_label
import cv2
import imutils
import os
import time

faceNet,maskNet = init_face_mask()
Hrisk = 0
Mrisk = 0
Lrisk = 0

def re_init():
    global Hrisk,Mrisk,Lrisk
    Hrisk = 0
    Mrisk = 0
    Lrisk = 0

def mask_count():
    global Hrisk,Mrisk,Lrisk
    return Hrisk,Mrisk,Lrisk


class Check_Mask(object):
    def __init__(self):
        pass

    def check_mask(self, label, imgpath):
        global Hrisk,Mrisk,Lrisk
        hrisk = 0
        mrisk = 0
        lrisk = 0

        # print("Makeup: ",label)
        iname = int((imgpath.split(os.sep)[-1]).split('.')[0])


        if label == "coughing":
            is_cough = True
        else:
            is_cough = False

        frame = cv2.imread(imgpath)
        try:
            frame = imutils.resize(frame, width=400)
        # print("resized frame shape:",frame.shape)
            (locs, preds, faces) = detect_and_predict_mask(frame, faceNet, maskNet)
            if (locs == -1) and (preds == -1):
                return False

            for (box, pred) in zip(locs, preds):

                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred
                label = "Mask" if mask > withoutMask else "No Mask"

                if mask>0.70 or withoutMask>0.70:
                	#sort into risk categories
                    if is_cough:
                        if label == 'Mask':
                            label = "Moderate Risk"
                            color = (255, 0, 0) #Blue
                            mrisk += 1

                        else:
                            label = "High Risk"
                            color = (0, 0, 225) #Red
                            hrisk += 1

                    else:
                        if label == 'Mask':
                            label = "Low Risk"
                            color = (0, 225, 0) #Green
                            lrisk += 1

                        else:
                            label = "Moderate Risk"
                            color = (255, 0, 0) #Blue
                            mrisk += 1



                	# include the probability in the label
                	# label = "{} ({:.1f}%)".format(label, max(mask, withoutMask) * 100)
                	# display the label and bounding box rectangle on the output frame
                    cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

                    if hrisk > Hrisk:
                        Hrisk = hrisk
                    if mrisk > Mrisk:
                        Mrisk = mrisk
                    if lrisk > Lrisk:
                        Lrisk = lrisk



                else:
                    continue

            if faces < 5:
                # show the output frame
                # cv2.imshow("Frame", frame)
                # key = cv2.waitKey(1) & 0xFF
                cv2.imwrite(imgpath,frame)
                # cv2.imshow('myframe',frame)
                # return img.transpose(Image.FLIP_LEFT_RIGHT)
            return imgpath
        except:
            time.sleep(1)
            return ""
