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
numToBeat[3.25] = "dhalf"
numToBeat[2.75] = "dhalf"
numToBeat[2.5] = "dhalf"
numToBeat[2.25] = "half"
numToBeat[1.75] = "half"
numToBeat[1.25] = "quarter"
##Jong calls this. Passes in array of arrays of notes, sample rate, and tempo
## Tempo (bpm)
def processNotes(notes = [], sampleRate = 44100.0, tempo = 72):

	notes = filterNoise(notes)
	deltaT = 1.0/(sampleRate/512.0)
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
	allNotes.append([]) #hacky solution to detect last note hit.
	currentNotes = {} #pitch : [startTime, lastSeen]
	out = []
	time = 0
	i = 0
	while allNotes[i] == []: # cut off empty time in front
		i+= 1
	while i < len(allNotes):
		notes = allNotes[i]
		i+=1
		prevNotes = set(list(currentNotes.keys())) 
		# Update notes in this timestamp
		for note in notes: 
			if note not in currentNotes: # note is starting here
				currentNotes[note] = [time, 0]
			else:
				currentNotes[note][1] = 0

		# Find notes that end in this timestamp and track in Out
		toPop = []
		for note in currentNotes:
			currentNotes[note][1] += 1
			if currentNotes[note][1] > 3: #Note ends here
				if  (time - currentNotes[note][0]) > 0.15: #real note
					out.append((note, currentNotes[note][0], time))
				toPop.append(note)
		for note in toPop:
			currentNotes.pop(note)
		time += deltaT
	for note in currentNotes:
		out.append((note, currentNotes[note][0], time))
	# for note in out:
	# 	print note

	# print "================================"
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
		startBeat = approxBeatNum8(note[1], beatLength)
		endBeat = approxBeatNum8(note[2], beatLength)
		measNum = startBeat//beatsPerMeasure
		beatLen = endBeat - startBeat
		if endBeat > (measNum + 1) * 4:
			beatLen = (measNum + 1) * 4 - startBeat
		# print note
		# print "\t beatLen: ", beatLen
		# print "\t beatLength", beatLength
		# print "\t startBeat", startBeat
		# print "\t endBeat", endBeat
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

	for meas in beats:
		print meas, beats[meas]
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
				if currBeat < beat: # Fill space with note or rest
					lastElem = thisMeasure.get_last()
					print lastElem, type(lastElem)
					if lastElem != None and isinstance(lastElem, Note):
						print "attempted extend"

						#extend note to now, if possible
						newLen = beat - currBeat + dottedLengthToNum(lastElem.note_length, lastElem.dot_string != "")
						if newLen in beatToNum.values():
							newLenStr, newLenDotted = convDot(numToBeat[newLen], 4)
							lastElem.note_length = newLenStr
							lastElem.set_dot(newLenDotted)
						else: 
							fillInRest(thisMeasure, beat-currBeat)
					else:
						fillInRest(thisMeasure, beat - currBeat)
					currBeat = beat

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
							pitch, octave, sharp = convPitch(note[0])
							c.add_note(Note(pitch, octave, chordLen, dotted, sharp))
						thisMeasure.add_element(c)
						currBeat += min(beatToNum[chordLen], lenMax)

					elif len(notes) == 1: # Make note
						if (beatToNum[notes[0][1]] + currBeat) > 4: #rest of note overflows into next measure
							overflowLen = (beatToNum[notes[0][1]] + currBeat) - 4
							addOverflow(notes, numToBeat[overflowLen], beats, measNum + 1)
							trailingMeasures = True
						noteLen, dotted = convDot(notes[0][1], lenMax)
						pitch, octave, sharp = convPitch(notes[0][0])
						thisMeasure.add_element(Note(pitch, octave, noteLen, dotted, sharp))
						currBeat += min(beatToNum[notes[0][1]], lenMax)
					else: 
						print "Something went wrong in dataToNotes.py, beatsToXML."
			if currBeat < 4: # fill rest of measure with note or rest
				lastElem = thisMeasure.get_last()
				print lastElem, type(lastElem)
				if lastElem != None and isinstance(lastElem, Note):
					print "attempted extend"
					#extend note to now, if possible
					newLen = 4 - currBeat + dottedLengthToNum(lastElem.note_length, lastElem.dot_string != "")
					if newLen in beatToNum.values():
						newLenStr, newLenDotted = convDot(numToBeat[newLen], 4)
						lastElem.note_length = newLenStr
						lastElem.set_dot(newLenDotted)
					else: 
						fillInRest(thisMeasure, beat-currBeat)
				else:
					fillInRest(thisMeasure, beat - currBeat)
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
		return pitch[0], int(pitch[1]), ""
	return pitch[0:1], int(pitch[2]), "sharp"

def dottedLengthToNum(note_length, isDotted):
	l = beatToNum[note_length]
	if isDotted:
		return l * 1.5
	return l
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