import cv2
from cv2 import CAP_PROP_POS_FRAMES, CAP_PROP_POS_MSEC
from cv2 import CAP_PROP_FRAME_COUNT
from deepface import DeepFace
import json
import random
import tkinter
from eye_contact_logic import EyeContactLogic
from gaze_tracking_logic import GazeTrackingLogic
from emotion_change_logic import EmotionChangeLogic

from gaze_tracking import GazeTracking

gaze = GazeTracking()

labels = []

# Create a VideoCapture object and read from input file
video = cv2.VideoCapture('CS-4700/videos/alex3.MOV')

cframe = int(video.get(CAP_PROP_POS_FRAMES)) # retrieves the current frame number
tframe = int(video.get(CAP_PROP_FRAME_COUNT))  # get total frame count
fps = video.get(cv2.CAP_PROP_FPS)  # get the FPS of the video


# Boolean Toggles
usingEyeContact = True
usingGazeTracking = True
usingEmotionChangeTracking = True
showingDemo = True


# Parameters
eyeContactTime = 1 # How long (seconds) to record eye contact
eyeContactConfidence = .5 # What percentage of frames in the past eyeContactConfidenceTime seconds need eye contact
eyeContactConfidenceTime = 1 # How long (seconds) to parse back in time
emotion_count = 7 # Never change, only 7 emotions from DeepFace
emotionTime = 2 # Number of seconds to go back


gazeTime = 2 # How long (seconds) to record staring
gazeWindow = 0.05 # The size of the staring "window"
gazeConfidence = .80 # What percentage of frames in the past gazeConfidenceTime seconds need eye contact
gazeConfidenceTime = 1 # How long (seconds) to parse back in time


emotionAverageTime = 1 # How long (seconds) to average
emotionConfidence = 0.8 # What percent of past frames need a valid reading
emotionGate = 0.50 # What the average needs to be above in order to be the "dominant" expression, else unsure
emotionTimeout = 5 # Must change expressions faster than this or else throw it out

# Check if the file opened successfully
if (video.isOpened() == False):
    print("Error opening video stream or file")


# Instantiating the Objects
emotion_change_logic = EmotionChangeLogic(
        tframe,
        emotionConfidence,
        emotionAverageTime,
        emotionGate,
        emotionTimeout,
        fps
    )


eye_contact_logic = EyeContactLogic(
        eyeContactTime,
        eyeContactConfidence,
        eyeContactConfidenceTime,
        fps
    )

gaze_tracking_logic = GazeTrackingLogic(
        gazeTime,
        gazeWindow,
        gazeConfidence,
        gazeConfidenceTime,
        fps
    )


# Read until video is completed
while (video.isOpened()):

    _, frame = video.read()
    if _ == True:
        
        cframe = int(video.get(CAP_PROP_POS_FRAMES)) # retrieves the current frame number
        currentTimestamp = int(video.get(CAP_PROP_POS_MSEC))
        
        # Frame processing
        alpha = 1.5 # Contrast
        beta = 5 # Brightness
        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        
        # Changes the frame's resolution
        h, w = frame.shape[:2]
        aspectRatio = float(w)/h
        frame = cv2.resize(frame, (720, int(720 / aspectRatio)), 0, 0, interpolation=cv2.INTER_CUBIC)
            

        # The main gaze tracker function call
        if (usingEyeContact or usingGazeTracking):
            gaze.refresh(frame)
            
            
        # Facial Recognition begins here
        emotions_in_frames = [None for i in range(emotion_count)]

        try:
            demography = DeepFace.analyze(frame, actions=['emotion'])

            if isinstance(demography, list):
                demography = demography[0]
        
            if "dominant_emotion" in demography:

                # Inserting emotion information per frame
                emotions_in_frames[0] = demography["emotion"]["angry"]
                emotions_in_frames[1] = demography["emotion"]["disgust"]
                emotions_in_frames[2] = demography["emotion"]["fear"]
                emotions_in_frames[3] = demography["emotion"]["happy"]
                emotions_in_frames[4] = demography["emotion"]["sad"]
                emotions_in_frames[5] = demography["emotion"]["surprise"]
                emotions_in_frames[6] = demography["emotion"]["neutral"]
                
                # Prints the emotions
                #for i in range(7): print(emotions_in_frames[i])


            ####else:
                ####print("Warning: 'dominant_emotion' key not found in demography.")
            
            
        except Exception as e:
            # Print the specific exception for debugging purposes
            #################print(f"Exception encountered: {e}")
            demography_json = "No face detected."


        ############################################
        ## All of the logic code will now be here ##
        ############################################
        
        # Eye contact logic
        if (usingEyeContact):
            eye_contact_logic.addFrameInformation(gaze.is_center(), currentTimestamp)
            eye_contact_output = eye_contact_logic.getEyeContact(cframe, tframe)
            # if (eye_contact_output != None): print(eye_contact_output)
            if (eye_contact_output != None): labels.append(eye_contact_output)
            labels_json = json.dumps(labels, indent=4)
        
        
        # Gaze tracking logic
        if (usingGazeTracking):
            gaze_tracking_logic.add_frame_information(gaze.horizontal_ratio(), gaze.vertical_ratio(), currentTimestamp)
            gaze_tracking_output = gaze_tracking_logic.getGazeTracking(cframe, tframe)
            # if (gaze_tracking_output != None): print(gaze_tracking_output)
            if (gaze_tracking_output != None): labels.append(gaze_tracking_output)
            labels_json = json.dumps(labels, indent=4)

        # Emotion change logic
        if (usingEmotionChangeTracking):
            emotion_change_logic.addFrameInformation(cframe, emotions_in_frames, currentTimestamp)
            emotion_change_output = emotion_change_logic.getEmotionChange(cframe)
            # if (emotion_change_output != None): print(emotion_change_output)
            if (emotion_change_output != None): labels.append(emotion_change_output)
            labels_json = json.dumps(labels, indent=4)

        ########################################print(demography_json)
        
        # Rendering Stuff
        if showingDemo:
            cv2.imshow("Demo", frame)

        if cv2.waitKey(1) == 27:
            break

    else:
        break

print(labels_json)

# When everything done, release the video capture object
video.release()

# Closes all the frames
cv2.destroyAllWindows()

#print(emotionFrameArray)