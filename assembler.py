import InstTable
import SymbolTable
import TokenTable

class assembler:
    lineList = list()
    TokenList = list()
    symTabList = list()
    codeList = list()
    '''
    클래스 초기화. instruction Talbe을 초기화와 동시에 세팅한다.
    :param instFile : instruction 명세를 작성한 파일 이름.
    '''
    def __init__(self, instFile):
        self.instTable = InstTable.InstTable(instFile)
        self.loadInputFile("input.txt")

        self.pass1()
        self.printSymbolTable("symbolTable.txt")

        self.pass2()
        self.printObjectCode("output.txt")
    '''
    inputFile을 읽어들여서 lineList에 저장한다.
    :param inputFile : input 파일 이름 
    '''
    def loadInputFile(self, inputFile):
        f = open(inputFile)
        lines = f.readlines()
        for line in lines:
            self.lineList.append(line)
    '''
    pass1 과정을 수행.
    1) 프로그램 소스를 스캔하여 토큰단위로 분리한 뒤 토큰테이블 생성
    2) 프로그램 소스 각 라인에 location 값 지정
    3) label을 symbolTable에 정리
    주의사항 : SymbolTable과 TokenTable은 프로그램의 section별로 하나씩 선언되어야 한다.
    '''
    def pass1(self):
        k = -1
        for i in range(len(self.lineList)):
            label = self.lineList[i].split('\t')[0]
            if label != ".":
                operator = self.lineList[i].split('\t')[1]
                '''
                operator가 "START"이거나 "CSECT"일 때 새로운 섹션이 시작된다고 간주하여
                symTabList와 TokenList에 각각 SymbolTable과 TokenTable을 추가해준다.
                '''
                if operator == 'START' or operator == 'CSECT':
                    k += 1
                    self.symTabList.append(SymbolTable.SymbolTable())
                    self.TokenList.append(TokenTable.TokenTable(self.symTabList[k], self.instTable))
                self.TokenList[k].putToken(self.lineList[i])

        '''Token별 byteSize값 설정'''
        for i in range(len(self.TokenList)):
            for j in range(len(self.TokenList[i].tokenList)):
                self.TokenList[i].setByteSize(j)
        '''Token별 location값 설정'''
        for i in range(len(self.TokenList)):
            for j in range(len(self.TokenList[i].tokenList)):
                self.TokenList[i].assignMemory(j)
        '''Section별 symbolTable 생성'''
        for i in range(len(self.TokenList)):
            for j in range(len(self.TokenList[i].tokenList)):
                self.TokenList[i].makeSymbolTable(j)
                '''operator가 EQU일때 symbol의 location값 변경'''
                if self.TokenList[i].getToken(j).operator == "EQU":
                    if self.TokenList[i].getToken(j).operand[0] != "*":
                        tempLoc1 = self.symTabList[i].search(self.TokenList[i].getToken(j).operand.split('-')[0])
                        tempLoc2 = self.symTabList[i].search(self.TokenList[i].getToken(j).operand.split('-')[1])
                        self.symTabList[i].modifySymbol(self.TokenList[i].getToken(j).label, tempLoc1 - tempLoc2)

    '''
    작성된 SymbolTable을 출력
    :param fileName : 저장되는 파일 이름
    '''
    def printSymbolTable(self, fileName):
        f = open(fileName, 'w')
        for i in range(len(self.symTabList)):
            for j in range(len(self.symTabList[i].symbolList)):
                f.write(self.symTabList[i].symbolList[j]+"\t\t")
                f.write(str.format("%X" % (self.symTabList[i].locationList[j]))+"\n")
            f.write("\n")
        f.close()

    '''
        pass2 과정을 수행.
        1) 분석된 내용을 바탕으로 object code를 생성하여 codeList에 저장.
    '''
    def pass2(self):
        for i in range(len(self.TokenList)):
            for j in range(len(self.TokenList[i].tokenList)):
                self.TokenList[i].makeObjectCode(j)

        # codeList 생성
        for i in range(len(self.TokenList)):
            code = ""
            text = ""
            size = 0
            progLength = 0
            for j in range(len(self.TokenList[i].tokenList)):
                assem_operator = self.TokenList[i].getToken(j).operator

                # Header record
                if assem_operator == "START" or assem_operator == "CSECT":
                    for k in range(len(self.TokenList[i].tokenList)-1, -1, -1):
                        if self.TokenList[i].getToken(k).operator != "EQU":
                            if self.TokenList[i].getToken(k).operator != "RESB":
                                progLength = self.TokenList[i].getToken(k).location + self.TokenList[i].getToken(k).byteSize
                            else:
                                progLength = self.TokenList[i].getToken(k).location + int(self.TokenList[i].getToken(k).operand)
                            break
                    code = "H" + self.TokenList[i].getToken(j).label + "\t" + str.format("%06X" % self.TokenList[i].getToken(j).location)
                    code += str.format("%06X" %progLength) + "\n"
                # Define record
                elif assem_operator == "EXTDEF":
                    code += "D"
                    assem_def = str()
                    for k in range(len(self.TokenList[i].getToken(j).operand.split(','))):
                        assem_def = self.TokenList[i].getToken(j).operand.split(',')[k]
                        code += assem_def + str.format("%06X" % self.symTabList[i].search(assem_def))
                    code += "\n"
                # Refer record
                elif assem_operator == "EXTREF":
                    code += "R"
                    assem_ref = str()
                    for k in range(len(self.TokenList[i].getToken(j).operand.split(','))):
                        assem_ref = self.TokenList[i].getToken(j).operand.split(',')[k]
                        code += assem_ref
                    code += "\n"
                # Text Record
                else:
                    if len(self.TokenList[i].getToken(j).objectCode) != 0:
                        if len(text) == 0:
                            code += "T" +str.format("%06X" % self.TokenList[i].getToken(j).location)
                        text += self.TokenList[i].getToken(j).objectCode
                        size += self.TokenList[i].getToken(j).byteSize
                        if j == (len(self.TokenList[i].tokenList)-1):
                            code += str.format("%02X" % size) + text + "\n"
                        elif (size + self.TokenList[i].getToken(j + 1).byteSize >= 30) or ((len(self.TokenList[i].getToken(j + 1).objectCode) == 0) and self.TokenList[i].getToken(
                                j + 1).operator != "END"):
                            code += str.format("%02X" % size) + text + "\n"
                            text = ""
                            size = 0
                    if j == (len(self.TokenList[i].tokenList)-1):
                        # Modification record
                        for k in range(len(self.TokenList[i].tokenList)):
                            if self.TokenList[i].getToken(k).operator[0] == "+":
                                code += "M" + str.format("%06X" % (self.TokenList[i].getToken(k).location + 1))
                                code += "05+" + self.TokenList[i].getToken(k).operand.split(',')[0] + "\n"
                            elif self.TokenList[i].getToken(k).operator == "WORD":
                                for m in range(len(self.TokenList[i].getToken(k).operand.split('-'))):
                                    temp_str = self.TokenList[i].getToken(k).operand.split('-')[m]
                                    if m == 0 :
                                        code += "M" + str.format("%06X" % self.TokenList[i].getToken(k).location) + "06+" + temp_str+"\n"
                                    elif m == 1:
                                        code += "M" + str.format(
                                            "%06X" % self.TokenList[i].getToken(k).location) + "06-" + temp_str + "\n"
                        #End record
                        code += "E"
                        if i == 0:
                            code += str.format("%06X" % self.TokenList[0].getToken(0).location)
                        code += "\n\n"
                        self.codeList.append(code)
    '''
        작성된 codeList를 출력형태에 맞게 출력.
        :param fileName : 저장되는 파일 이름
    '''
    def printObjectCode(self, fileName):
        f = open(fileName, 'w')
        for i in range(len(self.TokenList)):
            f.write(self.codeList[i])
        f.close()


a = assembler("inst.data")