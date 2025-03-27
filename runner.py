import run_i as VirtueBar
import os
import time
import sys
os.system('cls')

if len(sys.argv) > 1:
	pTime = time.time()
	path = sys.argv[1]
	file = path
	ext = file[-4:]
	#print(ext)
	if path == '' or path == ' ':
		raise RuntimeError('No filename was specified')
	elif ext == 'virh' or ext == 'virb':

		ospath = os.path.abspath(file)
		fullpath = ospath.replace("\\", "/")
		command = f'run("{fullpath}")'

		if ext == 'virh': header = True 
		else: header = False
		
		try:
			with open(fullpath, "r") as file:
				script = file.read()
		except Exception as e:
				print(f"Failed to load script \"{fullpath}\"\n" + str(e))
				sys.exit(1)
		#print(command)
		result, error = VirtueBar.run(f'{file}', script, path=True, header=header)
		if error: print(error.as_string())
		elif result:
			if len(result.elements) == 1:
				if result.elements[0] != None:
					if str(repr(result.elements[0])) != None: print(result.elements[0])
			else:
					
				for i in result.elements:
					try:
							
						if i.value != None:
							#print(3777, i.value, type(i.value), None, type(None))
							#print(repr(i))
							pass
							#print(result, result.elements)
					except AttributeError:
						pass
		elif result == None:
			pass
		
	else: raise RuntimeError('Invalid file extension was given')
		
	cTime = time.time()
	TimeTaken = cTime - pTime
	TimeTaken = ("%.3f" %TimeTaken)
	print(f"Executed within {TimeTaken}")