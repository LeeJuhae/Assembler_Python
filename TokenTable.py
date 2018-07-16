import SymbolTable
import InstTable
class TokenTable:


    def __init__(self, symTab, instTab):
        self.tokenList = list()
        self.symTab = symTab()  # ################
        self.instTab = instTab  # ################

    def putToken(self, line):
        isOverLap = False
        self.tokenList.append(Token(line))
        '''리터럴 처리'''
        tempOpt = self.getToken(len(self.tokenList)-1).operator
        if tempOpt == "LTORG" or tempOpt == "CSECT" or tempOpt == "END":
            for i in range(len(self.tokenList)):
                if self.getToken(i).operand[0:1] == "=":
                    for j in range(len(self.tokenList)):
                        if self.getToken(i).operand == self.getToken(j).operator:
                            isOverLap = True
                            break
                    '''
                    리터럴이 tokenTable에 저장되어 있지 않은 경우만 tokenTable에 추가해준다.
                    중복되는 리터럴이 추가되는것을 방지하기 위해 isOverLap 변수 사용
                    '''
                    if not isOverLap:
                        line = "*\t" + self.getToken(i).operand+ "\t\t"
                        self.tokenList.append(Token(line))

    def getToken(self, index):
        return self.tokenList[index]

    def setByteSize(self, index):
        if self.getToken(index).operator == "BYTE":
            if self.getToken(index).operand[0] == "C":
                self.getToken(index).byteSize = (len(self.getToken(index).operand)-4) * 2
            elif self.getToken(index).operand[0] == "X":
                self.getToken(index).byteSize = int((len(self.getToken(index).operand)-3) / 2)
        elif self.getToken(index).operator == "WORD":
            self.getToken(index).byteSize = 3
        # 리터럴 일때
        elif self.getToken(index).operator[0] == "=":
            if self.getToken(index).operator[1] == 'C':
                self.getToken(index).byteSize = len(self.getToken(index).operator) - 4
            elif self.getToken(index).operator[1] == 'X':
                self.getToken(index).byteSize = int((len(self.getToken(index).operator) - 4) / 2)
        else:
            # 1, 2, 3형식 명령어 일때
            if self.getToken(index).operator in self.instTab.instMap:
                format = int(self.instTab.searchInst(self.getToken(index).operator).instFormat[0])
                self.getToken(index).byteSize = format
            # 4형식 명령어 일때
            elif self.getToken(index).operator[0] == '+':
                self.getToken(index).byteSize = 4

    def assignMemory(self, index):
        if self.getToken(index).operator != "EXTDEF" or self.getToken(index).operator != "EXTREF":
            if index == 0:
                location = 0
            else:
                if self.getToken(index - 1).operator == "RESW":
                    location = self.getToken(index - 1).location + int(self.getToken(index - 1).operand) * 3
                elif self.getToken(index - 1).operator == "RESB":
                    location = self.getToken(index - 1).location + int(self.getToken(index - 1).operand)
                elif self.getToken(index - 1).operator == "LTORG" or self.getToken(index - 1).operator == "END":
                    location = self.getToken(index - 1).location
                else:
                    location = self.getToken(index - 1).location + self.getToken(index - 1).byteSize
            self.getToken(index).location = location

    def makeSymbolTable(self, index):
        '''Token의 label이 null이거나 *(리터럴)일 경우 제외'''
        if self.tokenList[index].label != '' and self.tokenList[index].label != '*':
           # print(len(self.symTab.symbolList))
            for i in range(len(self.symTab.symbolList)):
                if i == len(self.symTab.symbolList)-1:
                    print(self.symTab.symbolList[i])
            self.symTab.putSymbol(self.tokenList[index].label, self.tokenList[index].location)


class Token:
    label = str()
    operator = str()
    operand = str()
    byteSize = int()
    location = int()

    def __init__(self, line):
        self.parsing(line)

    def parsing(self, line):
        for i in range(3):
            temp_str = line.split('\t')[i]
            if i == 0:
                self.label = temp_str
            elif i == 1:
                self.operator = temp_str
            elif i == 2:
                self.operand = temp_str
