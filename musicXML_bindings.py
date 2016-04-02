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
        if self.current_measure == 1:
            measure.set_first_measure(self.beats, self.beat_type)
        measure.set_measure_number(self.current_measure)
        self.measures.append(measure)
        self.current_measure += 1

    def get_xml(self):
        return '<score-partwise version="3.0">\n\t<part-list>\n\t\t<score-part id="P0">\n\t\t\t<part-name>{}</part-name>\n\t\t</score-part>\n\t</part-list>\n\t<part id="P0">'.format(self.name) + "".join([i.get_xml() for i in self.measures]) + "\n\t</part>\n</score-partwise>"

    def write_to_file(self):
        with open(self.name + ".xml", 'w') as f:
            f.write(self.get_xml())

    def __str__(self):
        s = "Score: "+ self.name + " " +  str(self.beats) + " " +  str(self.beat_type) + "\n"
        for measure in self.measures:
            s += str(measure) + "\n"
        return s

class Measure:
    def __init__(self):
        self.elements = []
        self.first_measure_string = "\n\t\t\t<attributes>\n\t\t\t\t<divisions>1</divisions>\n\t\t\t</attributes>"

    def add_element(self, element):
        self.elements.append(element)

    def set_measure_number(self, number):
        self.number = number

    def set_first_measure(self, beats, beat_type):
        self.first_measure_string = "\n\t\t\t<attributes>\n\t\t\t\t<divisions>1</divisions\n\t\t\t\t<time>\n\t\t\t\t\t<beats>{}</beats>\n\t\t\t\t\t<beat-type>{}</beat-type>\n\t\t\t\t</time>\n\t\t\t\t<clef>\n\t\t\t\t\t<sign>G</sign>\n\t\t\t\t\t<line>2</line>\n\t\t\t\t</clef>\n\t\t\t</attributes>".format(beats, beat_type)

    def get_xml(self):
        return '\n\t\t<measure number="{}">{}'.format(self.number, self.first_measure_string) + "".join([i.get_xml() for i in self.elements]) + "\n\t\t</measure>"

    def __str__(self):
        s = "\tMeasure: "
        for elem in self.elements:
            s +=  str(elem) + " "
        return s

class Chord:
    def __init__(self):
        self.notes = []

    def add_note(self, note):
        if len(self.notes) > 0:
            note.set_chord()
        self.notes.append(note)

    def get_xml(self):
        return "".join([i.get_xml() for i in self.notes])

    def __str__(self):
        s = "Chord< "
        for note in self.notes:
            s += str(note) + " "
        s += ">"
        return s

class Note:
    def __init__(self, pitch, octave, note_length, dot=False, semi=""):
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
        self.chord_string = ""
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

    def set_chord(self):
        self.chord_string = "\n\t\t\t\t<chord/>"

    def get_xml(self):
        return "\n\t\t\t<note>{}\n\t\t\t\t<pitch>\n\t\t\t\t\t<step>{}</step>\n\t\t\t\t\t<octave>{}</octave>\n\t\t\t\t\t<alter>{}</alter>\n\t\t\t\t</pitch>\n\t\t\t\t<type>{}</type>{}\n\t\t\t</note>".format(self.chord_string, self.pitch, self.octave, self.semi, self.note_length, self.dot_string)

    def __str__(self):
        if self.dot_string != "":
            return self.pitch + str(self.octave) + "-" + self.note_length + "*"
        return self.pitch + str(self.octave) + "-" + self.note_length

class Rest:
    def __init__(self, note_length, dot=False):
        self.note_length = note_length
        self.dot_string = "\n\t\t\t\t<dot/>" if dot else ""

    def get_xml(self):
        return "\n\t\t\t<note>\n\t\t\t\t<rest/>\n\t\t\t\t<type>{}</type>{}\n\t\t\t</note>".format(self.note_length, self.dot_string)

    def __str__(self):
        if self.dot_string != "":
            return "rest-" + self.note_length + "*"
        return "rest-" + self.note_length
