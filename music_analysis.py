import librosa as lib
import sklearn.decomposition as decomp
import numpy as np

from scipy import signal

INDEX_TO_NOTE = {1 : 'C', 2: 'C#', 3: 'D', 4: 'D#', 5:'E', 6:'F', 7:'F#', 8:'G', 9: 'G#', 10: 'A', 11: 'A#', 12: 'B'}

def loudness_filter(song):
    b1, a1 = [0.98500175787242, -1.97000351574484, 0.98500175787242], [1.96977855582618, -0.97022847566350] #2nd order butterworth 
    b2 = [0.05418656406430 , -0.02911007808948, -0.00848709379851, -0.00851165645469, -0.00834990904, 0.02245293253, -0.02596338512915, 0.01624864962975, -0.00240879051584, 0.00674613682247, -0.00187763777362]     
    a2 = [3.47845948550071, -6.36317777566148, 8.54751527471874, -9.47693607801280, 8.81498681370155, -6.85401540936998, 4.39470996079559, -2.19611684890774, 0.75104302451432, -0.13149317958808] #Yulewalk filter 10th order

    filter_song = signal.lfilter(b2, a2, signal.lfilter(b1, a1, song))
    return filter_song

def load_song(audio_file, sr=44100):
    song, sr_song = lib.load(audio_file, sr=sr)
    if len(song.shape) == 2:
        song = np.average(song, axis=1)
    tuning = lib.estimate_tuning(song)
    song = loudness_filter(song)
    return song, sr_song, tuning 

def find_essential_notes(song, sr, tuning):
    cqt = np.abs(lib.cqt(song, sr=sr, hop_length=256, n_bins=84, bins_per_octave=12, norm=2,real=False, tuning=tuning))
    strong_elem = []
    for time_slice in cqt.T:
        local_peaks = signal.argrelextrema(time_slice, np.greater)[0]
        peaks = []
        for elem in local_peaks:
            db = 20 * np.log10(time_slice[elem])
            if db > -80:
                peaks.append(elem)
        strong_elem.append(peaks)

    notes = []
    for time_slice in strong_elem:
        note_slice = [(idx/12 + 1, idx % 12 + 1) for idx in time_slice]
        note_slice = [INDEX_TO_NOTE[note[1]]+ str(note[0]) for note in note_slice]
        notes.append(note_slice)

    return notes

def extract_tempo(song, sr):
    return 

def test():
    song,sr, tuning = load_song('./twinkle.mp3')
    print find_essential_notes(song, sr, tuning)

if __name__ == '__main__': test()
