class article:
    #get the string contents of an article, length will be tied to it
    #For later comparisons, use the average of two lengths
    def __init__(self,string=""):
        self.__contents = string
        self.__length = string.len()

    def get_contents(self):
        return self.__contents

    def get_length(self):
        return self.__length    