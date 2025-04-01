import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import mido

# --- Encoding Function using mido (MIDI export only) ---
def text_to_midi(text, filename):
    # Define the pentatonic scale: C, D, E, G, A (starting at middle C = 60)
    base_notes = [60, 62, 64, 67, 69]
    # Punctuation mapping: space → 70, comma → 71, full stop → F♯4 (66)
    punctuation_map = {
        ' ': 70,
        ',': 71,
        '.': 66
    }
    duration_ticks = 480  # quarter note duration (assuming 480 ticks per beat)
    
    # Create a new MIDI file with default ticks_per_beat=480
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo (100 BPM → 600,000 microseconds per beat)
    tempo = 400000
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    # Process each character in the text.
    for char in text:
        if char.isalpha():
            letter = char.upper()
            num = ord(letter) - ord('A') + 1  # A=1, B=2, …, Z=26
            index = (num - 1) % 5
            octave_offset = 12 * ((num - 1) // 5)
            note = base_notes[index] + octave_offset
            channel = 0  # Letters on channel 0.
            track.append(mido.Message('note_on', note=note, velocity=100, time=0, channel=channel))
            track.append(mido.Message('note_off', note=note, velocity=0, time=duration_ticks, channel=channel))
        elif char in punctuation_map:
            note = punctuation_map[char]
            channel = 1  # Punctuation on channel 1.
            track.append(mido.Message('note_on', note=note, velocity=100, time=0, channel=channel))
            track.append(mido.Message('note_off', note=note, velocity=0, time=duration_ticks, channel=channel))
        else:
            # Skip any other characters.
            pass

    mid.save(filename)
    return filename

# --- Decoding Function using mido ---
def midi_to_text(filename):
    # Build reverse mapping for letter notes.
    base_notes = [60, 62, 64, 67, 69]
    note_to_letter = {}
    for num in range(1, 27):  # For letters A to Z.
        index = (num - 1) % 5
        octave_offset = 12 * ((num - 1) // 5)
        note_val = base_notes[index] + octave_offset
        letter = chr((num - 1) + ord('A'))
        note_to_letter[note_val] = letter

    punctuation_map = {
        70: ' ',
        71: ',',
        66: '.'
    }
    
    mid = mido.MidiFile(filename)
    output_text = ""
    for msg in mid.tracks[0]:
        if msg.type == 'note_on' and msg.velocity > 0:
            if msg.channel == 0:
                output_text += note_to_letter.get(msg.note, '?')
            elif msg.channel == 1:
                output_text += punctuation_map.get(msg.note, '')
    return output_text

# --- GUI Application ---
exported_file = ""

def encode_action():
    global exported_file
    text = encode_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Please enter text to encode.")
        return

    # Only MIDI export is available now.
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
        # Open the MIDI file with the default associated program.
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

encode_frame.pack(fill="both", expand=True)
root.mainloop()
