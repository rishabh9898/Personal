class Solution:
    def reorganizeString(self, s: str) -> str:

        dict = {}
        
        for i in s:
            if i in dict:
                dict[i] +=1
            else:
                dict[i] = 1
        
        #  we have characters stored 

        maxHeap = [ [-1*cnt,char] for char,cnt in dict.items()]

        heapq.heapify(maxHeap)


        prev = None

        res = ""

        while prev or maxHeap:

            if prev and not maxHeap:
                return ""

            count,char = heapq.heappop(maxHeap)
            res +=char
            count+=1

            if prev:
                heapq.heappush(maxHeap, prev)
                prev = None

            if count!=0:
                prev = [count,char]

        return res

            


        


        