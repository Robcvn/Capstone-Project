import datetime
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import Button
from tkinter import ttk
from tkVideoPlayer import TkinterVideo
from tkinter import *
from PIL import ImageTk, Image

# Function for opening the 
# file explorer window
def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("MP4 files", "*.mp4"),
                                                       ("AVI files", "*.avi"),
                                                       ("MKV files", "*.mkv"),
                                                       ("MOV files", "*.mov"),
                                                       ("All files", "*.*")))
      
    load_video(filename)
    # Change label contents
    label_file_explorer.configure(text="File Opened: "+filename)

def load_results():
    with open('results.json', 'r') as f:
        results = json.load(f)
    
    for event in results['Eye Contact']:
        sidebar.insert(eye_contact_id, 'end', text=f"Eye Contact at {event['timestamp']}")

    for event in results['Staring']:
        sidebar.insert(eye_contact_id, 'end', text=f"Staring at {event['timestamp']}")

    for event in results['Facial Expression Change']:
        sidebar.insert(emotion_id, 'end', text=f"Expression Change at {event['timestamp']}")



def update_duration(event):
    """ updates the duration after finding the duration """
    duration = vid_player.video_info()["duration"]
    end_time["text"] = str(datetime.timedelta(seconds=duration))
    progress_slider["to"] = duration
    


def update_scale(event):
    """ updates the scale value """
    progress_slider.set(vid_player.current_duration())


def load_video(filename):
    """ loads the video """
#    file_path = filedialog.askopenfilename() #Used for file input! (Problaby use this for final product)
    # file_path = "CS-4700/videos/boy1.mp4"
    file_path = filename

    if file_path:
        vid_player.load(file_path)

        progress_slider.config(to=0, from_=0)
        play_pause_btn["text"] = "Play"
        progress_slider.set(0)
        #vid_player.set_size((1920, 1080))


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


root = tk.Tk()
root.title("Video/Audio GUI")
root.geometry("800x600")

# Create a File Explorer label
label_file_explorer = Label(root, 
                            text = "File Explorer using Tkinter",
                            width = 100, height = 4, 
                            fg = "blue")


button_explore = Button(root, text = "Browse Files", command = browseFiles) 
button_explore.pack()

label = tk.Label(root)
label.pack(side="bottom", fill="x")

# Set up sidebar using Treeview
sidebar = ttk.Treeview(root)

# Adding groups to sidebar
eye_contact_id = sidebar.insert("", tk.END, text="Eye Contact", open=False)  
emotion_id = sidebar.insert("", tk.END, text="Emotion", open=False)  

# Subgroups for Eye Contact
sidebar.insert(eye_contact_id, 'end', text="Staring")  
sidebar.insert(eye_contact_id, 'end', text="Eye Contact")  

# Subgroup for Emotion Change
sidebar.insert(emotion_id, 'end', text="Facial Expression Changes") 

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

# load_btn = tk.Button(root, text="Load", command=load_video)
# load_btn.pack()

vid_player = TkinterVideo(scaled=True, master=root)
vid_player.pack(fill="both", expand=True)

# vid_player = TkinterVideo(root,
#                                bg="blue",
#                                width=100,
#                                height= 50)
# vid_player.pack()

play_pause_btn = tk.Button(root, text="Play", command=play_pause)
play_pause_btn.pack()

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

#A function that detects if a list item is clicked on and scrubbs the slider to the index of the item.
def callback(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)
        label.configure(text=data)
        
        # print(test[index+1][1])

        #scribbing to the index of the list item
        #progress_slider.set(index+1)
        progress_slider.set(test[index+1][1])
        vid_player.seek(int(progress_slider.get()))
       
    else:
        label.configure(text="")

#Json file analysis

# #Opening JSON file
# j = open('sample.json')

# # returns JSON object as a dictionary
# data = json.load(j)
 
# # Iterating through the json
# for i in data[data["segments"][0]["text"]]:
#     print(i)

# # Closing file
# j.close()

# Function to handle Treeview item selection
def on_tree_select(event):
    item = sidebar.selection()[0]
    # Basic concept for label and video player interaction
    # Click on item and seek to the corresponing timestamped time
    print(f"You clicked on: {sidebar.item(item, 'text')}")

sidebar.bind("<<TreeviewSelect>>", on_tree_select)

root.mainloop()
