import SymbolTable
import InstTable
'''
사용자가 작성한 프로그램 코드를 단어별로 분할한 후, 의미를 분석하고, 최종 코드로 변환하는 과정을 총괄.
section마다 인스턴스가 하나씩 할당됨.
'''
class TokenTable:

    def __init__(self, symTab, instTab):
        self.tokenList = list()
        self.symTab = symTab
        self.instTab = instTab

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
                    리터럴이 tokenTable에 저장되어 있지 않은 경우만 tokenTable에 추가.
                    중복되는 리터럴이 추가되는것을 방지하기 위해 isOverLap 변수 사용.
                    '''
                    if not isOverLap:
                        line = "*\t" + self.getToken(i).operand+ "\t\t"
                        self.tokenList.append(Token(line))
    '''
        tokenList에서 index에 해당하는 Token을 리턴.
        :param : index
        :return : index 번호에 해당하는 코드를 분석한 Token 클래스
    '''
    def getToken(self, index):
        return self.tokenList[index]
    '''
    tokenList에서 index에 해당하는 Token의 byteSize를 지정
    :param :index
    '''
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
    '''
        tokenList에서 index에 해당하는 Token의 location 값을 지정.
        (index-1)번째의 명령어 또는 지시어에 따라 index번째의 location값이 정해짐.
        :param index
    '''
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
    '''
        tokenList에서 index에 해당하는 Token이 symbol에 해당하면 symbolTable에 넣어준다.
        :param index
    '''
    def makeSymbolTable(self, index):
        '''Token의 label이 null이거나 *(리터럴)일 경우 제외'''
        if self.tokenList[index].label != '' and self.tokenList[index].label != '*':
            self.symTab.putSymbol(self.tokenList[index].label, self.tokenList[index].location)
'''
    각 라인별로 저장된 코드를 단어 단위로 분할한 후 의미를 해석하는 데 사용되는 변수와 연산 정의.
    의미 해석이 끝나면 pass2()에서 object code로 변형되었을 때의 바이트 코드 역시 저장.
'''
class Token:
    label = str()
    operator = str()
    operand = str()
    byteSize = int()
    location = int()

    def __init__(self, line):
        self.parsing(line)
    '''
        line을 토큰별로 끊어서 저장.
        :parm line : 문장단위로 저장된 프로그램 코드.
    '''
    def parsing(self, line):
        for i in range(3):
            temp_str = line.split('\t')[i]
            if i == 0:
                self.label = temp_str
            elif i == 1:
                self.operator = temp_str
            elif i == 2:
                self.operand = temp_str
