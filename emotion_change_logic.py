# The emotion change logic class goes here
class EmotionChangeLogic:
    
    # Emotion parameters
    emotion_count = 7 # 7 Emotions in the library
    emotion_confidence = 0 # Number of past frames need to valid for an average
    emotion_average_frame_count = 0 # Number of frames to go back for an average
    emotion_gate = 0 # Must be above this to be the dominant average emotion
    emotion_timeout_frame_count = 0 # Face must change faster than X frames
    
    # Per-frame information
    emotions_in_frames = [] # Big 7 x tframe array with every emotion parameter per frame
    average_emotions_in_past_frames = [] # 7 x tframe - a bit array with calculated averages
    emotion_labels = [
        "Angry",                #0
        "Disgust",              #1
        "Fear",                 #2
        "Happy",                #3
        "Sad",                  #4
        "Surprise",             #5
        "Neutral",              #6
        "No face detected",     #7 is null
        "No dom. emotion"   #8 is no dominant emotion
        ]
    dominant_emotions = [] # Stores every calculated dominant emotion index
    timestamp_of_each_frame = []
    
    # Logic variables
    
    
    def __init__(self,
                 tframe,
                 emotion_confidence,
                 emotion_average_time,
                 emotion_gate,
                 emotion_timeout,
                 fps):
        
        self.emotion_count = 7
        
        self.emotion_confidence = emotion_confidence
        self.emotion_average_frame_count = int(emotion_average_time * fps)
        self.emotion_gate = emotion_gate * 100 # Because it is 0 - 100 not 0 - 1
        self.emotion_timeout_frame_count = int(emotion_timeout * fps)
        
        self.emotions_in_frames = [[None for i in range(tframe)] for j in range(self.emotion_count)]
        self.average_emotions_in_past_frames = [[0 for i in range(tframe - self.emotion_average_frame_count + 1)] for j in range(self.emotion_count)]
        pass
    
    def addFrameInformation(self, cframe, emotions_in_frames, current_timestamp):
        
        self.timestamp_of_each_frame.append(current_timestamp)
        
        # Adds to the 2D array
        # Once per emotion
        for i in range(self.emotion_count):
            if (emotions_in_frames[i] != None): 
                self.emotions_in_frames[i][cframe - 1] = emotions_in_frames[i]
            
        # self.emotion_frame_count is how far back to go
        # Cannot start before then so end if so
        if (cframe < self.emotion_average_frame_count):
            #print("not enough")
            return
        #print("emotion average frame count", self.emotion_average_frame_count)
        #print("cframe - 1", cframe - 1)
        #print("tframe-emotion", tframe - self.emotion_average_frame_count)
        
        # Checking that enough frames were read, if not, then None and end function
        valid_frame_count = 0 # Number of past frames that had emotions
        # Counts up the past frames, just need emotion 0
        for i in range(self.emotion_average_frame_count):
            if (self.emotions_in_frames[0][cframe - 1 - i] != None):
                valid_frame_count += 1
        #print("valid frame count:", valid_frame_count)
        
        
        current_average_index = cframe - self.emotion_average_frame_count
        
        
        # Checks if not enough past frames were valid
        if (valid_frame_count < self.emotion_average_frame_count * self.emotion_confidence):
            # None for each emotion
            for i in range(self.emotion_count):
                # -1 because that is never happening
                self.average_emotions_in_past_frames[i][current_average_index] = -1
            #print("too low, returning")
            return
        
        
        # Doing the tallying up and dividing for the averages
        # Once per emotion
        for i in range(self.emotion_count):
            for j in range(self.emotion_average_frame_count):
                # Skips if None because cannot add up None
                if (self.emotions_in_frames[i][cframe - j - 1] == None):
                    continue
                
                #print(self.emotions_in_frames[i][cframe-j])
                self.average_emotions_in_past_frames[i][current_average_index] += self.emotions_in_frames[i][cframe - j - 1]
            
            # After totalling, divide by number of frames
            self.average_emotions_in_past_frames[i][current_average_index] /= valid_frame_count
        pass
            
    
    def getEmotionChange(self, cframe):
        
        # Checks if there is an average for the frame.
        # If not, then skip
        if (cframe < self.emotion_average_frame_count):
            return
        
        # Which average we are currently using
        current_average_index = cframe - self.emotion_average_frame_count

        # Prints all of the average emotions
        # Once per emotion
        #for i in range(self.emotion_count): print(str(self.emotions[i]) + ": " + str(self.average_emotions_in_past_frames[i][current_average_index]))


        """
        # 0. Angry
        # 1. Disgust
        # 2. Fear
        # 3. Happy
        # 4. Sad
        # 5. Surprise
        # 6. Neutral
        # 7. No face detected
        # 8. No dominant expression
        """
        
        """
        # No face detected
        if (current_emotion == None):
            #print("appending 8")
            self.dominant_emotions.append(7)
        """
        
        
        # Face detected
        #else:
        has_no_dominant_expression = True
        # Adds the dominant average emotion to the array
        # Once per emotion
        for i in range(self.emotion_count):
            current_emotion = self.average_emotions_in_past_frames[i][current_average_index]
            #print(current_emotion)
            
            # If None then invalid
            if (current_emotion == -1):
                self.dominant_emotions.append(7)
                #print("Dominant emotion: no face detected, returning")
                return

            # Checks the ith emotion to see if dominant
            if (current_emotion > self.emotion_gate):
                has_no_dominant_expression = False
                self.dominant_emotions.append(i)
                # print("Dominant emotion: " + str(self.emotion_labels[i]))
                #return "Dominant emotion: " + str(self.emotion_labels[i])
        
        # No dominant expression
        if(has_no_dominant_expression):
            #print("appending 7")
            self.dominant_emotions.append(8)
            
        #print("Dominant emotion: " + self.emotion_labels[self.dominant_emotions[current_average_index]])
        
        #return self.dominant_emotions[current_average_index]
        #return self.emotion_labels[self.dominant_emotions[current_average_index]]
        
        # Now we use the list of past frames to calculate changes
        # Going backwards we should see expression A -> no dom. expression -> expression B
        current_average_emotion = self.dominant_emotions[current_average_index]
        
        # Throw out if currently idk or None
        if (current_average_emotion >= 7): return
        
        for i in range(1, current_average_index):
            
            #for j in range(1): print("got here")
            
            first_emotion = self.dominant_emotions[current_average_index - i]
            #print("previous emotion: " + self.emotion_labels[first_emotion])
            
            # If longer than the timeout time, then throw it out.
            # Took too long to change expressions (usually really long)
            if (i >= self.emotion_timeout_frame_count): return
            
            # If the previous frame(s) are the same as the current,
            # there was no facial change so through it out.
            if (first_emotion == current_average_emotion): return #"Same"
        
        
            # If the previous frame(s) were None, we don't know.
            # Throw it out.
            if (first_emotion == 7): return #"N/A"
            
            
            # If the previous frame(s) are no dominant emotion, keep going.
            if (first_emotion == 8):
                print("going back farther")
                continue
            
            
            # If a different average emotion is reached, end the loop
            # This is a facial expression change!
            if (first_emotion != current_average_emotion):
                
                # Gets the average frame during the span
                middle_frame = int((cframe+(cframe-i))/2)
                # return_string = self.millisecondsToMinutes(self.timestamp_of_each_frame[middle_frame]), " - Facial Expression Change"
                # #print(return_string)
                # return return_string
                
                description = self.emotion_labels[first_emotion] + " to " + self.emotion_labels[current_average_emotion]
            
                dict = {"label": "Facial Expression Change", "Description": description, "Time Stamp": str(self.millisecondsToMinutes(self.timestamp_of_each_frame[middle_frame]))}
                return dict
        
        
        pass
    
    
        # Convert milliseconds to minutes
    def millisecondsToMinutes(self, ms):
        secondsOnes = int(ms / 1000 % 10)
        secondsTens = int(ms / 10000 % 10)

        minutesOnes = int(ms / 60000 % 10)
        minutesRest = int(ms / 600000)

        return (str(minutesRest) + str(minutesOnes) + ":" + str(secondsTens) + str(secondsOnes))