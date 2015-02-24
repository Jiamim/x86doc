import re
import sqlite3 as sq

def shift_left(lines):
	spaceLen = 999999

	for line in lines:
		if(len(line.strip()) > 0):
			m = re.search(r'([ ]+)?.*', line)
			spaceLen = min(len(m.group(1)), spaceLen)

	for i in range(0, len(lines)):
		print lines[i]
		lines[i] = lines[i].encode('utf8', 'ignore')
		if(len(line) > 0):
			lines[i] = lines[i][spaceLen:]

	return lines


data = open("armv8_just_instructions.txt").read()

outlines = []
skip = 0

for line in data.split("\n"):
	if(skip > 0):
		skip -= 1
	elif(line.find("Copyright") > 0):
		while(len(outlines) > 0 and len(outlines[-1].strip()) == 0):
			outlines.pop()

		skip = 7
	else:
		outlines.append(line)

con = sq.connect("asm.sqlite")
con.text_factory = str
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS instructions (platform TEXT, mnem TEXT, description TEXT)")
con.commit()

instData = []
curInst = None
for line in outlines:
	if(line[0] == 'C'):
		# close
		if(curInst != None):
			insts = re.split("[, ]+", curInst)
			added = 0
			for inst in insts:
				if(inst[0] == '('):
					break
				else:
					if(added > 0):
						cur.execute("INSERT INTO instructions VALUES (?, ?, ?)", ("ARM", inst, "-R:%s" % insts[0]))
					else:
						instData = shift_left(instData)
						cur.execute("INSERT INTO instructions VALUES (?, ?, ?)", ("ARM", inst, "\n".join(instData)))
						added += 1

		# start new inst
		m = re.search(r'[C0-9\. ]+(.*)?\r', line)
		curInst = m.group(1)
		instData = []

	else:
		instData.append(line)

con.commit()
con.close()