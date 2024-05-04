import datetime
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import Button
from tkinter import ttk
from tkVideoPlayer import TkinterVideo
from tkinter import *
from PIL import ImageTk, Image
import threading
import time
from tkinter import messagebox
import cv2
from video_processing import VideoProcessing


global file_path
file_path = None
added_events = set()


# Function for opening the 
# file explorer window
def browseAndLoadVideo():

    global file_path
    file_path = filedialog.askopenfilename(initialdir="/",
                                           title="Select a File",
                                           filetypes=(("MP4 files", "*.mp4"),
                                                       ("AVI files", "*.avi"),
                                                       ("MKV files", "*.mkv"),
                                                       ("MOV files", "*.mov"),
                                                       ("All files", "*.*")))

    if file_path:
        # Change label contents
        label_file_explorer.configure(text="File Opened: " + file_path)

        process_button.pack()

        # Load video
        vid_player.load(file_path)
        progress_slider.config(to=0, from_=0)
        play_pause_btn["text"] = "Play"
        progress_slider.set(0)
        #load_results()

    #    # Clear the sidebar
    #     sidebar.delete(*sidebar.get_children())
    #     added_events = set() 

    #     # Recreate labels
    #     eye_contact_id = sidebar.insert("", tk.END, text="Eye Contact", open=False)
    #     staring_id = sidebar.insert("", tk.END, text="Staring", open=False)
    #     emotion_id = sidebar.insert("", tk.END, text="Emotion", open=False)



def load_results(raw_json):
    json_data = json.loads(raw_json)

    for event in json_data:
        timestamp = event["Time Stamp"]
        description = event["Description"]

        # Check if the timestamp is not already added
        if timestamp not in added_events:
            if event["label"] == "Eye Contact":
                sidebar.insert(eye_contact_id, 'end', text=f"{timestamp}")
            elif event["label"] == "Staring":
                sidebar.insert(staring_id, 'end', text=f"{timestamp}")
            elif event["label"] == "Facial Expression Change":
                sidebar.insert(emotion_id, 'end', text=f"{timestamp} {description}")
            # Add the timestamp to the set
            added_events.add(timestamp)
    

def update_duration(event):
    """ updates the duration after finding the duration """
    duration = vid_player.video_info()["duration"]
    end_time["text"] = str(datetime.timedelta(seconds=duration))
    progress_slider["to"] = duration
    


def update_scale(event):
    """ updates the scale value """
    progress_slider.set(vid_player.current_duration())


def seek(event=None):
    """ used to seek a specific timeframe """
    vid_player.seek(int(progress_slider.get()))


def skip(value: int):
    """ skip seconds """
    vid_player.seek(int(progress_slider.get())+value)
    progress_slider.set(progress_slider.get() + value)


def play_pause():
    """ pauses and plays """
    if vid_player.is_paused():
        vid_player.play()
        play_pause_btn["text"] = "Pause"

    else:
        vid_player.pause()
        play_pause_btn["text"] = "Play"


def video_ended(event):
    """ handle video ended """
    progress_slider.set(progress_slider["to"])
    play_pause_btn["text"] = "Play"
    progress_slider.set(0)
    
def display_frame(frame):
    # Convert the frame to tkinter
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)

    # Resize image to vidplayer size
    video_player_width = vid_player.winfo_width()
    video_player_height = vid_player.winfo_height()
    resize_image = img.resize((video_player_width, video_player_height))

    # Convert to PhotoImage
    imgtk = ImageTk.PhotoImage(image=resize_image)
    
    # Update the image panel to display the frame
    imgPanel.configure(image=imgtk)
    imgPanel.image = imgtk

def clear_frame_display():
    imgPanel.configure(image=None)
    imgPanel.image = None


root = tk.Tk()
root.title("Video/Audio GUI")
root.geometry("800x600")

#########################
# FILE PROCESSING LOGIC #
#########################

def process_file(file_path):
    print(f"Processing file: {file_path}")
    import cv2

    video = cv2.VideoCapture(file_path)
    tframe = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # get total frame count
    fps = video.get(cv2.CAP_PROP_FPS)  # get the FPS of the video

    video_processor = VideoProcessing(tframe, fps)

    # Goes through each frame of the video
    while video.isOpened():
        ret, frame = video.read()

        if ret:
            cframe = int(video.get(cv2.CAP_PROP_POS_FRAMES)) # retrieves the current frame number
            currentTimestamp = int(video.get(cv2.CAP_PROP_POS_MSEC))
            #img2=ImageTk.PhotoImage(frame)
            #img.config(Image = img2)
            raw_json = video_processor.processFrame(cframe, currentTimestamp, frame)
            #print(raw_json)
            load_results(raw_json)
            
            
            # Adding current frame being processed
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            resize_image = img.resize((250, 180))
            #puts the image in a PhotoImage type so that it can be read/displayed
            img = ImageTk.PhotoImage(resize_image)
            
            root.after(0, display_frame, frame)
            

            # Uncomment and edit the following lines if there is a GUI to show the video demo
            # if showingDemo:
            #     cv2.imshow("Demo", frame)
            # if cv2.waitKey(1) == 27:  # Press 'Esc' key to break
            #     break
        else:
            break
        
    video.release()  # Release the video object
    # cv2.destroyAllWindows()  # Close all OpenCV windows
    print("File processing complete.")

