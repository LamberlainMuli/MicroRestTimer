import time
import random
import pygame
import tkinter as tk
from tkinter import Label, Button, Entry, StringVar
from tkinter import Canvas
import pyautogui

pygame.init()

class GapLearningApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Gap Learning Timer")

        self.interval_min = 80  # 1 minute 20
        self.interval_max = 160 # 2 minutes 40
        self.standard_deviation = 5

        # Layout & Styling
        self.root.configure(bg="white")

        # Duration Entry
        self.duration_var = StringVar(value="3600")
        tk.Label(root, text="Duration (seconds):", bg="white").pack(pady=10)
        tk.Entry(root, textvariable=self.duration_var).pack(pady=10)

        # Timer Display
        self.time_label = Label(root, text="00:00:00", bg="white", font=("Arial", 20, "bold"))
        self.time_label.pack(pady=20)

        # Adding a canvas for a circular timer visualization
        self.canvas = Canvas(root, width=220, height=220, bg='white', highlightthickness=0)
        self.canvas.pack(pady=20, side=tk.TOP)
        
        # State Management
        self.state = "Not Started"

        # Start, Pause & Resume Buttons
        self.start_button = Button(root, text="Start", bg="green", fg="white", command=self.start_timer)
        self.start_button.pack(pady=10, side=tk.LEFT, padx=10)

        self.pause_button = Button(root, text="Pause", bg="orange", fg="white", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.pack(pady=10, side=tk.LEFT, padx=10)
        
        self.resume_button = Button(root, text="Resume", bg="blue", fg="white", command=self.resume_timer, state=tk.DISABLED)
        self.resume_button.pack(pady=10, side=tk.LEFT, padx=10)

        self.reset_button = Button(root, text="Reset", bg="blue", fg="white", command=self.reset_timer)
        self.reset_button.pack(pady=10, side=tk.LEFT, padx=10)

    def start_timer(self):
        if self.state == "Not Started":
            
            self.duration = int(self.duration_var.get())
            self.remaining_time = self.duration
            self.end_time = time.time() + self.duration
            self.intervals = self.generate_intervals()
            self.pause_button.config(state=tk.NORMAL)
            self.state = "Running"

        # Initialize the time for the first break
        if len(self.intervals) > 0:
            self.next_break_time = self.intervals.pop(0)

        self.update_timer()

    def reset_timer(self):
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)
        self.state = "Not Started"
        self.time_label.config(text="00:00:00")
        self.update_canvas()
    
    def pause_timer(self):
        if self.state == "Running":
            self.remaining_pause_time = self.remaining_time
            self.root.after_cancel(self.after_id)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.NORMAL)
            self.state = "Paused"
            
    def resume_timer(self):
        if self.state == "Paused":
            self.end_time = time.time() + self.remaining_pause_time
            self.state = "Running"
            self.resume_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.update_timer()
                    
    def stop_timer(self):
        self.remaining_time = self.end_time - time.time()
        self.root.after_cancel(self.after_id)
        self.time_label.config(text=self.format_time(self.remaining_time))

    def update_timer(self):
        if time.time() < self.end_time and self.state == "Running":
            self.remaining_time = self.end_time - time.time()
            self.time_label.config(text=self.format_time(self.remaining_time))
            # Update canvas visualization
            self.update_canvas()
            # Check if it's time for the next break
            if len(self.intervals) > 0 and self.remaining_time <= self.duration - self.next_break_time:
                pyautogui.press("playpause")
                self.play_sound('start_signal.wav') 
                time.sleep(10)
                self.play_sound('end_signal.wav')
                pyautogui.press("playpause")
                
                # Update the time for the next break
                self.next_break_time += self.intervals.pop(0)

            self.after_id = self.root.after(1000, self.update_timer)
        else:
            self.time_label.config(text="00:00")
            self.play_sound('end_signal.wav')

    def update_canvas(self):
        """Draws a circular countdown visualization."""
        self.canvas.delete("all")  # Clear the previous drawings
        # print("update canvas called")
        # Full circle representing the total timer duration (greyed out background)
        self.canvas.create_arc(10, 10, 210, 210, start=-90, extent=359, style=tk.ARC, outline='lightgrey', width=10)
        
        # Calculate the angle for the arc representing elapsed time
        angle = (1 - (self.remaining_time / self.duration)) * 360
        if angle > 0:  # Only draw if there's elapsed time
            self.canvas.create_arc(10, 10, 210, 210, start=-90, extent=angle, style=tk.ARC, outline='green', width=10)


 
    def format_time(self, seconds):
        return time.strftime('%H:%M:%S', time.gmtime(seconds))

    def generate_intervals(self):
        total_duration = int(self.duration_var.get())
        
        # 1. Determine the Number of Breaks
        mean_breaks_per_hour = 30
        std_dev_breaks = 5
        hours = total_duration / 3600  # Convert total duration to hours

        # Scale mean and draw random number of breaks based on normal distribution
        breaks_for_duration = round(random.gauss(mean_breaks_per_hour * hours, std_dev_breaks * hours))

        mean_interval = total_duration / breaks_for_duration
        intervals = []

        while sum(intervals) < total_duration:
            interval = random.gauss(mean_interval, mean_interval/10)  # Randomizing interval as before
            
            # Ensure the interval is within the defined bounds
            interval = max(self.interval_min, min(self.interval_max, interval))

            # To avoid infinite loop situations when nearing total_duration
            if sum(intervals) + interval > total_duration:
                intervals.append(total_duration - sum(intervals))
                break
            else:
                intervals.append(interval)
        print(intervals)
        return intervals

    def play_sound(self, filename):
        pygame.mixer.Sound(filename).play()

if __name__ == '__main__':
    root = tk.Tk()
    app = GapLearningApp(root)
    root.mainloop()
