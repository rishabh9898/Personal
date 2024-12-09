class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:

        A = nums1
        B = nums2

        half = (len(A) + len(B))//2

        if len(B) < len(A):
            A,B = B,A 
        
        l,r = 0, len(A)-1

        while True:

            i = l+(r-l)//2
            j = half -i-2
            Aleft = A[i] if i>=0 else float("-inf")
            Aright = A[i+1] if i+1 < len(A) else float("inf")
            Bleft = B[j] if j>=0 else float("-inf")
            Bright = B[j+1] if j+1 < len(B) else float("inf")

            if Aleft <= Bright and Bleft <= Aright:
                if (len(A) + len(B))%2==1:
                    return min(Aright,Bright)
                else:
                    num1 = max(Aleft,Bleft)
                    num2 = min(Aright,Bright)
                    median = (num1 + num2)/2
                    return median
            
            elif Aleft > Bright:
                r = i-1
            else:
                l = i+1




