class InstTable:
    instMap = dict()

    def __init__(self, instFile):
        self.openFile(instFile)

    def openFile(self, instFile):
        f = open(instFile, "r")
        lines = f.readlines()
        for line in lines:
            inst = Instruction(line)
            self.instMap[inst.instruction] = inst

    def searchInst(self, Inst):
        return self.instMap.get(Inst)

class Instruction:
    instruction = str()
    instFormat = str()
    opcode = str()
    numberOfOperand = int()

    def __init__(self, line):
        self.parsing(line)

    def parsing(self, line):
        self.instruction = line.split('\t')[0]
        self.instFormat = line.split('\t')[1]
        self.opcode = line.split('\t')[2]
        self.numberOfOperand = line.split('\t')[3]
