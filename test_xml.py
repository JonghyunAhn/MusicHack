from musicXML_bindings import *

r = Rest('quarter', True)
n = Note('G', 5, 'quarter', True, 'sharp')
n2 = Note('A', 6, 'quarter', True, 'flat')
n3 = Note('F', 4, 'quarter')

c = Chord()
c.add_note(n)
c.add_note(n2)

m = Measure()
m.add_element(c)
m.add_element(r)

m2 = Measure()
m2.add_element(n3)

s = Score('hello_world', 4, 4)
s.add_measure(m)
s.add_measure(m2)

s.write_to_file()
