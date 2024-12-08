

class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        # Merge the two sorted arrays
        res = []
        i, j = 0, 0

        # Merge elements from both arrays
        while i < len(nums1) and j < len(nums2):
            if nums1[i] < nums2[j]:
                res.append(nums1[i])
                i += 1
            else:
                res.append(nums2[j])
                j += 1

        # Append any remaining elements from nums1
        while i < len(nums1):
            res.append(nums1[i])
            i += 1

        # Append any remaining elements from nums2
        while j < len(nums2):
            res.append(nums2[j])
            j += 1

        # Find the median
        totalLen = len(res)

        if totalLen % 2 == 1:
            return res[totalLen // 2]
        else:
            medianSum = (res[(totalLen // 2) - 1] + res[totalLen // 2]) / 2.0
            return medianSum
