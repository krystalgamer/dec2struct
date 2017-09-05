from idaapi import *

vtable = lambda x: x + 'Vtable'

def CreateStruct(name):

    if GetStrucIdByName(name) != -1:
        print('Struct ' + name + ' already exists..Deleting it')
        DelStruc(GetStrucIdByName(name))
    sid = AddStruc(-1, name)  
    if sid == -1:
        print('Error creating struct ' + name)
        return None
    print(name + ' created! ')
    return sid

def main():
    filePath = AskFile(0, '*.cpp;*.h', 'Class File')
    
    if filePath is None:
        print('No filename specified, quitting..')
        return

    foundClass = False
    commentMode = False

    with open(filePath) as stream:
        for line in stream:
            if foundClass is False:
                if 'class' not in line:
                    continue
                className = line.split('class ')[-1].split()[0]
               
                sid = CreateStruct(vtable(className))
                if sid == None:
                    return
                foundClass = True
                continue
            #Ignore empty lines
            if len(line.split()) == 0:
                continue
 
            if commentMode:
                if line.split()[0].endswith('*/'):
                    commentMode = False
                continue
            if line.split()[0].startswith('/*'):
                commentMode = True
           
            #End of the class, time to setup the struct
            if '};' in line:
                nsid = CreateStruct(className)
                if nsid == None:
                    return

                AddStrucMember(nsid, 'vtable', 0, FF_DATA|FF_DWRD, -1, 4)
                SetType(GetMemberId(nsid, 0), vtable(className) + '** vtable')
                className = None
                cid = None
                foundClass = False
                continue

            #Ignore comments
            if line.split()[0].startswith('//'):
                continue
            #This shouldn't be triggered lmao
            if ';' not in line:
                continue

            funcName = GetFunctionName(line)
            if funcName is None:
                continue
            
            #Time to add the func
            if AddStrucMember(sid, funcName, -1, FF_DWRD|FF_DATA, -1, 4) != 0:
                print('Error adding ' + funcName)
                return

            print('Added ' + funcName)


def GetFunctionName(funcLine):
    func = funcLine.split('(')
    if len(func) != 2:
        for i in range(len(func)-1):
            result = AskYN(0, 'Couldnt get the correct function, help me to find it:\nIs ' + func[i].split()[-1] + ' the function?')
            if result == 1:
                return func[i].split()[-1]

        return None #Default
    return func[0].split()[-1].replace('*', '')

if __name__ == '__main__':
    main()
