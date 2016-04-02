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
        self.name = name
        self.beats = beats
        self.beat_type = beat_type
        self.current_measure = 1
        self.measures = []

    def add_measure(self, measure):
        pass

    def get_xml(self):
        pass

class Measure:
    def __init__(self):
        self.notes = []

    def add_chord(self, chord):
        pass

    def add_note(self, note):
        pass

    def add_rest(self, rest):
        pass

    def get_xml(self):
        pass

class Chord:
    def __init__(self):
        self.notes = []

    def add_note(self, note):
        self.notes.append(note)

    def get_xml(self):
        pass

class Note:
    def __init__(self, pitch, octave, note_length, dot, semi=""):
        """
        Parameters
        ----------
        pitch: string, the note pitch (capitalized)
        octave: int, octave the note is on
        note_length: string, the length of the note (quarter, half, whole, etc.)
        dot: boolean, if there is a dot following the note
        semi: string, the semitone i.e. sharp or flat
        """
        self.pitch = pitch
        self.octave = octave
        self.note_length = note_length
        self.dot_string = "\n\t\t\t\t<dot/>" if dot else ""
        if semi == "flat":
            self.semi = -1
        elif semi == "double flat":
            self.semi = -2
        elif semi == "sharp":
            self.semi = 1
        elif semi == "double sharp":
            self.semi = 2
        else:
            self.semi = 0

    def get_xml(self):
        return "\n\t\t\t<note>\n\t\t\t\t<pitch>\n\t\t\t\t\t<step>{}</step>\n\t\t\t\t\t<octave>{}</octave>\n\t\t\t\t\t<alter>{}</alter>\n\t\t\t\t</pitch>\n\t\t\t\t<type>{}</type>{}\n\t\t\t</note>".format(self.pitch, self.octave, self.semi, self.note_length, self.dot_string)

class Rest:
    def __init__(self, note_length):
        self.note_length = note_length

    def get_xml(self):
        return "\n\t\t\t<note>\n\t\t\t\t<rest/>\n\t\t\t\t<type>{}</type>\n\t\t\t</note>".format(self.note_length)
