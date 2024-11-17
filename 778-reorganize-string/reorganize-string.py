class Solution:
    def reorganizeString(self, s: str) -> str:

        dict = {}

        for i in s:
            if i in dict:
                dict[i]+=1
            else:
                dict[i] = 1
        
        maxHeap = [[-cnt,char] for char,cnt in dict.items()]

        heapq.heapify(maxHeap)

        prev = None
        res = ""

        while maxHeap or prev:

            if prev and not maxHeap:
                return ""
            cnt,char = heapq.heappop(maxHeap)
            res+=char
            cnt+=1

            if prev:
                heapq.heappush(maxHeap,prev)
                prev = None

            if cnt!=0:
                prev = [cnt,char]
        return res
        
        


        