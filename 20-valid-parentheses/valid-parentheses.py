class Solution:
    def isValid(self, s: str) -> bool:

        if len(s)<2:
            return False

        stack = []

        close = {")":"(","}":"{","]":"[" }

        for i in s:
            if i in close:
                if len(stack)>0 and stack[-1] == close[i]:
                    stack.pop()
                else:
                    return False
            else:
                stack.append(i)

        if len(stack) == 0:
            return True
        return False

