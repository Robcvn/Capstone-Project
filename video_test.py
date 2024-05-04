import cv2 

# reading the input 
cap = cv2.VideoCapture("CS-4700/videos/alex.mp4") 

output = cv2.VideoWriter( 
    "CS-4700/videos/output.mp4", cv2.VideoWriter_fourcc(*'x264'), cap.get(cv2.CAP_PROP_FPS), (1280, 720)) 

currentFrame = 0

while(cap.isOpened): 
    ret, frame = cap.read() 
    if(ret): 

        currentFrame += 1 
        print(currentFrame)

        # adding rectangle on each frame 
        cv2.rectangle(frame, (100, 100), (500, 500), (0, 255, 0), 3) 
            
        # writing the new frame in output 
        output.write(frame) 
        cv2.imshow("output", frame) 
    
    else:
        break

output.release() 
cap.release() 

cv2.destroyAllWindows()
