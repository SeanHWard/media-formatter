

import os
import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from concurrent.futures import ThreadPoolExecutor

def mute_audio(video_file):
    # Load the video clip
    clip = VideoFileClip(video_file)

    # Rotate video 90 degrees counterclockwise
    clip = clip.rotate(-90)

    # Resize video to 1920x1080
    clip = clip.resize((1920, 1080))

    # Mute audio
    muted_clip = clip.set_audio(None)

    # Rotate video 90 degrees clockwise
    muted_clip = muted_clip.rotate(90)

    # Write the video to a file
    muted_file = video_file.replace('.mp4', '_muted.mp4')
    muted_clip.write_videofile(muted_file, codec='libx264', fps=clip.fps)

    return muted_file

def rename_and_mute_videos(directory, prefix, mute_audio_flag):
    # Change the working directory to the directory containing the videos
    os.chdir(directory)

    # List all the files in the directory
    files = os.listdir()

    # Filter out only the video files
    video_files = [file for file in files if file.endswith('.mp4') or file.endswith('.MOV') or file.endswith('.MP4') or file.endswith('.mov')]

    # Disable all buttons and show loading state
    browse_button.config(state="disabled")
    start_button.config(state="disabled")
    directory_entry.config(state="disabled")
    prefix_entry.config(state="disabled")
    mute_check.config(state="disabled")
    root.update()

    # Rename and mute audio for each video file
    with ThreadPoolExecutor(max_workers=4) as executor:
        for i, file in enumerate(video_files):
            # Generate the new file name
            new_name = f"{prefix}_{i+1}.mp4"  # Change the extension accordingly if needed

            # Rename the file
            os.rename(file, new_name)

            # Mute audio if selected
            if mute_audio_flag:
                executor.submit(mute_audio, new_name)

            print(f"'{file}' renamed and audio muted successfully as '{new_name}'")

    # Check if there are any files with '_muted' in their name
    if any('_muted' in file for file in os.listdir(directory)):
        # Create a new directory for muted files
        new_directory = os.path.join(directory, f"{prefix}_MUTED")
        os.makedirs(new_directory, exist_ok=True)

        # Move all _muted files to the new directory and remove '_muted' from their names
        for file in os.listdir(directory):
            if '_muted' in file:
                os.rename(os.path.join(directory, file), os.path.join(new_directory, file.replace('_muted', '')))

        print(f"Muted files moved to '{new_directory}'")

    # Enable all buttons and hide loading state
    browse_button.config(state="normal")
    start_button.config(state="normal")
    directory_entry.config(state="normal")
    prefix_entry.config(state="normal")
    mute_check.config(state="normal")
    result_label.config(text="Processing completed successfully!", fg="green")

def get_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)

def start_renaming():
    directory = directory_entry.get().strip()
    prefix = prefix_entry.get().strip()
    mute_audio_flag = mute_var.get()

    # Check if the provided directory exists
    if not os.path.isdir(directory):
        result_label.config(text="Directory not found!", fg="red")
    else:
        # Call the function to rename and mute audio of the videos
        result_label.config(text="Processing...")
        root.update()
        rename_and_mute_videos(directory, prefix, mute_audio_flag)

# Create the main window
root = tk.Tk()
root.title("Media Formatter")

# Frame for directory selection
directory_frame = tk.Frame(root)
directory_frame.pack(pady=10)

directory_label = tk.Label(directory_frame, text="Directory:")
directory_label.grid(row=0, column=0, padx=5, pady=5)

directory_entry = tk.Entry(directory_frame, width=50)
directory_entry.grid(row=0, column=1, padx=5, pady=5)

browse_button = tk.Button(directory_frame, text="Browse", command=get_directory)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Frame for prefix input
prefix_frame = tk.Frame(root)
prefix_frame.pack(pady=10)

prefix_label = tk.Label(prefix_frame, text="Prefix:")
prefix_label.grid(row=0, column=0, padx=5, pady=5)

prefix_entry = tk.Entry(prefix_frame, width=50)
prefix_entry.grid(row=0, column=1, padx=5, pady=5)

# Checkbox for muting audio
mute_var = tk.BooleanVar()
mute_check = tk.Checkbutton(root, text="Mute audio", variable=mute_var)
mute_check.pack()

# Start button
start_button = tk.Button(root, text="Start Renaming and Muting Audio", command=start_renaming)
start_button.pack(pady=10)

# Result label
result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
