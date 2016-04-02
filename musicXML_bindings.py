# bindings for the MusicXML format
# each function writes sequentially

class Score:
    def __init__(self, name, beats, beat_type):
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
        pass

class Rest:
    def __init__(self, note_length):
        pass
