import InstTable
import SymbolTable
import TokenTable

class assembler:
   # instTable = InstTable()
    lineList = list()
    TokenList = list()
    symTabList = list()
    '''
    클래스 초기화. instruction Talbe을 초기화와 동시에 세팅한다.
    :param instFile : instruction 명세를 작성한 파일 이름.
    '''
    def __init__(self, instFile):
        self.instTable = InstTable.InstTable(instFile)
        self.loadInputFile("input.txt")

        self.pass1()
        #self.test()
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
    pass1 과정을 수행한다.
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
                    self.symTabList.append(SymbolTable.SymbolTable)
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

    def test(self):
        for i in range(len(self.TokenList)):
            for j in range(len(self.TokenList[i].tokenList)):
                print(self.TokenList[i].getToken(j).operator)



a = assembler("inst.data")