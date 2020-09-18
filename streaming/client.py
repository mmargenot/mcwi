import time

import requests

r = requests.post('http://localhost:5000/generate-samples', stream=True)

samples = [] 
 
previous_right = None 
 
left = None 
right = None 
 
for chunk in r.iter_content(9): 
    chunk = str(chunk) 
    chunk = chunk.replace("b", '') 
    chunk = chunk.replace("'", '') 
     
    print("CHUNK IS:", chunk) 
     
    data = str(chunk).split(',') 
     
    if len(data) > 1: 
        left, right = data 
 
        print('left is:', left)     
        print('right is:', right) 
 
        if previous_right is not None: 
            left = previous_right + left 
            print("left is now:", left) 
            samples.append(left) 
 
        previous_right = right 
    else: 
        previous_right = None 
     
    print('') 
    time.sleep(1)
