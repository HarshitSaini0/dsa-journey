"""
Problem: 20. Valid Parentheses
Link: https://leetcode.com/problems/valid-parentheses/
Pattern: stack
Difficulty: Easy
Date: 2026-11-20

--- PROBLEM DESCRIPTION ---
Determine if a string containing only '(', ')', '{', '}', '[' and ']' is valid by ensuring every opening bracket is closed by the same type in the correct order. Constraints: 1 <= s.length <= 10^4.

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   Failing to check if the stack is empty before popping, or incorrectly handling mismatched bracket types, leads to runtime errors or false positives.

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   The LIFO (Last-In-First-Out) nature of nested structures and the requirement to match the most recent opening bracket immediately points to a stack.

3. Complexity:
   - Time: O(n) -> We iterate through the string exactly once, performing constant time stack operations for each character.
   - Space: O(n) -> In the worst case of all opening brackets, the stack will store up to n characters.

4. What Else? (Alternative approaches or trade-offs):
   A hash map can replace the list index lookups to improve readability and potentially performance by providing O(1) bracket matching.
"""

class Solution:
    def isValid(self, s: str) -> bool:
        if len(s) % 2 != 0:
            return False

        bracket_stack = []
        starting_bracket = ['(', '{', '[']
        ending_bracket = [')', '}', ']']

        for p in s:
            if p in starting_bracket:
                bracket_stack.append(p)
            elif p in ending_bracket:
                if not bracket_stack:
                    return False
                index_of_p = ending_bracket.index(p)
                if bracket_stack[-1] == starting_bracket[index_of_p]:
                    bracket_stack.pop()
                else:
                    return False
            else:
                return False

        return len(bracket_stack) == 0
