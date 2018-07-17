'''
symbol과 관련된 데이터와 연산을 소유
section별로 하나씩 인스턴스를 할당
'''
class SymbolTable:

    def __init__(self):
        self.symbolList=[]
        self.locationList=[]
    '''
        새로운 symbol을 table에 추가
        :param symbol : 새로 추가되는 symbol의 label
        :param location : 해당 symbol이 가지는 주소값
    '''
    def putSymbol(self, symbol, location):
        self.symbolList.append(symbol)
        self.locationList.append(location)
    '''
        기존에 존재하는 symbol 값에 대해서 가리키는 주소값을 변경
        :param symbol : 변경을 원하는 symbol 의 label
        :param location : 새로 바꾸고자 하는 주소값
    '''
    def modifySymbol(self, symbol, newlocation):
        for i in range(len(self.symbolList)):
            if self.symbolList[i] == symbol:
                self.locationList[i] = newlocation
                break
    '''
        인자로 전달된 symbol의 주소 검색
        :param symbol : 검색을 원하는 symbol 의 label
        :param location : symbol 이 가지고 있는 주소값. 해당 symbol이 없을 경우 -1 리턴
    '''
    def search(self, symbol):
        address = -1
        for i in range(len(self.symbolList)):
            if self.symbolList[i] == symbol:
                address = self.locationList[i]
                break
        return address