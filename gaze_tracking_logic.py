# The gaze tracking logic class goes in here
class GazeTrackingLogic:

    # Gaze/Staring Tracking Parameters
    gaze_required_frame_count = 0 # How many total frames need to be staring
    gaze_window = 0 # The size of the gaze "window"
    gaze_confidence = 0 # What percent of previous frames need to register
    gaze_confidence_frame_count = 0 # How far to check back to see if confident
    
    # Gaze Tracking Per-Frame Information
    delta_gaze = []
    timestamp_of_each_frame = []

    # Logic variables
    past_frame_tally = -1 # -1 because one is added at the start of getGazeTracking
    previous_gaze_ratio = 0.5 # The past gaze ratio for calculating delta gaze

    def __init__(self,
                 gaze_time,
                 gaze_window,
                 gaze_confidence,
                 gaze_confidence_time,
                 fps):
        
        self.gaze_required_frame_count = int(gaze_time * fps)
        self.gaze_window = gaze_window
        self.gaze_confidence = gaze_confidence
        self.gaze_confidence_frame_count = int(gaze_confidence_time * fps)
        pass
    
    
    # Appends useful information to the internal arrays
    # Also calculates delta_gaze
    def add_frame_information(self, x_gaze_ratio, y_gaze_ratio, current_timestamp):
        
        try:
            current_gaze_ratio = x_gaze_ratio if (x_gaze_ratio > y_gaze_ratio) else y_gaze_ratio
        except:
            current_gaze_ratio = 0
        
        delta_gaze_num = 0
        try:
            delta_gaze_num = current_gaze_ratio - self.previous_gaze_ratio
            self.delta_gaze.append(delta_gaze_num)
        except:
            self.delta_gaze.append(None)
        
        self.previous_gaze_ratio = current_gaze_ratio

        self.timestamp_of_each_frame.append(current_timestamp)
        pass
    
    
    # Retrieves whether or not we are confident about this frame
    # is staring or not. Considers previous frames as well.
    # Should return a JSON string
    def getGazeTracking(self, cframe, tframe):
        # Goes through, once per frame, and checks if still looking within the "window" (gaze_confidence)

        self.past_frame_tally += 1 # A frame has passed, record it to get the total length

        past_frame_count = min(self.past_frame_tally, self.gaze_confidence_frame_count) # How far back to look
        past_gaze_count = 0 # Number of previous frames with eye contact
        
        # Now we check backwards a certain depth to tally frames with similar gaze (small delta_gaze)
        for i in range(past_frame_count):
            if (self.delta_gaze[cframe-i-1] <= self.gaze_window):
                past_gaze_count += 1
        
        
        # Checking if NOT confident enough
        # Continues through and tallies length until hopefully long enough
        
        
        if (past_gaze_count < (past_frame_count * self.gaze_confidence) or cframe == tframe-1):
            
            # When not confident, always reset the tally. We are starting over.
            temp_past_gaze_tally = self.past_frame_tally # "One time use" variable because we need it immediately after
            self.past_frame_tally = -1
            
            # Now we check the length. Long enough implies gaze.
            if (temp_past_gaze_tally >= self.gaze_required_frame_count):
                
                # Gets the average frame during the span
                middle_frame = int((cframe+(cframe-temp_past_gaze_tally))/2)
                # return_string = self.millisecondsToMinutes(self.timestamp_of_each_frame[middle_frame]), " - Staring"
                # #print(return_string)
                # return return_string

                dict = {"label": "Staring", "Description": "", "Time Stamp": str(self.millisecondsToMinutes(self.timestamp_of_each_frame[middle_frame]))}
                return dict
        pass
    
    
    # Convert milliseconds to minutes
    def millisecondsToMinutes(self, ms):
        secondsOnes = int(ms / 1000 % 10)
        secondsTens = int(ms / 10000 % 10)

        minutesOnes = int(ms / 60000 % 10)
        minutesRest = int(ms / 600000)

        return (str(minutesRest) + str(minutesOnes) + ":" + str(secondsTens) + str(secondsOnes))