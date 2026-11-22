"""
Problem: 28. find-the-index-of-the-first-occurrence-in-a-string
Link: https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/
Pattern: two-pointers
Difficulty: Medium
Date: 2026-11-21

--- PROBLEM DESCRIPTION ---
Given two strings haystack and needle, return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack. Constraints: 1 <= haystack.length, needle.length <= 10^4.

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   The user's code incorrectly increments string_count even when characters do not match, leading to false positives; it should break immediately upon a mismatch.

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   The constraint of 10^4 length suggests that an O(N*M) approach might pass but is inefficient compared to O(N+M) string matching algorithms.

3. Complexity:
   - Time: O(N * M) -> The nested loop structure compares the needle against the haystack at every possible starting position.
   - Space: O(1) -> The algorithm uses a constant amount of extra space regardless of input size.

4. What Else? (Alternative approaches or trade-offs):
   The optimal approach is the Knuth-Morris-Pratt (KMP) algorithm, which uses a prefix function (LPS table) to skip unnecessary comparisons.
"""

class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        n = len(haystack)
        m = len(needle)

        string_count = 0

        for i in range(0,n-m+1,1): # n = 10 , m = 3 , n-m = 7 =6,7,8,9
            temp_i = i
            string_count = 0
            for j in range(0,m,1):
                if needle[j] != haystack[temp_i+j]:
                    continue
                else:
                    string_count += 1
            if (string_count == m):
                return i


        return -1
