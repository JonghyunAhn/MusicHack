from myMusicXML_bindings import *
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

##Jong calls this. Passes in array of arrays of notes, sample rate, and tempo
## Tempo (bpm)
def processNotes(notes, sampleRate, tempo):
	notes = filterNoise(notes)
	deltaT = 1.0/sampleRate
	beatsPerSec = tempo/60
	beatLength = 1/beatsPerSec
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
		beatLen = numToBeat[endBeat - startBeat]
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
	for measNum in range(int(totalNumMeasures + 1)):
		thisMeasure = Measure()
		score.add_measure(thisMeasure)
		measBeats = beats.get(measNum) # dictionary {beatInmeas: [(pitch, length)]}

		if measBeats is None:
			thisMeasure.add_rest(Rest(numToBeat[4], False))
		else: 
			currBeat = 0 #when the previous note ended
			for beat in sorted(measBeats.keys()):
				notes = measBeats[beat] #list [(pitch, length)]
				if currBeat < beat: # Fill in a rest
					restLen = numToBeat[beat-currBeat]
					restLen, dotted = convDot(restLen)
					thisMeasure.add_rest(Rest(restLen, dotted))
					currBeat = beat
				if len(notes) > 1: # Make chord
					c = Chord()
					chordLen = notes[0][1] #assume all notes in chord same len
					chordLen, dotted = convDot(chordLen)
					for note in notes:
						pitch, octave = convPitch(note[0])
						c.add_note(Note(pitch, octave, chordLen, dotted))
					thisMeasure.add_chord(c)
					currBeat += beatToNum[chordLen]
				elif len(notes) == 1:
					noteLen, dotted = convDot(notes[0][1])
					pitch, octave = convPitch(notes[0][0])
					thisMeasure.add_note(Note(pitch, octave, noteLen, dotted))
					currBeat += beatToNum[notes[0][1]]
				else: 
					print "Something went wrong in dataToNotes.py, beatsToXML."
			if currBeat != 4: # trailing rest in measure
				restLen, dotted = convDot(numToBeat[4 - currBeat])
				thisMeasure.add_rest(Rest(restLen, dotted))
	print score

def convDot(beatLen):
	dotted = False
	if beatLen[0] == 'd':
		beatLen = beatLen[1:]
		dotted = True
	return (beatLen, dotted)

def convPitch(pitch):
	return pitch[0], int(pitch[1])

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
	notes = [("a2c2", 2), ("b2", 1), ("a2", 1), 
		("r", 4), 
		("c3", 4), 
		("a3", 0.25), ("b3", 0.25), ("c2", 0.5), ("a2", 0.5),  ("b2", 0.5), ("r", 2),
		("r", 2), ("a4", 1), ("r", 0.5), ("b4", 0.5),
		("a5", 1), ("r", 2), ("b5", 1),
		("a5", 3), ("r", 1),
		("a5", 1.5), ("r", 0.5), ("b5", 0.75), ("r", 0.25), ("c5", 1)]
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
	processNotes(makeNotes(4), 4, 60)

test()