from gaze_tracking import GazeTracking
from emotion_change_logic import EmotionChangeLogic
from eye_contact_logic import EyeContactLogic
from gaze_tracking_logic import GazeTrackingLogic
import cv2
from deepface import DeepFace
import json

class VideoProcessing:

    gaze = GazeTracking()

    labels = []

    tframe = None

    emotion_change_logic = None
    eye_contact_logic = None
    gaze_tracking_logic = None

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

    def __init__(self, tframe, fps):
        
        self.tframe = tframe

        # Instantiating the Objects
        self.emotion_change_logic = EmotionChangeLogic(
                tframe,
                self.emotionConfidence,
                self.emotionAverageTime,
                self.emotionGate,
                self.emotionTimeout,
                fps
            )


        self.eye_contact_logic = EyeContactLogic(
                self.eyeContactTime,
                self.eyeContactConfidence,
                self.eyeContactConfidenceTime,
                fps
            )

        self.gaze_tracking_logic = GazeTrackingLogic(
                self.gazeTime,
                self.gazeWindow,
                self.gazeConfidence,
                self.gazeConfidenceTime,
                fps
            )
    
    def processFrame(self, cframe, currentTimestamp, frame):

          # Frame processing
        alpha = 1.5 # Contrast
        beta = 5 # Brightness
        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        
        # Changes the frame's resolution
        h, w = frame.shape[:2]
        aspectRatio = float(w)/h
        frame = cv2.resize(frame, (960, int(960 / aspectRatio)), 0, 0, interpolation=cv2.INTER_CUBIC)
            

        # The main gaze tracker function call
        if (self.usingEyeContact or self.usingGazeTracking):
            self.gaze.refresh(frame)
            
            
        # Facial Recognition begins here
        emotions_in_frames = [None for i in range(self.emotion_count)]

        try:
            demography = DeepFace.analyze(frame, actions=['emotion'], detector_backend="mtcnn")

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
        if (self.usingEyeContact):
            self.eye_contact_logic.addFrameInformation(self.gaze.is_center(), currentTimestamp)
            eye_contact_output = self.eye_contact_logic.getEyeContact(cframe, self.tframe)
            # if (eye_contact_output != None): print(eye_contact_output)
            if (eye_contact_output != None): self.labels.append(eye_contact_output)
            labels_json = json.dumps(self.labels, indent=4)
        
        
        # Gaze tracking logic
        if (self.usingGazeTracking):
            self.gaze_tracking_logic.add_frame_information(self.gaze.horizontal_ratio(), self.gaze.vertical_ratio(), currentTimestamp)
            gaze_tracking_output = self.gaze_tracking_logic.getGazeTracking(cframe, self.tframe)
            # if (gaze_tracking_output != None): print(gaze_tracking_output)
            if (gaze_tracking_output != None): self.labels.append(gaze_tracking_output)
            labels_json = json.dumps(self.labels, indent=4)

        # Emotion change logic
        if (self.usingEmotionChangeTracking):
            self.emotion_change_logic.addFrameInformation(cframe, emotions_in_frames, currentTimestamp)
            emotion_change_output = self.emotion_change_logic.getEmotionChange(cframe)
            # if (emotion_change_output != None): print(emotion_change_output)
            if (emotion_change_output != None): self.labels.append(emotion_change_output)
            labels_json = json.dumps(self.labels, indent=4)

        return labels_json
    
    pass