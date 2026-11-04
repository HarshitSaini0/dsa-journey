"""
Problem: 8. String to Integer (atoi)
Link: https://leetcode.com/problems/string-to-integer-atoi/
Pattern: math-geometry
Difficulty: Medium
Date: 2026-11-04

--- PROBLEM DESCRIPTION ---
Implement the `myAtoi(string s)` function to parse an integer from a string according to specific conversion rules. Ignore leading whitespace, handle optional '+' or '-' signs, read digits until the first non-digit character, and clamp values outside the 32-bit signed range `[-2^31, 2^31 - 1]`.

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   String slicing like `s[1:]` and using `s.strip()` creates unnecessary string copies in memory; also, `s.strip()` removes trailing whitespace which can be redundant. Using `str.index()` adds minor lookup overhead compared to `ord(c) - ord('0')`.

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   Rule-based sequential parsing requiring leading whitespace elimination, single sign handling, sequential digit accumulation, and bounded range overflow checks directly indicates a single-pass simulation/state-machine approach.

3. Complexity:
   - Time: O(N) -> Single pass through the string of length N to parse digits and validate constraints.
   - Space: O(N) -> String slicing and `strip()` create new string copies of up to size N.

4. What Else? (Alternative approaches or trade-offs):
   An optimal constant space O(1) approach maintains a single index pointer moving from left to right instead of slicing strings. In languages without arbitrary-precision integers (like C++ or Java), overflow must be checked before multiplying by 10. A Deterministic Finite Automaton (DFA) state machine is a formal alternative.
"""

class Solution:
    def myAtoi(self, s: str) -> int:
        fixed_str = s.strip()
        nums_str = '0123456789'
        is_neg = False
        start = False
        counter = 0 
        if len(fixed_str)==0:
            return 0
        if fixed_str[0]=='-':
            is_neg = True
            fixed_str = fixed_str[1::]
        elif fixed_str[0] == '+':
            fixed_str = fixed_str[1::]

        for char in fixed_str:
            if char in nums_str:
                if start or char!='0':
                    counter = (counter * 10) + nums_str.index(char)
                    start = True
                elif char == '0':
                    continue
            else:
                break


        if is_neg:
            counter = counter * (-1)
        INT_MIN = -2**31
        INT_MAX = 2**31 - 1

        return max(INT_MIN, min(counter, INT_MAX))
