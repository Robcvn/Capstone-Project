# This is the code that pertains to eye contact with the camera
class EyeContactLogic:
    
    # Eye Contact Parameters
    eye_contact_required_frame_count = 0 # The length (in frames) required for eye contact
    eye_contact_confidence = 0 # Confidence parameter in case some frames aren't read
    eye_contact_confidence_frame_count = 0 # How far back (frames) we check for confidence
    
    # Eye Contact Per-Frame Information
    eye_contact = []
    timestamp_of_each_frame = []
    
    # Logic Information
    past_frame_tally = -1 # -1 because we add one at the start of getEyeContact
    
    def __init__(self, eye_contact_time,
                 eye_contact_confidence,
                 eye_contact_confidence_time,
                 fps):
        
        self.eye_contact_required_frame_count = int(eye_contact_time * fps)
        self.eye_contact_confidence = eye_contact_confidence
        self.eye_contact_confidence_frame_count = int(eye_contact_confidence_time * fps)
    
    
    # Adds information to the object about the current frame
    # Boolean if there is eye contact
    # Timestamp of the frame
    def addFrameInformation(self, is_eye_contact, current_time_stamp):
        self.eye_contact.append(bool(is_eye_contact))
        self.timestamp_of_each_frame.append(current_time_stamp)
        pass
    
    
    # Retrieves whether or not we are confident about this frame has eye
    # contact with the camera or not. Considers previous frames as well.
    # Should return a JSON string
    def getEyeContact(self, cframe, tframe):
        # Goes through, once per frame, and checks to see if eye contact occurs
        
        self.past_frame_tally += 1 # A frame has passed, record it to get the total length
        
        #print("i is", str(i))
        past_frame_count = min(self.past_frame_tally, self.eye_contact_confidence_frame_count) # How far back we check
        past_eye_contact_count = 0 # How many of the previous frames have eye contact
        
        # Now we check backwards a certain depth to tally frames with eye contact
        for i in range(past_frame_count):
            #print("j is", str(j))
            #print("Length:", str(len(self.eye_contact)))
            if self.eye_contact[cframe-i-1]:
                past_eye_contact_count += 1
    
        
        # Checking if NOT confident enough
        # Continues through and tallies length until hopefully long enough
        
        #print(str(past_eye_contact_count))
        #print(str(past_frame_count * self.eye_contact_confidence))
        if (past_eye_contact_count < (past_frame_count * self.eye_contact_confidence) or cframe == tframe-1):
            
            # When we are not confident, always reset the tally. We are starting over
            temp_past_frame_tally = self.past_frame_tally # "One time use" variable because we need it immediately after
            self.past_frame_tally = -1
            
            # Now we must check if it is long enough. Long enough implies eye contact.
            if (temp_past_frame_tally >= self.eye_contact_required_frame_count):
                
                # Gets the average frame during the span
                middle_frame = int((cframe+(cframe-temp_past_frame_tally))/2)
                # return_string = self.millisecondsToMinutes(self.timestamp_of_each_frame[middle_frame]), " - Eye Contact"
                #print(return_string)

                dict = {"label": "Eye Contact", "Description": "", "Time Stamp": str(self.millisecondsToMinutes(self.timestamp_of_each_frame[middle_frame]))}
                return dict
        pass
    
    
    # Convert milliseconds to minutes
    def millisecondsToMinutes(self, ms):
        secondsOnes = int(ms / 1000 % 10)
        secondsTens = int(ms / 10000 % 10)

        minutesOnes = int(ms / 60000 % 10)
        minutesRest = int(ms / 600000)

        return (str(minutesRest) + str(minutesOnes) + ":" + str(secondsTens) + str(secondsOnes))