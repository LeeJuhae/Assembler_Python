class SymbolTable:
    symbolList = list()
    locationList = list()

    def putSymbol(self, symbol, location):
        self.symbolList.append(symbol)
        self.locationList.append(location)
