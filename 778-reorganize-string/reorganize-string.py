class Solution:
    def reorganizeString(self, s: str) -> str:

        dict = {}
        res = ""

        for i in s:
            if i in dict:
                dict[i]+=1
            else:
                dict[i]=1
               
        #  Stored the frequency

        maxHeap = []

        for char,cnt in dict.items():
            maxHeap.append([-1*cnt,char])
        
        heapq.heapify(maxHeap)
        prev = None

        while maxHeap or prev:
            if prev and not maxHeap:
                return ""
            cnt,char = heapq.heappop(maxHeap)
            res+=char
            cnt+=1
            if prev:
                heapq.heappush(maxHeap, prev)
                prev = None

            if cnt!=0:
                prev = [cnt,char]

        return res
            






            


        


        