"""
Problem: 17. letter-combinations-of-a-phone-number
Link: https://leetcode.com/problems/letter-combinations-of-a-phone-number/
Pattern: backtracking
Difficulty: Medium
Date: 2026-11-19

--- PROBLEM DESCRIPTION ---
Given a string containing digits from 2-9, return all possible letter combinations that the number could represent based on phone keypad mapping. Constraints: 0 <= digits.length <= 4.

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   Iterative approaches with nested loops are impossible because the number of loops depends on the input length, necessitating recursion.

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   The requirement to generate all possible combinations of a variable-length input strongly indicates a backtracking or DFS approach.

3. Complexity:
   - Time: O(4^n * n) -> We explore up to 4 choices per digit for n digits, and joining the path takes O(n) time.
   - Space: O(n) -> The recursion stack depth and the temporary path list both scale linearly with the number of input digits.

4. What Else? (Alternative approaches or trade-offs):
   An iterative approach using a queue (BFS) can also solve this by progressively appending characters to existing combinations in the queue.
"""

def letterCombinations(digits):
    num_map = { '2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs', '8':'tuv','9':'wxyz'}

    n = len(digits)
    if n == 0:
        return[]

    path_list = []
    res_list = []
    def backtrack(i):
        if i == n:
            res_list.append("".join(path_list))
            return
        for char in num_map[digits[i]]:
            path_list.append(char)
            backtrack(i+1)
            path_list.pop()


    backtrack(0)
    return res_list


    # exponentional grwoth ho giii 
    
    
print(letterCombinations('22'))
