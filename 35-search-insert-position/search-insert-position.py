class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:

        
        l = 0
        r = len(nums)-1

        mid = l+(r-l)//2

        if target > nums[r]:
            return r+1
        elif target<nums[l]:
            return 0
        elif target == nums[r]:
            return r

        while l<=r:

            mid = l+(r-l)//2

            if nums[mid] == target:
                return mid

            elif nums[mid]>target:
                r = mid-1
            else:
                l = mid+1
        
        if target>nums[mid]:
            return mid+1
        
        return mid
        