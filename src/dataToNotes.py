

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
	# Do one pass to approximate start and ending beat for each note.
	for _ in range(len(startEndTimes)):


def filterNoise(notes):
	return notes

def makeNotes(freq):
	notes = [("ac", 2), ("b", 1), ("a", 1), ("r", 4), ("c", 4)]
	out = []
	for note in notes:
		pitches = note[0]
		length = note[1]
		if pitches == "r":
			for _ in range(length) * freq:
				out.append([])
		else: 
			for _ in range(length) * freq:
				out.append([pitch for pitch in pitches])
	return out

def test():
	processNotes(makeNotes(2), 2, 60)

test()