class DebugTab:
    def __init__(self): self.lines=[]
    def log(self,msg,level='info'): self.lines.append((level,msg))
