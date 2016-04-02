

# Find out start/end times for each note
# Find out where rests are
# Divide notes into measures
# Convert this to number of measure, location in measure, length of note
# Output array of notes [
# Write to XML


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
def convertToXML(startEndTimes, beatLength, beatsPerMeasure):
	# Do one pass to approximate start and ending beat for each note, and group chords.
	notes = [] #List of (pitches, beatNum, length, measNum, beatInMeas), e.g. (["c3", "e3"], 21, 0.5, 5, 1). 
	beats = {} # Dict of dicts {measNum : {beatInMeas: [(pitch, length)]}}
	lengths = ["whole", "half", "quarter", "eighth", "sixteenth"]
	for note in startEndTimes:
		#Extract useful values for this note
		pitch = note[0]
		startBeat = approxBeatNum16(note[1], beatLength)
		endBeat = approxBeatNum16(note[2], beatLength)
		beatLen = endBeat - startBeat
		if beatLen == 4:
			beatLen = lengths[0]
		elif beatLen == 2:
			beatLen = lengths[1]
		elif beatLen == 1:
			beatLen = lengths[2]
		elif beatLen == 0.5:
			beatLen = lengths[3]
		elif beatLen == 0.25:
			beatLen = lengths[4]
		measNum = startBeat//beatsPerMeasure
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
	notes = [("ac", 2), ("b", 1), ("a", 1), 
		("r", 4), 
		("c", 4), 
		("a", 0.25), ("b", 0.25), ("c", 0.5), ("a", 0.5),  ("b", 0.5), ("r", 2)]
	out = []
	for note in notes:
		pitches = note[0]
		length = note[1]
		if pitches == "r":
			for _ in range(int(length * freq)):
				out.append([])
		else: 
			for _ in range(int(length * freq)):
				out.append([pitch for pitch in pitches])
	return out

def test():
	processNotes(makeNotes(4), 4, 60)

test()