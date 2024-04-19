class Solution:
    def isAnagram(self, s: str, t: str) -> bool:

        if len(s)!=len(t):
            return False 
        
        # constant memory space 0(n)
        dict = {}

        # run time O(n)
        for i in range(len(s)):
            if s[i] in dict:
                dict[s[i]]+=1
            else:
                dict[s[i]] = 1
        
        # run time o(n)
        for j in range(len(t)):
            if t[j] in dict:
                dict[t[j]]-=1
            else:
                return False

        # run time o(n)
        for p,q in dict.items():
            if q!=0:
                return False
        return True


