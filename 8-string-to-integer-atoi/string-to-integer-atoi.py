class Solution:
    def myAtoi(self, s: str) -> int:
        strRes = ""
        isNeg = False
        started = False

        for i in s:
            if i == " " and not started:
                # Skip leading spaces
                continue

            if i == "-" and not started:
                # Handle negative sign
                started = True
                isNeg = True
            elif i == "+" and not started:
                # Handle positive sign
                started = True
                continue
            elif i.isdigit():
                # Collect digits
                strRes += i
                started = True
            elif started:
                # If we've started collecting digits and encounter a non-digit
                break
            else:
                # If no number has started, break immediately
                break

        # If no valid number is found
        if not strRes:
            return 0

        # Convert the result
        res = int(strRes)
        if isNeg:
            res = -res

        # Clamp the result to fit within 32-bit integer range
        return max(min(res, 2**31 - 1), -2**31)
