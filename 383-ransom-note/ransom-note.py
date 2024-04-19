class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        dict = {}

        n = len(ransomNote)

        for i in range(len(magazine)):
            if magazine[i] in dict:
                dict[magazine[i]]+=1
            else:
                dict[magazine[i]] = 1

        for i in range(len(ransomNote)):
            if ransomNote[i] in dict and dict[ransomNote[i]]>0:
                dict[ransomNote[i]]-=1
                n-=1
            else:
                return False
        
        if n==0:
            return True