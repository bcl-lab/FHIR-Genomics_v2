__author__ = 'HemingY'

f = file("/Users/apple/Documents/FHIR-Genomics-2/fhir/examples/loinc-code.txt")
f2 = file("/Users/apple/Documents/FHIR-Genomics-2/fhir/examples/loinc-code2.txt", 'w')
line = f.readline()
print len(line)
for i in range (0, len(line)):
    if line[i] == '\r':
        line = line[0:i] + '\n' + line[i+1:]
f2.write(line)