def start_processing_file():
    global file_path
    if file_path:
        process_button.config(text="Processing...", state="disabled")
        processing_thread = threading.Thread(target=process_file, args=(file_path,))
        processing_thread.start()
        def monitor():
            processing_thread.join()
            process_button.config(text="Process file", state="normal")
            messagebox.showinfo("Processing Complete", "The file has been processed.")
        monitoring_thread = threading.Thread(target=monitor)
        monitoring_thread.start()

# Create a File Explorer label
label_file_explorer = Label(root, 
                            text = "File Explorer using Tkinter",
                            width = 100, height = 4, 
                            fg = "blue")


button_explore = Button(root, text = "Browse Files", command = browseAndLoadVideo)
process_button = Button(root, text="Process file", command=start_processing_file)

button_explore.pack()

label = tk.Label(root)
label.pack(side="bottom", fill="x")

# Set up sidebar using Treeview
sidebar = ttk.Treeview(root)

# Adding groups to sidebar
eye_contact_id = sidebar.insert("", tk.END, text="Eye Contact", open=False)
staring_id = sidebar.insert("", tk.END, text="Staring", open=False)   
emotion_id = sidebar.insert("", tk.END, text="Emotion", open=False)  

# Put sidebar on left side
sidebar.pack(side="left", fill="y")


#creates the image and resizes it
img = Image.open("CS-4700/video.png")
resize_image = img.resize((250, 180))
#puts the image in a PhotoImage type so that it can be read/displayed
img = ImageTk.PhotoImage(resize_image)
#puts the image in a pannel below the
imgPanel = tk.Label(root, image = img)
imgPanel.pack(side="bottom", fill="both", expand=True)

vid_player = TkinterVideo(scaled=True, master=root)
vid_player.pack(fill="both", expand=True)

# vid_player = TkinterVideo(root,
#                                bg="blue",
#                                width=100,
#                                height= 50)
# vid_player.pack()

play_pause_btn = tk.Button(root, text="Play", command=play_pause)
play_pause_btn.pack()

process_button = Button(root, text="Process file", command=start_processing_file)

#creates a button that skips behind in the video by 5 seconds
skip_plus_5sec = tk.Button(root, text="-5 sec", command=lambda: skip(-5))
skip_plus_5sec.pack(side="left")

#displays the start time of the video
start_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
start_time.pack(side="left")

progress_slider = tk.Scale(root, from_=0, to=0, orient="horizontal")
progress_slider.bind("<ButtonRelease-1>", seek)
progress_slider.pack(side="left", fill="x", expand=True)

#displays the end time of the video
end_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
end_time.pack(side="left")

vid_player.bind("<<Duration>>", update_duration)
vid_player.bind("<<SecondChanged>>", update_scale)
vid_player.bind("<<Ended>>", video_ended )

#creates a button that skips ahead in the video by 5 seconds
skip_plus_5sec = tk.Button(root, text="+5 sec", command=lambda: skip(5))
skip_plus_5sec.pack(side="left")


# Function that seeks to timestamp time in video once clicked on and pauses
def on_tree_select(event):
    item = sidebar.selection()[0]
    timestamp_str = sidebar.item(item, 'text')

    if ("Eye Contact" in timestamp_str or "Emotion" in timestamp_str or "Staring" in timestamp_str):
        pass

    else:
        
        # Convert timestamp into 00:00:00 format
        time_parts = timestamp_str.split(':')
        time_parts[1] = time_parts[1][0:2]

        if len(time_parts) == 3:
            hours, minutes, seconds = [int(part) for part in time_parts]
        elif len(time_parts) == 2:
            hours = 0
            minutes, seconds = [int(part) for part in time_parts]
        else:
            hours = 0
            minutes = 0
            seconds = int(time_parts[0])

        # Convert the timestamp to seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds
        
        # Seek to the specific time in video and pause
        vid_player.seek(total_seconds)
        progress_slider.set(total_seconds)
        

        play_pause_btn["text"] = "Play"
        root.after(100, lambda: vid_player.pause())
        vid_player.play()
        root.after(100, lambda: vid_player.pause())
    
sidebar.bind("<<TreeviewSelect>>", on_tree_select)

root.mainloop()