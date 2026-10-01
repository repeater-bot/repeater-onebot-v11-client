class SubCmdExit:
    def __init__(self, code: int = 0):
        self.code: int = code

    def __int__(self):
        return self.code

    def __str__(self):
        return str(self.code)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.code})"

class SubCmdBreaked(SubCmdExit):
    pass

class SubCmdCacelled(SubCmdExit):
    pass

class SubCmdTimeout(SubCmdExit):
    pass