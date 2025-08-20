import unittest
from TestableIC import relay_sheets_to_last_student

class TestRelaySheets(unittest.TestCase):
    def test_case_1(self):
        """
        Test Case 1:
        Input: [34, 67, 43, 78, 89]
        Explanation:
            - Student 0 (34):
                - u=1 (odd): Find the smallest B[l] >= 34. Possible candidates: 67, 43, 78, 89.
                  The smallest B[l] >= 34 is 43 (student 2).
                - u=2 (even): Find the largest B[l] <= 43. Candidates: 78, 89.
                  No student has B[l] <= 43 among these, so the sheet cannot be passed further.
            - Student 1 (67):
                - u=1 (odd): Find the smallest B[l] >= 67. Candidates: 78, 89.
                  The smallest B[l] >= 67 is 78 (student 3).
                - u=2 (even): Find the largest B[l] <= 78. Candidates: 89.
                  No student has B[l] <= 78 among these, so the sheet cannot be passed further.
            - Student 2 (43):
                - u=1 (odd): Find the smallest B[l] >= 43. Candidates: 78, 89.
                  The smallest B[l] >= 43 is 78 (student 3).
                - u=2 (even): Find the largest B[l] <= 78. Candidates: 89.
                  No student has B[l] <= 78 among these, so the sheet cannot be passed further.
            - Student 3 (78):
                - u=1 (odd): Find the smallest B[l] >= 78. Candidates: 89.
                  The smallest B[l] >= 78 is 89 (student 4).
                - u=2 (even): Since student 4 is the last student, the sheet has successfully reached the destination.
            - Student 4 (89):
                - Already at the last student; no pass required.
        Expected Output: 2
        (Only students 3 and 4 can successfully pass their sheets to the last student.)
        """
        self.assertEqual(relay_sheets_to_last_student([34, 67, 43, 78, 89]), 2)
    
    def test_case_2(self):
        """
        Test Case 2:
        Input: [1, 2, 3, 4, 5, 6, 7]
        Explanation:
            - All students have strictly increasing B[l] values.
            - For u=1 (odd):
                - Each student can pass the sheet to the next student since B[l] >= B[k].
                - The smallest B[l] >= B[k] is always B[k+1].
            - For u=2 (even):
                - At the next step, students attempt to pass back, but since B[l] >= B[k], no valid passes occur.
            - As a result, only the last two students (students 5 and 6) can successfully pass their sheets to the last student.
        Expected Output: 2
        (Only the last two students can successfully pass their sheets to the last student.)
        """
        self.assertEqual(relay_sheets_to_last_student([1, 2, 3, 4, 5, 6, 7]), 2)
    
    def test_case_3(self):
        """
        Test Case 3:
        Input: [5, 4, 3, 2, 1]
        Explanation:
            - All students have strictly decreasing B[l] values.
            - For u=1 (odd):
                - Each student attempts to pass the sheet to a student with a higher B[l], but no such student exists.
            - As a result, no sheets can be passed except for the last student, who already holds their sheet.
        Expected Output: 1
        (Only the last student inherently has the sheet.)
        """
        self.assertEqual(relay_sheets_to_last_student([5, 4, 3, 2, 1]), 1)
    
    def test_case_4(self):
        """
        Test Case 4:
        Input: [10, 5, 15, 6, 20]
        Explanation:
            - Student 0 (10):
                - u=1 (odd): Find the smallest B[l] >= 10. Candidates: 15, 6, 20.
                  The smallest B[l] >= 10 is 15 (student 2).
                - u=2 (even): Find the largest B[l] <= 15. Candidates: 6, 20.
                  The largest B[l] <= 15 is 6 (student 3).
                - u=3 (odd): Find the smallest B[l] >= 6. Candidates: 20.
                  The smallest B[l] >= 6 is 20 (student 4).
                  The sheet successfully reaches the last student.
            - Student 1 (5):
                - u=1 (odd): Find the smallest B[l] >= 5. Candidates:15,6,20.
                  The smallest B[l] >= 5 is 6 (student 3).
                - u=2 (even): Find the largest B[l] <= 6. Candidates:20.
                  No student has B[l] <= 6 among these, so the sheet cannot be passed further.
            - Student 2 (15):
                - u=1 (odd): Find the smallest B[l] >= 15. Candidates:20.
                  The smallest B[l] >= 15 is 20 (student 4).
                  The sheet successfully reaches the last student.
            - Student 3 (6):
                - u=1 (odd): Find the smallest B[l] >= 6. Candidates:20.
                  The smallest B[l] >= 6 is 20 (student 4).
                  The sheet successfully reaches the last student.
            - Student 4 (20):
                - Already at the last student; no pass required.
        Expected Output: 4
        (Students 0, 2, 3, and 4 can successfully pass their sheets to the last student.)
        """
        self.assertEqual(relay_sheets_to_last_student([10, 5, 15, 6, 20]), 4)
    
    def test_case_5_all_equal(self):
        """
        Test Case 5:
        Input: [7, 7, 7, 7]
        Explanation:
            - All students have the same B[l] value.
            - For u=1 (odd):
                - Each student can pass the sheet to the next student since B[l] >= B[k] (equality holds).
                - The smallest B[l] >= B[k] is the next student in the row.
            - For u=2 (even):
                - Each student attempts to pass back to a student with B[l] <= B[k], which includes all possible next students.
                - The largest B[l] <= B[k] is the next student in the row.
            - The passing sequence can proceed sequentially to the last student.
            - Therefore, all students except the last one can pass their sheets successfully to the last student.
            - Additionally, the last student already has their sheet.
        Expected Output: 4
        (All four students can successfully pass their sheets to the last student.)
        """
        self.assertEqual(relay_sheets_to_last_student([7, 7, 7, 7]), 4)
    
    def test_case_6_single_student(self):
        """
        Test Case 6:
        Input: [100]
        Explanation:
            - Only one student exists, who is also the last student.
            - No pass required as the sheet is already with the last student.
        Expected Output: 1
        (Only the last student inherently has the sheet.)
        """
        self.assertEqual(relay_sheets_to_last_student([100]), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
