class demo:
    def __init__(self):
        pass
    def def1(self):
        name=1
        print(name)
        return name
    def def2(self):
        print(self.def1())

if __name__=="__main__":
    c=demo()
    c.def2()