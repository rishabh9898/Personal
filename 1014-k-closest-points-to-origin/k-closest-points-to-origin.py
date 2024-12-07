class Solution:
    def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:

        minHeap = []

        for x,y in points:
            dist = x**2 + y**2
            minHeap.append((dist,(x,y)))        
        counter = 0

        heapq.heapify(minHeap)

        res = []

        print(minHeap)
        while counter < k:
            counter+=1
            if minHeap:
                res.append(heapq.heappop(minHeap)[1])
        return res
            




            


        