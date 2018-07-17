import SymbolTable
import InstTable
'''
사용자가 작성한 프로그램 코드를 단어별로 분할한 후, 의미를 분석하고, 최종 코드로 변환하는 과정을 총괄.
section마다 인스턴스가 하나씩 할당됨.
'''
class TokenTable:
    nFlag = 32
    iFlag = 16
    xFlag = 8
    bFlag = 4
    pFlag = 2
    eFlag = 1

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
        if self.getToken(index).label != '' and self.getToken(index).label != '*':
            self.symTab.putSymbol(self.getToken(index).label, self.getToken(index).location)
    '''
        인자로 전달된 literal의 주소를 반환.
        :param literal : 검색을 원하는 Token의 operand
        :return 리터럴의 주소. 해당 literal이 없을 경우 -1
    '''
    def searchLiteral(self, literal):
        address = -1
        for i in range(len(self.tokenList)):
            if self.getToken(i).operator == literal :
                address = self.getToken(i).location
                break
        return address
    '''
        pass2 과정에서 사용됨.
        instruction table, symbol table 등을 참조하여 objectCode를 생성하고 이를 저장.
        :param index
    '''
    def makeObjectCode(self, index):
        obcode = 0
        str_format = str()
        str_opcode = str()

        str_operand = list()
        str_inst = self.getToken(index).operator
        for i in range(len(self.getToken(index).operand.split(','))):
            str_operand.append(self.getToken(index).operand.split(',')[i])
        if self.getToken(index).operator in self.instTab.instMap or self.getToken(index).operator[0] == "+":
            if self.getToken(index).operator[0] == "+":
                str_inst = str_inst[1:]
                str_format = "4"
            else:
                str_format = self.instTab.searchInst(str_inst).instFormat[0]
            str_opcode = self.instTab.searchInst(str_inst).opcode
            # 명령어의 opcode를 int형으로 변환, shift 연산 후 obcode에 반영해줌.
            for i in range(2):
                obcode |= (int(str_opcode[i], 16) << ((self.getToken(index).byteSize * 2) - (i + 1)) * 4)
            # 3, 4형식 일 때, n, i, x, b, p, e값 설정
            if str_format == "3" or str_format == "4":
                ta = int() # target 값
                pc = int() # 다음 Token의 location 값
                # n, i 설정
                if str_inst == "RSUB":
                    self.getToken(index).setFlag(self.nFlag, 1)
                    self.getToken(index).setFlag(self.iFlag, 1)
                elif str_operand[0][0] == "#":
                    self.getToken(index).setFlag(self.nFlag, 0)
                    self.getToken(index).setFlag(self.iFlag, 1)
                elif str_operand[0][0] == "@":
                    self.getToken(index).setFlag(self.nFlag, 1)
                    self.getToken(index).setFlag(self.iFlag, 0)
                else:
                    self.getToken(index).setFlag(self.nFlag, 1)
                    self.getToken(index).setFlag(self.iFlag, 1)
                # x 설정
                if str_operand[0] != '':
                    for i in range(len(str_operand)):
                        if str_operand[i] == "X":
                            self.getToken(index).setFlag(self.xFlag, 1)
                        else:
                            self.getToken(index).setFlag(self.xFlag, 0)
                else: # input.txt 에서는 RSUB 경우만 해당됨.
                    self.getToken(index).setFlag(self.xFlag, 0)

                # b, p 설정
                if self.getToken(index).operator[0] == "+" or str_inst == "RSUB":
                    self.getToken(index).setFlag(self.bFlag, 0)
                    self.getToken(index).setFlag(self.pFlag, 0)
                else:
                    if str_operand[0][0] != "#":
                        if str_operand[0][0] == "@":
                            str_operand[0] = str_operand[0][1:]
                        if str_operand[0][0] != "=":
                            ta = self.symTab.search(str_operand[0])
                        else:
                            ta = self.searchLiteral(str_operand[0])
                        pc = self.getToken(index + 1).location
                        if -2048 <= (ta - pc) <= 2047:
                            self.getToken(index).setFlag(self.bFlag, 0)
                            self.getToken(index).setFlag(self.pFlag, 1)
                        else:
                            self.getToken(index).setFlag(self.bFlag, 1)
                            self.getToken(index).setFlag(self.pFlag, 0)
                    else:
                        self.getToken(index).setFlag(self.bFlag, 0)
                        self.getToken(index).setFlag(self.pFlag, 0)

                # e 설정
                if self.getToken(index).operator[0] == "+":
                    self.getToken(index).setFlag(self.eFlag, 1)
                else:
                    self.getToken(index).setFlag(self.eFlag, 0)

                obcode |= self.getToken(index).nixbpe << ((self.getToken(index).byteSize * 2 -3) * 4)

                # disp 설정
                if str_format == "4":
                    obcode |= 0
                else:
                    if self.getToken(index).getFlag(self.pFlag) == 2:
                        if ta >= pc:
                            obcode |= ta - pc
                        else:
                            obcode |= ((ta - pc) & 0x0000FFF)
                    else:
                        if str_operand[0] != '':
                            obcode |= int(str_operand[0][1:])
                self.getToken(index).objectCode = str.format("%06X" % obcode)
            # 2형식 일때 레지스터 값 설정
            else:
                temp_var = int()
                for i in range(len(str_operand)):
                    if str_operand[i] == "A":
                        temp_var |= 0
                    elif str_operand[i] == "X":
                        temp_var |= 1
                    elif str_operand[i] == "L":
                        temp_var |= 2
                    elif str_operand[i] == "B":
                        temp_var |= 3
                    elif str_operand[i] == "S":
                        temp_var |= 4
                    elif str_operand[i] == "T":
                        temp_var |= 5
                    elif str_operand[i] == "F":
                        temp_var |= 6
                    elif str_operand[i] == "PC":
                        temp_var |= 8
                    elif str_operand[i] == "SW":
                        temp_var |= 9
                    if i == 0:
                        temp_var = temp_var << 4
                obcode |= temp_var
                self.getToken(index).objectCode = str.format("%04X" % obcode)
        # 명령어 아닐때
        else:
            if str_inst == "BYTE":
                self.getToken(index).objectCode = str_operand[0][2:len(str_operand[0])-1]
            elif str_inst == "WORD":
                a = self.symTab.search(str_operand[0].split('-')[0])
                b = self.symTab.search(str_operand[0].split('-')[1])
                if a == -1 and b == -1:
                    self.getToken(index).objectCode = str.format("%06X" % obcode)
                elif a!= -1 and b != -1:
                    self.getToken(index).objectCode = str.format("%06X" % (a - b))
            elif str_inst[0] == "=":
                if str_inst[1] == "X":
                    self.getToken(index).objectCode = str_inst[3:len(str_operand[0]) - 1]
                elif str_inst[1] == "C":
                    temp_str = str_inst[3:len(str_operand[0]) - 1]
                    for i in range(len(temp_str)):
                        self.getToken(index).objectCode += str.format("%02X" % ord(temp_str[i]))


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

    objectCode = ""
    nixbpe = int()

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

    '''
        n,i,x,b,p,e flag를 설정.
        :param flag : 원하는 비트 위치
        :param value : 집어넣고자 하는 값. 1 또는 0  
    '''
    def setFlag(self, flag, value):
        if value == 1:
            self.nixbpe |= flag

    '''
        원하는 flag들의 값을 반환.
        :param flags : 값을 확인하고자 하는 비트 위치
        :return : 비트위치에 들어있는 값.
        플래그별로 각각 32, 16, 8, 4, 2, 1의 값을 리턴할 것임.
    '''
    def getFlag(self, flags):
        return self.nixbpe & flags