import jpype
from jpype import JString
from jpype import JInt
from jpype import JArray
import unittest
import os

class TestCourseEnrollment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(os.path.dirname(__file__))

        # Start the JVM
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[path])

    @classmethod
    def tearDownClass(cls):
        if jpype.isJVMStarted():
            jpype.shutdownJVM()

    def setUp(self):
        # Import the Java class
        self.IdealCompletion = jpype.JClass('IdealCompletion')
        self.Course = self.IdealCompletion.Course
        self.Learner = self.IdealCompletion.Learner
        self.Instructor = self.IdealCompletion.Instructor
        self.Admin = self.IdealCompletion.Admin

    # A helper method to get a completed course
    @staticmethod
    def getCompletedCourse(self, course_id, course_name, course_instructor_qualification):
        return self.Course(JString(course_id), JString(course_name), JInt(1), JInt(4), JString(course_instructor_qualification), None)
    
    # A helper method to get a course
    @staticmethod
    def getCourse(self, course_id, course_name, course_instructor_qualification, prerequisite):
        return self.Course(JString(course_id), JString(course_name), JInt(2), JInt(6), JString(course_instructor_qualification), prerequisite)
    
    # A helper method to get course catalog
    @staticmethod
    def getCourseCatalog(self):
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        cs101 = TestCourseEnrollment.getCourse(self, "CS101", "Computer Science 101", "Phd", mth101)
        phy101 = TestCourseEnrollment.getCourse(self, "PHYSICS101", "Physics 101", "BSc", mth101)
        chm101 = TestCourseEnrollment.getCourse(self, "CHEMISTRY101", "Chemistry 101", "BSc", mth101)
        bio101 = TestCourseEnrollment.getCourse(self, "BIOLOGY101", "Biology 101", "BSc", eng101)
        IntArrayCls = JArray(self.Course)
        return IntArrayCls([cs101, phy101, chm101, bio101])

    # A helper method to get a learner
    @staticmethod
    def getLearner(self, name, email, password):
        learner = self.Learner(JString(name), JString(email), JString(password), JInt(2))
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        learner.addToCompletedCourses(mth101, JString("A"))
        learner.addToCompletedCourses(eng101, JString("B"))
        return learner
    
    # A helper method to get an instructor
    @staticmethod
    def getInstructor(self, name, email, password):
        instructor = self.Instructor(JString(name), JString(email), JString(password))
        instructor.setOfficeHourStart(JInt(2), JInt(9), JInt(0));
        instructor.setOfficeHourEnd(JInt(6), JInt(17), JInt(0));
        instructor.setQualifications([JString("BSc"), JString("MSc")]);
        return instructor
    
    # A helper method to get an admin
    @staticmethod
    def getAdmin(self, name, email, password):
        return self.Admin(JString(name), JString(email), JString(password))

    # A helper method to allocate an instructor to a course
    @staticmethod
    def allocateInstructorToCourse(admin, instructor, course):
        return admin.allocateInstructorToCourse(course, instructor)

    # A helper method for filing complaints
    @staticmethod
    def fileComplaints(learner):
        learner.fileComplaint(JString("Schedule conflict"))
        learner.fileComplaint(JString("Login error"))
        return learner
    
    # A helper method to enrol a learner in courses
    @staticmethod
    def enrolLearnerInCourses(self):
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        cs101 = TestCourseEnrollment.getCourse(self, "CS101", "Computer Science 101", "BSc", mth101)
        cs101.setSchedule(JInt(3), JInt(10), JInt(0), JInt(2))
        phy101 = TestCourseEnrollment.getCourse(self, "PHYSICS101", "Physics 101", "BSc", mth101)
        phy101.setSchedule(JInt(4), JInt(12), JInt(0), JInt(2))
        chm101 = TestCourseEnrollment.getCourse(self, "CHEMISTRY101", "Chemistry 101", "BSc", mth101)
        chm101.setSchedule(JInt(5), JInt(13), JInt(0), JInt(2))
        learner = TestCourseEnrollment.getLearner(self, "John", "john@example.com", "pass123")
        learner.addToCompletedCourses(mth101, JString("A"))
        learner.addToCompletedCourses(eng101, JString("B"))
        learner.enrollInCourse(cs101)
        learner.enrollInCourse(phy101)
        learner.enrollInCourse(chm101)
        return learner

    # Test that users can login with valid credentials. This is to ensure that the login method is correctly implemented.
    def test_users_valid_credentials_can_login(self):
        learner = self.Learner(JString("John"), JString("john@example.com"), JString("pass123"), JInt(2))
        learner_login = learner.login("john@example.com", "pass123")
        instructor = self.Instructor(JString("Dr. Smith"), JString("smith@example.com"), JString("pass456"))
        instructor_login = instructor.login("smith@example.com", "pass456")
        admin = TestCourseEnrollment.getAdmin(self, "Admin", "admin@example.com", "admin123")
        admin_login = admin.login("admin@example.com", "admin123")

        self.assertTrue(learner_login)
        self.assertTrue(instructor_login)
        self.assertTrue(admin_login)

    # Test that users cannot login with invalid credentials. This is to ensure that the login method is correctly implemented.
    def test_users_invalid_credentials_cannot_login(self):
        learner = self.Learner(JString("John"), JString("john@example.com"), JString("pass123"), JInt(2))
        learner_login = learner.login("janet@example.com", "pass123")
        instructor = self.Instructor(JString("Dr. Smith"), JString("smith@example.com"), JString("pass456"))
        instructor_login = instructor.login("smith@example.com", "passed456")
        admin = TestCourseEnrollment.getAdmin(self, "Admin", "admin@example.com", "admin123")
        admin_login = admin.login("administrator@example.com", "administrator123")

        self.assertFalse(learner_login)
        self.assertFalse(instructor_login)
        self.assertFalse(admin_login)

    # Test that admin can oversee course catalog. This is to ensure that the admin is always aware of the course catalog's status.
    def test_admin_can_oversee_course_catalogue(self):
        admin = TestCourseEnrollment.getAdmin(self, "Admin", "admin@example.com", "admin123")
        course_catalog = TestCourseEnrollment.getCourseCatalog(self)
        output = admin.overseeCourseListings(course_catalog)

        expected_output = 4

        self.assertEqual(output, expected_output)

    # Test that admin can modify course catalogue. This is to ensure that the admin can manage the course catalog.
    def test_admin_can_modify_course_catalog(self):
        # Before the update
        admin = TestCourseEnrollment.getAdmin(self, "Nill", "admin@example.com", "admin123")
        course_catalog = TestCourseEnrollment.getCourseCatalog(self)
        output_1 = admin.overseeCourseListings(course_catalog)

        expected_output_1 = 4

        self.assertEqual(output_1, expected_output_1)

        # The update
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        geo101 = self.Course(JString("GEOGRAPHY101"), JString("Geography 101"), JInt(2), JInt(6), JString("BSc"), mth101)
        geo101.setSchedule(JInt(3), JInt(16), JInt(0), JInt(2))
        course_catalog_after_update = admin.addCourseToCatalogue(course_catalog, geo101)

        # After the update
        output_2 = admin.overseeCourseListings(course_catalog_after_update)

        expected_output_2 = 5

        self.assertEqual(output_2, expected_output_2)

    # Test that admin can oversee learner's records. This is to ensure that the admin can see the current learner's records.
    def test_admin_can_oversee_learner_records(self):
        learner = TestCourseEnrollment.getLearner(self, "Sam", "sam@example.com", "pass123")
        admin = TestCourseEnrollment.getAdmin(self, "Swizz", "admin@example.com", "admin123")
        output = admin.overseeLearnerRecords(learner)

        expected_output = "Sam, Enrolled: 0, Completed: 2, Complaints: 0"

        self.assertEqual(output, expected_output)

    # Test that admin can oversee learner's records. This is to ensure that the admin can modify learner's records.
    def test_admin_can_modify_learner_info(self):
        learner = TestCourseEnrollment.getLearner(self, "Sam", "sam@example.com", "pass123")
        admin = TestCourseEnrollment.getAdmin(self, "Ben", "admin@example.com", "admin123")
        admin.updateLearnerName(learner, JString("Sean"))
        admin.updateLearnerEmail(learner, JString("sean@example.com"))
        admin.updateLearnerPassword(learner, JString("pass321"))
        output = admin.overseeLearnerRecords(learner)

        expected_output = "Sean, Enrolled: 0, Completed: 2, Complaints: 0"

        self.assertEqual(output, expected_output)

    # Test that the admin can allocate an instructor to a course. This is to ensure that the admin can allocate instructors to courses.
    def test_admin_can_allocate_instructor_to_course(self):
        # Before allocating instructor to course
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        cs101 = TestCourseEnrollment.getCourse(self, "CS101", "Computer Science 101", "BSc", mth101)
        phy101 = TestCourseEnrollment.getCourse(self, "PHYSICS101", "Physics 101", "BSc", mth101)

        expected_output_1 = "None"
        expected_output_2 = "None"

        self.assertIn(expected_output_1, str(cs101.getInstructor()))
        self.assertIn(expected_output_2, str(phy101.getInstructor()))

        # Allocate instructor to course
        instructor_1 = TestCourseEnrollment.getInstructor(self, "Dr. Smith", "smith@example.com", "pass456")
        instructor_2 = TestCourseEnrollment.getInstructor(self, "Dr. Loveth", "loveth@example.com", "pass456")
        admin = TestCourseEnrollment.getAdmin(self, "Admin", "admin@example.com", "admin123")
        TestCourseEnrollment.allocateInstructorToCourse(admin, instructor_1, cs101)
        TestCourseEnrollment.allocateInstructorToCourse(admin, instructor_2, phy101)

        # After allocating instructor to course
        expected_output_3 = "Dr. Smith"
        expected_output_4 = "Dr. Loveth"

        self.assertIn(expected_output_3, str(cs101.getInstructor()))
        self.assertIn(expected_output_4, str(phy101.getInstructor()))

    # Test that the admin cannot allocate an unqualified instructor to a course. This is to ensure that only qualified instructors are allocated to courses.
    def test_admin_cannot_allocate_unqualified_instructor_to_course(self):
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        cs101 = TestCourseEnrollment.getCourse(self, "CS101", "Computer Science 101", "Phd", mth101)
        instructor = TestCourseEnrollment.getInstructor(self, "Dr. Smith", "smith@example.com", "pass456")
        admin = TestCourseEnrollment.getAdmin(self, "Admin", "admin@example.com", "admin123")

        output = TestCourseEnrollment.allocateInstructorToCourse(admin, instructor, cs101)

        expected_output = "Instructor not qualified."

        self.assertEqual(output, expected_output)

    # Test that a learner can browse courses. This is to ensure that learners can go through available courses.
    def test_learner_can_browse_courses(self):
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        cs101 = TestCourseEnrollment.getCourse(self, "CS101", "Computer Science 101", "BSc", mth101)
        cs101.setSchedule(JInt(3), JInt(10), JInt(0), JInt(2))
        phy101 = TestCourseEnrollment.getCourse(self, "PHYSICS101", "Physics 101", "BSc", mth101)
        phy101.setSchedule(JInt(4), JInt(12), JInt(0), JInt(2))
        chm101 = TestCourseEnrollment.getCourse(self, "CHEMISTRY101", "Chemistry 101", "BSc", mth101)
        chm101.setSchedule(JInt(5), JInt(13), JInt(0), JInt(2))
        bio101 = TestCourseEnrollment.getCourse(self, "BIOLOGY101", "Biology 101", "BSc", eng101)
        bio101.setSchedule(JInt(5), JInt(13), JInt(0), JInt(2))
        learner = TestCourseEnrollment.enrolLearnerInCourses(self)

        IntArrayCls = JArray(self.Course)
        output = learner.browseCourses(IntArrayCls([cs101, phy101, chm101, bio101]))

        expected_output_1 = "Course ID: CS101, Name: Computer Science 101, Instructor: null, Term: 2, Credits: 6, Prerequisite: Mathematics 101"
        expected_output_2 = "Course ID: PHYSICS101, Name: Physics 101, Instructor: null, Term: 2, Credits: 6, Prerequisite: Mathematics 101"
        expected_output_3 = "Course ID: CHEMISTRY101, Name: Chemistry 101, Instructor: null, Term: 2, Credits: 6, Prerequisite: Mathematics 101"
        expected_output_4 = "Course ID: BIOLOGY101, Name: Biology 101, Instructor: null, Term: 2, Credits: 6, Prerequisite: English 101"

        self.assertIn(expected_output_1, str(output))
        self.assertIn(expected_output_2, str(output))
        self.assertIn(expected_output_3, str(output))
        self.assertIn(expected_output_4, str(output))

    # Test that a learner can enroll in a course. This is to ensure that learners can enroll in courses.
    def test_learner_can_enroll_in_courses(self):
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        cs101 = TestCourseEnrollment.getCourse(self, "CS101", "Computer Science 101", "BSc", mth101)
        phy101 = TestCourseEnrollment.getCourse(self, "PHYSICS101", "Physics 101", "BSc", mth101)
        chm101 = TestCourseEnrollment.getCourse(self, "CHEMISTRY101", "Chemistry 101", "BSc", mth101)
        learner = TestCourseEnrollment.getLearner(self, "Stephanie", "stephanie@example.com", "pass123")
        learner.addToCompletedCourses(mth101, JString("A"));
        output_1 = learner.enrollInCourse(cs101)
        output_2 = learner.enrollInCourse(phy101)
        output_3 = learner.enrollInCourse(chm101)

        expected_output_1 = "Enrolled in Computer Science 101."
        expected_output_2 = "Enrolled in Physics 101."
        expected_output_3 = "Enrolled in Chemistry 101."

        self.assertEqual(expected_output_1, str(output_1))
        self.assertEqual(expected_output_2, str(output_2))
        self.assertEqual(expected_output_3, str(output_3))

    # Test that a learner cannot enroll in courses beyond their credit limit. This is to ensure that learners can only enroll in courses within their credit limit.
    def test_learner_cannot_enroll_in_courses_beyond_credit_limit(self):
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        bio101 = TestCourseEnrollment.getCourse(self, "BIOLOGY101", "Biology 101", "BSc", eng101)
        learner = TestCourseEnrollment.enrolLearnerInCourses(self)
        learner.addToCompletedCourses(eng101, JString("B"))
        output = learner.enrollInCourse(bio101)

        expected_output = "Credit limit exceeded."

        self.assertEqual(expected_output, str(output))

    # Test that a learner can review course schedule. This is to ensure that learners can review course schedules.
    def test_learner_can_review_schedule(self):
        learner = learner = TestCourseEnrollment.enrolLearnerInCourses(self)
        output = learner.reviewSchedule()

        expected_output_1 = "Computer Science 101:"
        expected_output_2 = "Physics 101:"
        expected_output_3 = "Chemistry 101:"

        self.assertIn(expected_output_1, str(output))
        self.assertIn(expected_output_2, str(output))
        self.assertIn(expected_output_3, str(output))

    # Test that learners can monitor their progress. This is to ensure that learners can view their academic process.
    def test_learner_can_monitor_progress(self):
        learner = TestCourseEnrollment.getLearner(self, "Stephanie", "stephanie@example.com", "pass123")
        output = learner.monitorProgress()

        expected_output_1 = "Mathematics 101: A"
        expected_output_2 = "English 101: B"
        expected_output_3 = "SGPA: 3.5"

        self.assertIn(expected_output_1, str(output))
        self.assertIn(expected_output_2, str(output))
        self.assertIn(expected_output_3, str(output))

    # Test that learners can withdraw course. This is to ensure that learners can stop taking some courses if they want.
    def test_learner_can_withdraw_course(self):
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        chm101 = TestCourseEnrollment.getCourse(self, "CHEMISTRY101", "Chemistry 101", "BSc", mth101)
        chm101.setSchedule(JInt(5), JInt(13), JInt(0), JInt(2))
        bio101 = TestCourseEnrollment.getCourse(self, "BIOLOGY101", "Biology 101", "BSc", eng101)
        bio101.setSchedule(JInt(3), JInt(11), JInt(0), JInt(2))
        learner = self.Learner("Stephanie", "stephanie@example.com", "pass123", JInt(2))
        learner.addToCompletedCourses(eng101, JString("A"))
        learner.addToCompletedCourses(mth101, JString("B"))
        learner.enrollInCourse(chm101)
        learner.enrollInCourse(bio101)

        # Before the withrawal
        output_1 = learner.reviewSchedule()

        expected_output_1 = "Chemistry 101:"

        self.assertIn(expected_output_1, str(output_1))

        # The withdrawal
        output_2 = learner.withdrawCourse(chm101)

        expected_output_2 = "Withdrew from Chemistry 101."

        self.assertEqual(expected_output_2, str(output_2))

        # After the withdrawal
        output_3 = learner.reviewSchedule()

        self.assertNotIn(expected_output_1, str(output_3))

    # Test that learners can file complaint. This is to ensure that learners can file a complaint.
    def test_learner_can_file_complaint(self):
        learner = TestCourseEnrollment.getLearner(self, "Stephanie", "stephanie@example.com", "pass123")
        learner = self.fileComplaints(learner)
        admin = TestCourseEnrollment.getAdmin(self, "Swizz", "admin@example.com", "admin123")
        output = admin.manageComplaints(learner.getComplaintsList())

        expected_output = """Status: Pending, Description: Schedule conflict
Status: Pending, Description: Login error
"""

        self.assertEqual(expected_output, str(output))

    # Test that instructors can oversea courses. This is to ensure that instructors can get the number of courses they manage.
    def test_instructor_can_oversee_courses(self):
        # Before allocating instructor to course
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        cs101 = TestCourseEnrollment.getCourse(self, "CS101", "Computer Science 101", "BSc", mth101)
        phy101 = TestCourseEnrollment.getCourse(self, "PHYSICS101", "Physics 101", "BSc", mth101)

        # Allocate instructor to course
        instructor_1 = TestCourseEnrollment.getInstructor(self, "Dr. Smith", "smith@example.com", "pass456")
        instructor_2 = TestCourseEnrollment.getInstructor(self, "Dr. Loveth", "loveth@example.com", "pass456")
        admin = TestCourseEnrollment.getAdmin(self, "Admin", "admin@example.com", "admin123")
        TestCourseEnrollment.allocateInstructorToCourse(admin, instructor_1, cs101)
        TestCourseEnrollment.allocateInstructorToCourse(admin, instructor_2, phy101)

        output = instructor_1.overseeCourses()
        output = instructor_2.overseeCourses()
        expected_output_1 = 1
        expected_output_2 = 1

        self.assertEqual(expected_output_1, output)
        self.assertEqual(expected_output_2, output)

    # Test that instructors can oversea registered learners. This is to ensure that instructors can get a summary of users enrolled in a course.
    def test_instructor_can_oversee_registered_learners(self):
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        bio101 = TestCourseEnrollment.getCourse(self, "BIOLOGY101", "Biology 101", "BSc", eng101)
        learner = self.Learner("John", "john@example.com", "pass123", JInt(2))
        learner.addToCompletedCourses(eng101, JString("B"))
        learner.enrollInCourse(bio101)
        instructor = TestCourseEnrollment.getInstructor(self, "Dr. Smith", "smith@example.com", "pass456")
        output = instructor.viewRegisteredLearners(bio101)

        expected_output = "John\n"

        self.assertEqual(expected_output, str(output))

    # Test that instructors can update course information. This is to ensure that instructors can modify course information.
    def test_instructor_can_update_course_info(self):
        # Before allocating instructor to course
        mth101 = TestCourseEnrollment.getCompletedCourse(self, "MATH101", "Mathematics 101", "BSc")
        phy101 = TestCourseEnrollment.getCourse(self, "PHYSICS101", "Physics 101", "BSc", mth101)

        # Allocate instructor to course
        instructor = TestCourseEnrollment.getInstructor(self, "Dr. Smith", "smith@example.com", "pass456")
        admin = TestCourseEnrollment.getAdmin(self, "Admin", "admin@example.com", "admin123")
        TestCourseEnrollment.allocateInstructorToCourse(admin, instructor, phy101)

        # Verification before the update
        expected_output_1 = "6"

        self.assertEqual(expected_output_1, str(phy101.getCredits()))

        # The update
        instructor.updateCourseSchedule("PHYSICS101", 2, 11, 0, 3);
        instructor.updateCourseCredit("PHYSICS101", 8);
        eng101 = TestCourseEnrollment.getCompletedCourse(self, "ENGLISH101", "English 101", "BSc")
        instructor.updateCoursePrerequisite("PHYSICS101", eng101);

        # Verification after the update
        expected_output_2 = "8"

        self.assertIn(expected_output_2, str(phy101.getCredits()))


    # Test that an admin can filter complaints. This is to ensure that an admin can filter learner's complaints.
    def test_admin_can_filter_complaints(self):
        learner = TestCourseEnrollment.getLearner(self, "John", "john@example.com", "pass123")
        learner = self.fileComplaints(learner)

        # Filter pending complaints
        admin = TestCourseEnrollment.getAdmin(self, "Swizz", "admin@example.com", "admin123")
        output_1 = admin.filterComplaintsByStatus(learner.getComplaintsList(), JString("Pending"))

        expected_output_1 = """Status: Pending, Description: Schedule conflict
Status: Pending, Description: Login error
"""

        self.assertEqual(expected_output_1, str(output_1))

        # Filter resolved complaints
        output_2 = admin.filterComplaintsByStatus(learner.getComplaintsList(), JString("Resolved"))

        expected_output_2 = ""

        self.assertEqual(expected_output_2, str(output_2))


    # Test that an admin can resolve complaints. This is to ensure that an admin can resolve learner's complaints.
    def test_admin_can_resolve_complain(self):
        learner = TestCourseEnrollment.getLearner(self, "John", "john@example.com", "pass123")
        learner = self.fileComplaints(learner)

        # Filter pending complaints before resolution
        admin = TestCourseEnrollment.getAdmin(self, "Swizz", "admin@example.com", "admin123")
        output_1 = admin.filterComplaintsByStatus(learner.getComplaintsList(), JString("Pending"))

        expected_output_1 = """Status: Pending, Description: Schedule conflict
Status: Pending, Description: Login error
"""

        self.assertEqual(expected_output_1, str(output_1))

        # Filter resolved complaints before resolution
        output_2 = admin.filterComplaintsByStatus(learner.getComplaintsList(), JString("Resolved"))

        expected_output_2 = ""

        self.assertEqual(expected_output_2, str(output_2))

        # Resolve the complaints
        admin.resolveComplaints(learner.getComplaintsList())

        # Filter pending complaints after resolution
        output_3 = admin.filterComplaintsByStatus(learner.getComplaintsList(), JString("Pending"))

        expected_output_3 = ""

        self.assertEqual(expected_output_3, str(output_3))

        # Filter resolved complaints after resolution
        output_4 = admin.filterComplaintsByStatus(learner.getComplaintsList(), JString("Resolved"))

        expected_output_4 = """Status: Resolved, Description: Schedule conflict
Status: Resolved, Description: Login error
"""

        self.assertEqual(expected_output_4, str(output_4))

if __name__ == '__main__':
    unittest.main(verbosity=2)