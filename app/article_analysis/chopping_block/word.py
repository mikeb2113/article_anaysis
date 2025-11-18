class Word:
    def __init__(self,__chunk_size,__text):
        self.__chunk_size = __chunk_size
        self.__text = __text
        self.__slices = [(i,min(i+__chunk_size,len(__text)))
                         for i in range (0, len(__text),__chunk_size)]
    
    def get(self, k: int) -> str:
        s,e = self.__slices[k]
        return self.__text[s:e]

    def get_chunk_size(self):
        return self.__chunk_size
    
    def get_text(self):
        return self.__text

    def __len__(self):
        return len(self.__slices)
    
    def __iter_print__(self):
        for s, e in self.__slices:
                print(self.__text[s:e])