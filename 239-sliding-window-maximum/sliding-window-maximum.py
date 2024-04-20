class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        v = []  # Array to store the maximum value in each window starting at index 0
        va = []  # Array to store the maximum value in each window ending at the last index
        ans = []  # Array to store the final maximum values for each window
        max_val = nums[0]  # Initialize the maximum value to the first element
        a = 0  # Counter for the current window size

        # Iterate through the input array 'nums'
        for i in range(len(nums)):
            if a == k:
                max_val = nums[i]
                a = 0

            if max_val < nums[i]:
                max_val = nums[i]

            v.append(max_val)  # Store the maximum value in the current window
            a += 1

        a = 0
        max_val = float('-inf')
        b = len(nums) % k

        # Calculate the maximum values for windows ending at the last index
        for i in range(len(nums) - 1, len(nums) - 1 - b, -1):
            if max_val < nums[i]:
                max_val = nums[i]

            va.append(max_val)

        max_val = float('-inf')

        # Calculate the maximum values for the remaining windows
        for i in range(len(nums) - 1 - b, -1, -1):
            if a == k:
                max_val = nums[i]
                a = 0

            if max_val < nums[i]:
                max_val = nums[i]

            va.append(max_val)
            a += 1

        j = len(nums) - 1

        # Compare the maximum values from 'v' and 'va' for each window and store the maximum in 'ans'
        for i in range(k - 1, len(nums)):
            if v[i] > va[j]:
                ans.append(v[i])
            else:
                ans.append(va[j])

            j -= 1

        return ans  # Return the final maximum values for each window

            



        