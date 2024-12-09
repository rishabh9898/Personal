# Your MinStack object will be instantiated and called as such:
# obj = MinStack()
# obj.push(val)
# obj.pop()
# param_3 = obj.top()
# param_4 = obj.getMin()

class MinStack:

    def __init__(self):
        self.stack = []
        self.minStack = []

    def push(self,val):
        self.stack.append(val)
        if self.minStack:
            minVal = min(val,self.minStack[-1])
            self.minStack.append(minVal)
        else:
            self.minStack.append(val)

    def pop(self):
        self.stack.pop()
        self.minStack.pop()

    def top(self):
        return self.stack[-1]

    def getMin(self):
        return self.minStack[-1]
