from __future__ import print_function, division
import glob, os, os.path
import argparse

ASMDIR = "asm"
MICDIR = "mic"

def processmicro(outfname):
	for fname in glob.glob(outfname):
		with open(fname) as f:
			reqs = f.readlines()[0]
	
	microfiles = [x.strip() for x in reqs.split()[1:]]
	
	mikropro = "version4\nmikroprogramm:\n"
	comms = {}


	def mystrproc(mstr):
		retval = ""
		lstr = len(mstr)
		mstr = list(reversed(mstr))
		for i in range(0,lstr,2):
			retval += mstr[i+1] + mstr[i] + " "
		return retval
		
	
	lind = 0
	curname = ""
	for fname in (glob.glob(os.path.join(MICDIR, f))[0] for f in microfiles):
		newposs = {}
		#if fname.endswith("output.mpr"):
		#	continue
		with open(fname) as f:
			content = f.readlines()
		content = [x.strip() for x in content]
		endindex = content.index("maschinenprogramm:") if "maschinenprogramm:" in content else content.index("register:")
		content = content[content.index("mikroprogramm:")+1:endindex]
		
		for c in content:
			cs = c.split()
			
			toname = False
			
			byt = ""
			predat = ""
			
			if len(cs) >= 12:
				byt = "".join(reversed(cs[2:]))
				name = cs[1]
				curname = name
				predat += name + " "
				if name not in comms:
					curname = ""
					toname = True
			else:
				byt = "".join(reversed(cs[1:]))
			
			if curname != "":
				continue
			
			mind = int(cs[0], 16)
			if mind % 16 == 0 and lind % 16 != 0:
				lind = (lind // 16 + 1) * 16
				
			newposs[mind] = lind
			
			data = int(byt, 16)
			jpos = (data >> 6) % (1 << 12)
			data -= jpos << 6
			jpos += 0 if jpos == 0 else lind - mind
			data += jpos << 6
			
			datastr = mystrproc('{0:020x}'.format(data))
			
			#print name, byt, datastr
			
			if toname:
				comms[name] = lind
			
			mikropro += '{0:03x}'.format(lind) + " "
			mikropro += predat + datastr
			mikropro += "\n"
			lind += 1

	def cleancomments(mstr):
		return (mstr if ";" not in mstr else mstr[:mstr.find(";")]).strip()

	mikropro += "maschinenprogramm:\n0000-03ff\n"
	comc = 0
	for fname in glob.glob(outfname):
		with open(fname) as f:
			content = f.readlines()
		content = [cleancomments(x) for x in content][1:]
		
		for c in content:
			if c == "":
				continue
			if c.startswith("#"):
				cs = c.split()
				comm = cs[0][1:]
				r1 = int(cs[1],16)
				r2 = int(cs[2],16)
				mikropro += '{0:02x}{1:01x}{2:01x}'.format(comms[comm] // 16, r1, r2)
			else:
				mikropro += c
			comc += 1
			mikropro += "\n"


	mikropro += "{0:04x}*0000\n".format(int("03ff",16) - comc + 1)

	mikropro += "register:\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\n0000\nbefehlszaehler:\n0000\n000"
	
	if not os.path.exists("output"):
		os.makedirs("output")
	
	with open(os.path.join("output", os.path.splitext(os.path.basename(outfname))[0] + ".mpr"), "w") as text_file:
		text_file.write(mikropro)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Link mpr files')
	parser.add_argument('--asmdir', help='Directory of asm files', default = ASMDIR)
	parser.add_argument('--micdir', help='Directory of mpr files', default = MICDIR)
	args = parser.parse_args()
	ASMDIR = args.asmdir
	MICDIR = args.micdir
	for fname in glob.glob(os.path.join(ASMDIR, "*.asm")):
		processmicro(fname)
