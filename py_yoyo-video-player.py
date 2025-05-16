# github.com/zeittresor
# YoYo-Video-Player - Player to play a selected video in a loop forwards and backwards

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.title("YoYo-Video-Player")
root.geometry("300x100")

video_pfad = None

def selectvid():
    global video_pfad
    filetypes = [("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
    pfad = filedialog.askopenfilename(title="Select video", filetypes=filetypes)
    if pfad:
        video_pfad = pfad
        play_button.config(state=tk.NORMAL)

select_button = tk.Button(root, text="Select video...", command=selectvid)
select_button.pack(pady=10)
play_button = tk.Button(root, text="Play video", state=tk.DISABLED, command=root.destroy) # Press ESC to exit
play_button.pack()

root.mainloop()

if not video_pfad:
    print("No video selected. Exit program.")
    exit(0)

cap = cv2.VideoCapture(video_pfad)
if not cap.isOpened():
    print(f"Videofile can not be opened: {video_pfad}")
    exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 25.0
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()

n = len(frames)
if n == 0:
    print("Error: No video frames found.")
    exit(1)
elif n == 1:
    print("Note: The video file have just one useable frame, showing it static now.")

try:
    temp_root = tk.Tk()
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    temp_root.destroy()
except Exception:
    screen_width, screen_height = 1920, 1080

video_aspect = frame_width / frame_height
screen_aspect = screen_width / screen_height
if video_aspect > screen_aspect:
    new_width = screen_width
    new_height = int(frame_height * (screen_width / frame_width))
else:
    new_height = screen_height
    new_width = int(frame_width * (screen_height / frame_height))

use_letterbox = (new_width != screen_width or new_height != screen_height)
if use_letterbox:
    base_frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

window_name = "Video"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_KEEPRATIO)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

delay = max(1, int(round(1000 / fps)))

if n == 1:
    while True:
        frame = frames[0]
        if use_letterbox:
            display_frame = base_frame.copy()
            y_off = (screen_height - new_height) // 2
            x_off = (screen_width - new_width) // 2
            resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            display_frame[y_off:y_off+new_height, x_off:x_off+new_width] = resized
        else:
            display_frame = cv2.resize(frame, (screen_width, screen_height), interpolation=cv2.INTER_AREA)
        cv2.imshow(window_name, display_frame)
        key = cv2.waitKey(delay) & 0xFF
        if key == 27 or key == ord('q'):
            break
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
    cv2.destroyAllWindows()
    exit(0)

i = 0
richtung = 1
while True:
    frame = frames[i]
    if use_letterbox:
        display_frame = base_frame.copy()
        y_off = (screen_height - new_height) // 2
        x_off = (screen_width - new_width) // 2
        resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        display_frame[y_off:y_off+new_height, x_off:x_off+new_width] = resized
    else:
        display_frame = cv2.resize(frame, (screen_width, screen_height), interpolation=cv2.INTER_AREA)

    cv2.imshow(window_name, display_frame)

    key = cv2.waitKey(delay) & 0xFF
    if key == 27 or key == ord('q'):
        break
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

    next_i = i + richtung
    if next_i >= n:
        richtung = -1
        next_i = n - 2  # to avoid problems while the direction change
    elif next_i < 0:
        richtung = 1
        next_i = 4      # to avoid problems with the start frames in the loop
    i = next_i

cv2.destroyAllWindows()
