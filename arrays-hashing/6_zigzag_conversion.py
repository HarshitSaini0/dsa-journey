"""
Problem: 6. Zigzag Conversion
Link: https://leetcode.com/problems/zigzag-conversion/
Pattern: arrays-hashing
Difficulty: Medium
Date: 2026-10-30

--- PROBLEM DESCRIPTION ---
The string is written in a zigzag pattern on a given number of rows and then read line by line. Given the string and number of rows, return the converted string. Constraints: 1 <= s.length <= 1000, 1 <= numRows <= 1000.

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   Attempting to derive a complex mathematical formula for character indices is error-prone; simulation is much more intuitive and less bug-prone.

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   The problem asks to distribute characters into rows based on a specific visual pattern, which is best handled by maintaining a list of strings representing each row.

3. Complexity:
   - Time: O(n) -> We iterate through the input string exactly once to distribute characters into the row buckets.
   - Space: O(n) -> We store all characters of the input string across the row buckets, requiring linear space relative to the input.

4. What Else? (Alternative approaches or trade-offs):
   One could calculate the cycle length (2 * numRows - 2) and use modular arithmetic to place characters directly into their respective rows without simulation.
"""

def convert(s: str, numRows: int) -> str:
    if numRows == 1 or numRows >= len(s):
        return s

    rows = [""] * numRows
    current_row = 0
    direction = 1

    for char in s:
        rows[current_row] += char

        if current_row == 0:
            direction = 1
        elif current_row == numRows - 1:
            direction = -1

        current_row += direction

    return "".join(rows)
