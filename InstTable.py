'''
    모든 instruction의 정보를 관리.
    instruction data들을 저장.
'''

class InstTable:
    '''
        inst.data 파일을 불러와 저장하는 공간.
    '''
    instMap = dict()

    def __init__(self, instFile):
        self.openFile(instFile)
    '''
        입력받은 이름의 파일을 열고 해당 내용을 파싱하여 instMap에 저장.
        :param fileName : 열고자 하는 파일 이름
    '''
    def openFile(self, instFile):
        f = open(instFile, "r")
        lines = f.readlines()
        for line in lines:
            inst = Instruction(line)
            self.instMap[inst.instruction] = inst
    '''
        명령어의 이름을 보고 필요한 명령어의 정보를 찾음.
        :param Inst : 찾고자 하는 명령어의 이름
    '''
    def searchInst(self, Inst):
        return self.instMap.get(Inst)


'''
    명령어 하나하나의 구체적인 정보는 Instruction 클래스에 담김.
    instruction과 관련된 정보들을 저장하고 기초적인 연산을 수행.
'''
class Instruction:
    instruction = str()
    instFormat = str()
    opcode = str()
    numberOfOperand = int()

    '''
        클래스를 선언하며 일반문자열을 즉시 구조에 맞게 파싱.
        :parm line : instruction 명세파일로부터 한줄씩 가져운 문자열
    '''
    def __init__(self, line):
        self.parsing(line)

    '''
        일반 문자열을 파싱하여 instruction 정보를 파악하고 저장.
        :param line : instruction 명세파일로부터 한줄씩 가져온 문자열.
    '''
    def parsing(self, line):
        self.instruction = line.split('\t')[0]
        self.instFormat = line.split('\t')[1]
        self.opcode = line.split('\t')[2]
        self.numberOfOperand = line.split('\t')[3]
