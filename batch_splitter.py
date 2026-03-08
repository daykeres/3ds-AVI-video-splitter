import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import tempfile
from PIL import Image, ImageTk

class BatchVideoSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual-Channel AVI Video Manager")
        self.root.geometry("1000x700")
        
        # Data storage
        self.video_list = [] # List of dictionaries containing video info
        self.selected_index = None
        self.output_dir = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- UI Styling ---
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        
        # Main Layout Container
        main_paned = tk.PanedWindow(self.root, orient="horizontal", sashrelief="raised", sashwidth=4)
        main_paned.pack(fill="both", expand=True)

        # --- LEFT PANEL: File List ---
        left_frame = tk.Frame(main_paned, width=600, bg="#e0e0e0")
        main_paned.add(left_frame)
        
        tk.Button(left_frame, text="➕ Add AVI Files", command=self.add_files, bg="#007bff", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=5, padx=5)
        
        self.canvas = tk.Canvas(left_frame, bg="#e0e0e0")
        self.scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#e0e0e0")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- RIGHT PANEL: Configuration & Preview ---
        right_frame = tk.Frame(main_paned, width=500, bg="white")
        main_paned.add(right_frame)
        
        main_paned.paneconfig(left_frame, stretch="always")
        main_paned.paneconfig(right_frame, stretch="never")

        self.lbl_selected_title = tk.Label(right_frame, text="Select a video from the list", font=("Arial", 12, "bold"), bg="white")
        self.lbl_selected_title.pack(pady=20)

        # Dual Preview Button (HStack)
        self.btn_dual = tk.Button(right_frame, text="Preview [ A | B ]", command=self.play_dual_loop, 
                                  state="disabled", bg="#17a2b8", fg="white", font=("Arial", 11, "bold"), padx=20, pady=10)
        self.btn_dual.pack(pady=10)

        # Individual File Export Options
        export_options_frame = tk.LabelFrame(right_frame, text=" Export Settings (Selected File) ", bg="white", padx=20, pady=20)
        export_options_frame.pack(pady=20)

        self.chk_a_var = tk.BooleanVar(value=True)
        self.chk_b_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(export_options_frame, text="Export Channel A", variable=self.chk_a_var, bg="white", command=self.update_video_settings).pack(anchor="w")
        tk.Checkbutton(export_options_frame, text="Export Channel B", variable=self.chk_b_var, bg="white", command=self.update_video_settings).pack(anchor="w")

        # --- BOTTOM SECTION: Global Export Control ---
        bottom_frame = tk.Frame(right_frame, bg="#f8f9fa", pady=20)
        bottom_frame.pack(side="bottom", fill="x")

        tk.Button(bottom_frame, text="📂 Select Destination Folder", command=self.select_dest).pack()
        self.lbl_dest = tk.Label(bottom_frame, text="Destination: Not selected", fg="gray", bg="#f8f9fa")
        self.lbl_dest.pack(pady=5)

        self.btn_export_all = tk.Button(bottom_frame, text="EXPORT ALL SELECTED", command=self.run_batch_export,
                                       bg="#28a745", fg="white", font=("Arial", 12, "bold"), state="disabled", padx=30, pady=15)
        self.btn_export_all.pack(pady=10)
        
        self.status = tk.Label(self.root, text="Ready", bd=1, relief="sunken", anchor="w")
        self.status.pack(side="bottom", fill="x")

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("AVI Video", "*.avi"), ("All Files", "*.*")])
        if files:
            for f in files:
                # Avoid duplicates
                if any(v['path'] == f for v in self.video_list): continue
                
                video_data = {
                    'path': f,
                    'name': os.path.basename(f),
                    'thumb': self.generate_single_thumb(f),
                    'export_a': True,
                    'export_b': True
                }
                self.video_list.append(video_data)
            self.refresh_list()
            self.btn_export_all.config(state="normal")

    def generate_single_thumb(self, path):
        """Generates a small thumbnail from the first video stream."""
        temp = tempfile.gettempdir()
        out_img = os.path.join(temp, f"t_{hash(path)}.jpg")
        # Map first video stream (0:v:0) and take 1 frame
        subprocess.run(["ffmpeg", "-y", "-i", path, "-map", "0:v:0", "-vframes", "1", out_img], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(out_img):
            img = Image.open(out_img).resize((80, 45), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    def remove_file(self, index):
        """Removes a file from the list and resets selection if needed."""
        del self.video_list[index]
        if self.selected_index == index:
            self.selected_index = None
            self.lbl_selected_title.config(text="Select a video from the list")
            self.btn_dual.config(state="disabled")
        elif self.selected_index is not None and self.selected_index > index:
            self.selected_index -= 1
            
        if not self.video_list:
            self.btn_export_all.config(state="disabled")
            
        self.refresh_list()

    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for i, video in enumerate(self.video_list):
            item_bg = "#cfe2ff" if i == self.selected_index else "#e0e0e0"
            
            f = tk.Frame(self.scroll_frame, bg=item_bg, pady=5)
            f.pack(fill="x", padx=2, pady=2)
            
            # Clickable area for selection
            click_area = tk.Frame(f, bg=item_bg, cursor="hand2")
            click_area.pack(side="left", fill="both", expand=True)
            click_area.bind("<Button-1>", lambda e, idx=i: self.select_video(idx))

            if video['thumb']:
                lbl_img = tk.Label(click_area, image=video['thumb'], bg=item_bg)
                lbl_img.pack(side="left", padx=5)
                lbl_img.bind("<Button-1>", lambda e, idx=i: self.select_video(idx))

            lbl_txt = tk.Label(click_area, text=video['name'], bg=item_bg, font=("Arial", 8), anchor="w")
            lbl_txt.pack(side="left", fill="x", expand=True)
            lbl_txt.bind("<Button-1>", lambda e, idx=i: self.select_video(idx))
            
            # Remove Button
            btn_del = tk.Button(f, text="❌", command=lambda idx=i: self.remove_file(idx), 
                                bg="#ffcccc", fg="red", relief="flat", font=("Arial", 8))
            btn_del.pack(side="right", padx=5)

    def select_video(self, index):
        """Displays settings for the clicked video."""
        self.selected_index = index
        video = self.video_list[index]
        self.lbl_selected_title.config(text=f"Editing: {video['name']}")
        self.chk_a_var.set(video['export_a'])
        self.chk_b_var.set(video['export_b'])
        self.btn_dual.config(state="normal")
        self.refresh_list()

    def update_video_settings(self):
        """Saves checkbox states into the video object."""
        if self.selected_index is not None:
            self.video_list[self.selected_index]['export_a'] = self.chk_a_var.get()
            self.video_list[self.selected_index]['export_b'] = self.chk_b_var.get()

    def play_dual_loop(self):
        """Optimized high-speed dual preview with loop."""
        if self.selected_index is None: return
        path = self.video_list[self.selected_index]['path']
        
        # FFMPEG: Feed decoded raw video into NUT pipe for ultra-low latency
        cmd_ffmpeg = [
            "ffmpeg", "-stream_loop", "-1", "-i", path,
            "-filter_complex", "[0:v:0][0:v:1]hstack=inputs=2",
            "-f", "nut", "-c:v", "rawvideo", "-pix_fmt", "yuv420p", "-"
        ]
        
        # FFPLAY: High performance flags to prevent lag
        ffplay_args = [
            "ffplay", "-i", "-", "-window_title", f"Dual Loop: {os.path.basename(path)}",
            "-fflags", "nobuffer", "-flags", "low_delay", "-framedrop", "-alwaysontop"
        ]
        
        proc = subprocess.Popen(cmd_ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        subprocess.Popen(ffplay_args, stdin=proc.stdout)

    def select_dest(self):
        d = filedialog.askdirectory()
        if d:
            self.output_dir = d
            self.lbl_dest.config(text=f"Destination: {d}", fg="black")

    def run_batch_export(self):
        if not self.output_dir:
            messagebox.showwarning("Attention", "Please select a destination folder.")
            return
        
        self.btn_export_all.config(state="disabled")
        threading.Thread(target=self.batch_work).start()

    def batch_work(self):
        """Lossless export using '-c copy' to preserve resolution, bitrate, and FPS."""
        for video in self.video_list:
            base = os.path.splitext(video['name'])[0]
            
            # Export Channel A (Stream 0 and Audio 1)
            if video['export_a']:
                dest_a = os.path.join(self.output_dir, f"{base}_A.avi")
                self.status.config(text=f"Exporting {video['name']} (Channel A)...")
                subprocess.run(["ffmpeg", "-y", "-i", video['path'], "-map", "0:0", "-map", "0:1", "-c", "copy", dest_a], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Export Channel B (Stream 2 and Audio 1)
            if video['export_b']:
                dest_b = os.path.join(self.output_dir, f"{base}_B.avi")
                self.status.config(text=f"Exporting {video['name']} (Channel B)...")
                subprocess.run(["ffmpeg", "-y", "-i", video['path'], "-map", "0:2", "-map", "0:1", "-c", "copy", dest_b], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self.root.after(0, self.finish_batch)

    def finish_batch(self):
        self.btn_export_all.config(state="normal")
        self.status.config(text="Batch process completed successfully.")
        messagebox.showinfo("Success", f"All files have been saved to:\n{self.output_dir}")
        os.startfile(self.output_dir) # Automatically open destination folder

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchVideoSplitter(root)
    root.mainloop()
