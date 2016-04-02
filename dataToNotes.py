from musicXML_bindings import *
## TODO:
## Parse pitch and octave
## Handle ties over between measures
## Maybe noise canceling?
## Note with beatlength 0?
totalNumMeasures = 0
beatToNum = {"16th" : 0.25,    # d signals dotted note
			 "d16th" : 0.375,
			 "eighth" : 0.5,
			 "deighth" : 0.75,
			 "quarter" : 1, 
			 "dquarter" : 1.5,
			 "half" : 2, 
			 "dhalf" : 3,
			 "whole" : 4}
numToBeat = dict((y, x) for x, y in beatToNum.iteritems())
numToBeat[3.75] = "whole"
numToBeat[3.5] = "whole"



##Jong calls this. Passes in array of arrays of notes, sample rate, and tempo
## Tempo (bpm)
def processNotes(notes = [], sampleRate = 44100.0, tempo = 120.0):

	notes = filterNoise(notes)
	deltaT = 1.0/(sampleRate/4096.0)
	beatsPerSec = tempo/60.0
	beatLength = 1.0/beatsPerSec
	beatsPerMeasure = 4 #assumed


	startEndTimes = findNoteTimes(notes, deltaT)
	convertToXML(startEndTimes, beatLength, beatsPerMeasure)

#Called by processNotes
# allNotes: array of array of notes
# deltaT: length of each time slice that each array entry represents
# return: a list of (pitch, startTime, endTime)
# Tested and works well with artificial array. 
def findNoteTimes(allNotes, deltaT):
	allNotes.append([]) # to detect the last note stopped.
	currentNotes = {} #pitch : startTime
	out = []
	time = 0
	for notes in allNotes:
		prevNotes = set(list(currentNotes.keys())) ##Double check that this list is populated correctly
		
		# Track notes that are starting in this timestamp
		for note in notes: 
			if note not in currentNotes: # note is starting here
				currentNotes[note] = time

		# Find notes that end in this timestamp and track in Out
		notes = set(notes)
		ended = prevNotes - notes
		for note in list(ended):
			out.append((note, currentNotes.pop(note), time))

		time += deltaT

	return out

#Converts notes' raw start and end times to actual XML using Leo's functions.
# startEndTimes: a list of (pitch, startTime, endTime) in seconds, sorted by
#               increasing END time.
# beatLength: length of a single beat in seconds
# beatsPerMeasure: Number of beats per measure.
# Tested and works well.
def convertToXML(startEndTimes, beatLength, beatsPerMeasure):
	global totalNumMeasures
	# Approximate start and ending beat for each note, and group chords.
	notes = [] #List of (pitches, beatNum, length, measNum, beatInMeas), e.g. (["c3", "e3"], 21, 0.5, 5, 1). 
	beats = {} # Dict of dicts {measNum : {beatInMeas: [(pitch, length)]}}
	for note in startEndTimes:
		#Extract useful values for this note
		pitch = note[0]
		startBeat = approxBeatNum16(note[1], beatLength)
		endBeat = approxBeatNum16(note[2], beatLength)
		measNum = startBeat//beatsPerMeasure
		beatLen = endBeat - startBeat
		if endBeat > (measNum + 1) * 4:
			beatLen = (measNum + 1) * 4 - startBeat
		if beatLen != 0:
			if beatLen <= 1:
				beatLen = numToBeat[approxBeatNum16(beatLen, 1)]
			elif beatLen <= 2: 
				beatLen = numToBeat[approxBeatNum8(beatLen, 1)]
			else:
				beatLen = numToBeat[approxBeatNum4(beatLen, 1)]
			measNum = startBeat//beatsPerMeasure
			totalNumMeasures = measNum #Probably safe since they're in order
			beatInMeas = startBeat% beatsPerMeasure

			# Add this information to notes and beats
			notes.append((pitch, startBeat, beatLen, measNum, beatInMeas))
			if measNum not in beats:
				beats[measNum] = {}
			thisMeasure = beats[measNum]
			if beatInMeas not in thisMeasure:
				thisMeasure[beatInMeas] = []
			thisMeasure[beatInMeas].append((pitch, beatLen))
	print "Notes: ", notes
	print "Beats: ", beats
	beatsToXML(beats)

