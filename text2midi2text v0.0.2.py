import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import mido

# --- Revised Encoding Function using mido ---
def text_to_midi(text, filename):
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo (e.g., 400000 microseconds per beat ≈ 100 BPM)
    track.append(mido.MetaMessage('set_tempo', tempo=400000, time=0))
    
    duration_ticks = 480  # Fixed note duration (quarter note)
    for char in text:
        # Map every character to a MIDI note: note = ord(char) + 1
        note = ord(char) + 1
        if 0 <= note <= 127:
            track.append(mido.Message('note_on', note=note, velocity=100, time=0, channel=0))
            track.append(mido.Message('note_off', note=note, velocity=0, time=duration_ticks, channel=0))
        else:
            # Warn if the character is out of the MIDI note range (will be skipped)
            print(f"Warning: Character '{char}' (ord {ord(char)}) out of range and was skipped.")
    
    mid.save(filename)
    return filename

# --- Revised Decoding Function using mido ---
def midi_to_text(filename):
    mid = mido.MidiFile(filename)
    output = ""
    # Process only the first track (assumes all messages are there)
    for msg in mid.tracks[0]:
        if msg.type == 'note_on' and msg.velocity > 0 and msg.channel == 0:
            output += chr(msg.note - 1)
    return output

# --- GUI Application ---
exported_file = ""

def encode_action():
    global exported_file
    text = encode_text.get("1.0", tk.END).rstrip("\n")
    if not text:
        messagebox.showerror("Error", "Please enter text to encode.")
        return

    save_path = filedialog.asksaveasfilename(
        defaultextension=".mid",
        filetypes=[("MIDI files", "*.mid")],
        title="Save MIDI file as..."
    )
    if not save_path:
        return

    try:
        text_to_midi(text, save_path)
        exported_file = save_path
        messagebox.showinfo("Success", f"MIDI file saved as:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def play_action():
    if not exported_file or not os.path.exists(exported_file):
        messagebox.showerror("Error", "No exported file available to play.")
        return

    try:
        os.startfile(exported_file)
    except Exception as e:
        messagebox.showerror("Playback Error", str(e))

def decode_action():
    file_path = filedialog.askopenfilename(
        filetypes=[("MIDI files", "*.mid")],
        title="Select a MIDI file to decode..."
    )
    if not file_path:
        return

    try:
        decoded = midi_to_text(file_path)
        decode_result.delete("1.0", tk.END)
        decode_result.insert(tk.END, decoded)
        messagebox.showinfo("Decoded", "Decoding complete.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_encode():
    encode_frame.pack(fill="both", expand=True)
    decode_frame.forget()

def show_decode():
    decode_frame.pack(fill="both", expand=True)
    encode_frame.forget()

# Build the main GUI.
root = tk.Tk()
root.title("Text/MIDI Encoder-Decoder (MIDI Only)")

mode_var = tk.StringVar(value="encode")
mode_frame = tk.Frame(root)
mode_frame.pack(pady=10)
tk.Radiobutton(mode_frame, text="Encode", variable=mode_var, value="encode", command=show_encode).pack(side="left", padx=5)
tk.Radiobutton(mode_frame, text="Decode", variable=mode_var, value="decode", command=show_decode).pack(side="left", padx=5)

# --- Encode Frame ---
encode_frame = tk.Frame(root)
tk.Label(encode_frame, text="Enter text to encode:").pack(pady=5)
encode_text = scrolledtext.ScrolledText(encode_frame, width=60, height=10)
encode_text.pack(pady=5)
buttons_frame = tk.Frame(encode_frame)
buttons_frame.pack(pady=10)
tk.Button(buttons_frame, text="Export MIDI", command=encode_action).pack(side="left", padx=5)
tk.Button(buttons_frame, text="Play MIDI", command=play_action).pack(side="left", padx=5)

# --- Decode Frame ---
decode_frame = tk.Frame(root)
tk.Button(decode_frame, text="Select MIDI File to Decode", command=decode_action).pack(pady=5)
tk.Label(decode_frame, text="Decoded Text:").pack(pady=5)
decode_result = scrolledtext.ScrolledText(decode_frame, width=60, height=10)
decode_result.pack(pady=5)

# Start with the encode frame visible.
encode_frame.pack(fill="both", expand=True)
root.mainloop()
