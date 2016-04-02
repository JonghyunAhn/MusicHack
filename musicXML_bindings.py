# bindings for the MusicXML format
# each function writes sequentially

class Score:
    def __init__(self, name, beats, beat_type):
        """
        Parameters
        ----------
        name: string, name of the piece
        beats: int, beats per measure
        beat_type: int, which note subdivision is one beat
        """
        pass

    def add_measure(self, measure):
        pass

class Measure:
    def __init__(self):
        pass

    def add_chord(self, chord):
        pass

    def add_note(self, note):
        pass

class Chord:
    def __init__(self):
        pass

    def add_note(self, note):
        pass

class Note:
    def __init__(self, pitch, note_length, semi):
        """
        Parameters
        ----------
        pitch: string, the note pitch (capitalized)
        note_length: string, the length of the note (quarter, half, whole, etc.)
        semi: string, the semitone i.e. sharp or flat
        """
        pass

class Rest:
    def __init__(self, note_length):
        pass
