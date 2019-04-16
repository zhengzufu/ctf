#!/usr/bin/python3

import os, re
import subprocess

START_DIR = '.'
SEQ_DIR = 'seq'

class Node:
    def __init__(self, n, ntype, addr, delr, files):
        
        self.children = []
        
        if ntype == 'ADD':
            
            self.item = addr.pop(n)
            files += self.item[2]
            
            # find next DEL revs... 
            for i in range(len(delr)):
                del_allowed = True
                for f in delr[i][2]:
                    if f in files:
                        continue
                    else:
                        del_allowed = False
                        break
                
                if del_allowed:
                    self.children.append(Node(i, 'DEL', addr.copy(), delr.copy(), files.copy()))
        
        else:
            
            self.item = delr.pop(n)
            for f in self.item[2]:
                files.pop(files.index(f))
            
            # find next ADD revs... 
            for i in range(len(addr)):
                add_allowed = True
                for f in addr[i][2]:
                    if f not in files:
                        continue
                    else:
                        add_allowed = False
                        break
                
                if add_allowed:
                    self.children.append(Node(i, 'ADD', addr.copy(), delr.copy(), files.copy()))
        
        self.ntype = ntype
        self.addr = addr    
        self.delr = delr
        self.files = files
    
    def __str__(self):
        return self.item[0]

def find_max_depth(depth, node, seq):
    seq.append(str(node))
    for child in node.children:
        find_max_depth(depth+1, child, seq.copy())
    if depth == 20:
        max_seq.append(seq)
        print('Max tree depth reached. Found valid sequence of revisions.')

dir_names = [\
'7b0eb1f95d1048a6a4a046347f7421f52802620b110a9e9acdb147ff4460fe91', 
'1b6a1a7688499919f36a54e86eb9ea1ecb6c2ca8e6b5f67d019b1b154efe6426', 
'9529d8b28ec530e57deb78622b48f93a7a8503d9d8f9bafbb3a48a45902ba571', 
'24ae8db0a8d56c1fbdaa5a899fe7bd40ff0620043862c1831bcd4c7dc4ac2efc', 
'f86dad3cffca8d6564a21e48efb922457de335bb27f66785435ba6e9655ee126', 
'811fc921019e7fc4f116cbc517a960e6db36bdcbff05a0d852cdd172e8372958', 
'4eceda2102c39bb05684f5d3bad4678e22278f7563d628fafe65d84b76138b52', 
'b9fb9364b2141b829d6d6704e96fd8c47e5ad7b020bace604ea6323cba51b826', 
'b8c582c7134c751e165e9ff16053b94a09ff27e307dd11dd3187b8e1dd77548a', 
'62dddd2eb47ea0f3c7612b4c561472d115387dda5e7db5ad97890f233c42134d',
'2d98c6317f633c11f9769887838fb9aa00c2d9bf1151b855eb2c2446154c370a', 
'c7a52a7eb57d97ad8f20c5b6e7b5fed15bed2fbf852b0fd371d8bc55113f7c83', 
'161eeac1208eeb8bce94cd9fd13d6e63118561cbb9a9dffad3f27a3052f18891', 
'de79454a442570a1423e6a0b7ef45dea1d65d922526806a523558b83df3bc443', 
'8bd6aff2fcf00277602e6bafb6ccf4ef9b9378e5945721ce6b765ec299d3dca6', 
'4885415ba7b00e3e8887cc8f6956204de6be52f72f4450edf62d17c79fa1e05e', 
'e1a379dd4d1d64a73da7bb3a66245f7c57efaa9dd688eeeab93c3e63bab53b5b', 
'2bfdca8e66f19cfc868315c5457851e42f2d24042a40136a524e29fe9f48241f', 
'5fb2808ba584da714d978c7c84cd758a3a0241ecb717f8c11627e11587baecdb',
'8dc7fe009a66df10e7842dbca56d7ca80e53d4a21786f3f6e59681591f81be92',
'276d86e23c70b8e7bab08e8fcff694e91c3f932bd66773382d9959e90a2d5aac', 
]

max_seq = []
add_rev = []
del_rev = []
nodes = []

print('Loading revisions ...')
for i in range(len(dir_names)):
    
    f = os.path.join(START_DIR, dir_names[i], 'layer.tar')
    out = subprocess.check_output(['tar', '-tf', f]).decode('utf-8')

    if '.wh.' in out:
        del_rev.append((dir_names[i], 'DEL', sorted([int(re.sub('\D', '', line)) for line in out.split('\n')[1:-1]])))
        print('Added revision: {}'.format(del_rev[-1]))
    else:
        add_rev.append((dir_names[i], 'ADD', sorted([int(re.sub('\D', '', line)) for line in out.split('\n')[1:-1]])))
        print('Added revision: {}'.format(add_rev[-1]))

print('\nGenerating revision sequence node trees ...')
for i in range(len(add_rev)):
    print('Loading node tree with starting \'ADD\' revision: {}'.format(add_rev[i][0]))
    nodes.append(Node(i, 'ADD', add_rev.copy(), del_rev.copy(), []))

print('\nSearching node trees ...')
for node in nodes:
    find_max_depth(0, node, [])

# create separate directory for extracting sequences
if not os.path.exists(SEQ_DIR):
    os.makedirs(SEQ_DIR)

# extract /root/flag.sh
f = os.path.join(START_DIR, '24d12bbeb0a9fd321a8decc0c544f84bf1f6fc2fd69fa043602e012e3ee6558b', 'layer.tar')
subprocess.check_output(['tar', '-C', SEQ_DIR, '-xvf', f, 'root/flag.sh']).decode('utf-8')

# extract based on valid sequences and output resulting flag
print('\nProcessing valid sequences ...')
for i in range(len(max_seq)):
    
    print('Extracting sequence #{:>02} : '.format(i), end='')
    d = os.path.join(SEQ_DIR, str(i))
    if not os.path.exists(d):
        os.makedirs(d)
    
    for j in range(len(max_seq[i])):
        f = os.path.join(START_DIR, max_seq[i][j], 'layer.tar')
        subprocess.check_output(['tar', '-C', d, '-xvf', f]).decode('utf-8')
    
    os.chdir(os.path.join(d, 'root'))
    out = subprocess.check_output(['../../root/flag.sh']).decode('utf-8')
    print(out.strip())
    os.chdir('../../..')

print()
