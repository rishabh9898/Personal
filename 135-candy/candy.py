from typing import List

class Solution:
    def candy(self, ratings: List[int]) -> int:
        # Handle edge cases
        if not isinstance(ratings, list) or not ratings:
            return 0

        n = len(ratings)
        res = [1] * n  # Start with 1 candy for each child

        # Forward pass: Compare with the previous child
        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                res[i] = res[i - 1] + 1

        # Backward pass: Compare with the next child
        for j in range(n - 2, -1, -1):
            if ratings[j] > ratings[j + 1]:
                res[j] = max(res[j], res[j + 1] + 1)

        return sum(res)
