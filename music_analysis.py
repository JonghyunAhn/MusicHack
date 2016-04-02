import librosa as lib
import sklearn.decomposition as decomp
import numpy as np

import dataToNotes as data 

from scipy import signal

INDEX_TO_NOTE = {1 : 'C', 2: 'C#', 3: 'D', 4: 'D#', 5:'E', 6:'F', 7:'F#', 8:'G', 9: 'G#', 10: 'A', 11: 'A#', 12: 'B'}

def loudness_filter(song):
    b1, a1 = [0.98500175787242, -1.97000351574484, 0.98500175787242], [1.96977855582618, -0.97022847566350] #2nd order butterworth 
    b2 = [0.05418656406430 , -0.02911007808948, -0.00848709379851, -0.00851165645469, -0.00834990904, 0.02245293253, -0.02596338512915, 0.01624864962975, -0.00240879051584, 0.00674613682247, -0.00187763777362]     
    a2 = [3.47845948550071, -6.36317777566148, 8.54751527471874, -9.47693607801280, 8.81498681370155, -6.85401540936998, 4.39470996079559, -2.19611684890774, 0.75104302451432, -0.13149317958808] #Yulewalk filter 10th order

    filter_song = signal.lfilter(b2, a2, signal.lfilter(b1, a1, song))
    return filter_song

def load_song(audio_file, sr=44100., duration = None):
    song, sr_song = lib.load(audio_file, sr=sr, duration = duration)
    if len(song.shape) == 2:
        song = np.average(song, axis=1)
    song = loudness_filter(song)
    return song, sr_song 

def find_essential_notes(song, sr):
    cqt = np.abs(lib.cqt(song, sr=sr, hop_length=128, n_bins=84, bins_per_octave=12,real=False, filter_scale=0.75))
    strong_elem = []
    for time_slice in cqt.T:
        local_peaks = signal.argrelextrema(time_slice, np.greater)[0]
        peaks = []
        for elem in local_peaks:
            db = 20 * np.log10(time_slice[elem])
            if db > -110:
                peaks.append(elem)
        strong_elem.append(peaks)
        
    weight1 = 1.0
    weight2 = 1.5
    weight3 = 1.0

    notes_idx = []
    for idx,notes in enumerate(strong_elem):
        if len(notes) == 0 or len(notes_idx) == 0:
            notes_idx.append(notes)
        else:
            if len(notes_idx[idx-1]) == 0:
                note_choice = []
                power_sum = sum(cqt[note][idx] for note in notes)
                for note in notes:
                    score = weight1 * cqt[note][idx]/power_sum - weight3 * abs(84/2. - note)/84.
                    note_choice.append((score,note))
                notes_idx.append([max(note_choice)[1]])
            else:
                prev_note = notes_idx[idx-1]
                power_sum = sum(cqt[note][idx] for note in notes)
                note_choice = []
                for note in notes:
                    score = weight1 * cqt[note][idx]/power_sum - weight2 * abs(note - prev_note)/84. - weight3 * abs(84/2. - note)/84.
                    note_choice.append((score,note))
                notes_idx.append([max(note_choice)[1]])
                                           
    notes = []
    for peaks in notes_idx:
        note_slice = [(idx/12 + 1, idx % 12 + 1) for idx in peaks]
        note_slice = [INDEX_TO_NOTE[note[1]]+ str(note[0]) for note in note_slice]
        notes.append(note_slice)

    return notes

def extract_tempo(song, sr):
    tempo, _ = lib.beat.beat_track(song, sr=sr)
    return tempo

def test():
    song,sr = load_song('./rondo.mp3')
    notes = find_essential_notes(song, sr)
    tempo = extract_tempo(song, sr) / 4
    data.processNotes(notes, float(sr), tempo=tempo) 

if __name__ == '__main__': test()
