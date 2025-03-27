import run_i as VirtueBar
import os
import time
os.system('cls')
print('==========================================')
print('        VirtueBar Shell V1.1.0            ')
print('      Release Version: 01/04/2023         ')
from values_i import Runtime
if Runtime.developement_mode == True:
    print("  Warning: Developement Mode is active    ")
print('==========================================')
while True:
    text = input('ON>> ')
    if text == 'LOUT': 
        exit()

    elif text == '' or text == ' ': 
        pTime = time.time()
        result, error = VirtueBar.run('<stdin.filename>', text)
        cTime = time.time()
        TimeTaken = cTime - pTime
    else:
        pTime = time.time()
        result, error = VirtueBar.run('<stdin.filename>', text)
        cTime = time.time()
        TimeTaken = cTime - pTime
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
                            print(repr(i))
                    except AttributeError:
                        pass
        elif result == None:
            pass

    TimeTaken = ("%.3f" %TimeTaken)
    print(f"Executed within {TimeTaken}")