#Converts a beats dictionary, divided by measure, into useful chord, note, rest definitions
# Then actually makes the XML stuff
# beats: Dict of dicts {measNum : {beatInMeas: [(pitch, length)]}}
# Untested.
def beatsToXML(beats):
	score = Score("a song", 4, 1) #assumed for now
	measNum = 0
	trailingMeasures = False
	while measNum <= int(totalNumMeasures) or trailingMeasures:
		trailingMeasures = False
		thisMeasure = Measure()
		score.add_measure(thisMeasure)
		measBeats = beats.get(measNum) # dictionary {beatInmeas: [(pitch, length)]}

		if measBeats is None:
			thisMeasure.add_element(Rest(numToBeat[4], False))
		else: 
			currBeat = 0 #when the previous note ended
			for beat in sorted(measBeats.keys()):
				if beat >= 4:
					print "Something went wrong, beat is greater than 4."
				notes = measBeats[beat] #list [(pitch, length)]
				if currBeat < beat: # Fill in a rest
					fillInRest(thisMeasure, beat - currBeat)

				lenMax = 4 - currBeat
				if lenMax != 0:
					if len(notes) > 1: # Make chord
						c = Chord()
						chordLen = notes[0][1] #assume all notes in chord same len
						if beatToNum[chordLen] > lenMax: #rest of chord overflows into next measure
							overflowLen = beatToNum[chordLen] - lenMax
							addOverflow(notes, numToBeat[overflowLen], beats, measNum + 1)
							trailingMeasures = True
						chordLen, dotted = convDot(chordLen, lenMax)
						for note in notes:
							pitch, octave = convPitch(note[0])
							c.add_note(Note(pitch, octave, chordLen, dotted))
						thisMeasure.add_element(c)
						currBeat += min(beatToNum[chordLen], lenMax)

					elif len(notes) == 1: # Make note
						if (beatToNum[notes[0][1]] + currBeat) > 4: #rest of note overflows into next measure
							overflowLen = (beatToNum[notes[0][1]] + currBeat) - 4
							addOverflow(notes, numToBeat[overflowLen], beats, measNum + 1)
							trailingMeasures = True
						noteLen, dotted = convDot(notes[0][1], lenMax)
						pitch, octave = convPitch(notes[0][0])
						thisMeasure.add_element(Note(pitch, octave, noteLen, dotted))
						currBeat += min(beatToNum[notes[0][1]], lenMax)
					else: 
						print "Something went wrong in dataToNotes.py, beatsToXML."
			if currBeat < 4: # trailing rest in measure
				fillInRest(thisMeasure, 4-currBeat)
		measNum += 1
	print score
	score.write_to_file()

def fillInRest(measure, numBeats):
	numBeats = round(numBeats * 16) / 16
	if numBeats == 0.25:
		measure.add_element(Rest("16th"))
	elif numBeats == 0.5:
		measure.add_element(Rest("eighth"))
	elif numBeats == 0.75:
		measure.add_element(Rest("eighth", True))
	elif numBeats <= 1.25:
		measure.add_element(Rest("quarter"))
	elif numBeats == 1.5:
		measure.add_element(Rest("eighth"))
		measure.add_element(Rest("quarter"))
	elif numBeats <= 2.5:
		measure.add_element(Rest("half"))
	elif numBeats <= 3.5:
		measure.add_element(Rest("quarter"))
		measure.add_element(Rest("half"))
	else:
		measure.add_element(Rest("whole"))


##Helper function for beatsToXML
# notes: list [(pitch, length)], length is previous length, don't use.
# length: string length
# beats: dict of dicts {measNum : {beatInMeas: [(pitch, length)]}}
# meas: measure to add to
def addOverflow(notes, length, beats, meas):
	if beats.get(meas) is None:
		beats[meas] = {} # make new measure
	if beats[meas].get(0) is None:
		beats[meas][0] = []
	for note in notes:
		beats[meas][0].append((note[0], length))

def convDot(beatLen, lenMax):
	if beatToNum[beatLen] > lenMax:
		return convDot(numToBeat[lenMax], 4)
	dotted = False
	if beatLen[0] == 'd':
		beatLen = beatLen[1:]
		dotted = True
	return (beatLen, dotted)

def convPitch(pitch):
	if len(pitch) == 2:
		return pitch[0], int(pitch[1])
	return pitch[0:2], int(pitch[2])

def approxBeatNum16(time, beatLength): 
	beat = time/beatLength
	return round(beat * 4) / 4

def approxBeatNum8(time, beatLength):
	beat = time/beatLength
	return round(beat * 2) / 2

def approxBeatNum4(time, beatLength):
	return round(time/beatLength)

def filterNoise(notes):
	return notes

def makeNotes(freq):
	# Use only a "r" in notes to specify a rest. Use "abc" or corresponding values to specify chord".
	notes = [("A2A2", 2), ("B2", 1), ("A2", 1), 
		("r", 4), 
		("C3", 4), 
		("A3", 0.25), ("B3", 0.25), ("C2", 0.5), ("A2", 0.5),  ("B2", 0.5), ("r", 2),
		("r", 2), ("A4", 1), ("r", 0.5), ("B4", 0.5),
		("A5", 1), ("r", 2), ("B5", 1),
		("A5", 3), ("r", 1),
		("A5", 1.5), ("r", 0.5), ("B5", 0.75), ("r", 0.25), ("C5", 1),
		("A3", 0.75), ("A2", 0.25), ("A3", 0.25), ("r", 0.75), ("C3", 2), 
		("A2", 3), ("B2", 2), ("r", 3),
		("A3", 2), ("B2", 2),
		("A3", 2.75)]
	out = []
	for note in notes:
		pitches = note[0]
		length = note[1]
		if pitches == "r":
			for _ in range(int(length * freq)):
				out.append([])
		else: 
			for _ in range(int(length * freq)):
				out.append([pitches[i: i + 2] for i in range(0, len(pitches), 2)])
	return out

def test():
	#processNotes(makeNotes(4), 4, 60)

	notes = []
	arr = []
	inArray = False
	note = ""
	inNote = False
	with open("./output.txt", 'r') as f:
		while True:
			c = f.read(1)
			if not c:
				break
			if c == '[':
				inArray = True
			elif c == ']':
				notes.append(arr)
				arr = []
				inArray = False
			elif c == '\'' and not inNote:
				inNote = True
			elif c == '\'' and inNote:
				inNote = False
				arr.append(note)
				note = ""
			elif inNote:
				note += c
	processNotes(notes)

if __name__ == "__main__":
	test()