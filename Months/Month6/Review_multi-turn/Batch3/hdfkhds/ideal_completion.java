        public void resolveComplaints(List<Complaint> complaintsList) {
            complaintsList.forEach(Complaint::resolveComplaint);
        }

        public String overseeLearnerRecords(Learner learner) {
            return learner.getName() + ", Enrolled: " + learner.getEnrolledCourses().size() + 
                   ", Completed: " + learner.getCompletedCourses().size() + 
                   ", Complaints: " + learner.getComplaintsList().size();
        }

        public void updateLearnerName(Learner learner, String name) {
            learner.setName(name);
        }

        public void updateLearnerEmail(Learner learner, String email) {
            learner.setEmail(email);
        }

        public void updateLearnerPassword(Learner learner, String password) {
            learner.setPassword(password);
        }

        public String allocateInstructorToCourse(Course course, Instructor instructor) {
            if (!instructor.getQualifications().contains(course.getLeastRequiredInstructorQualification())) {
                return "Instructor not qualified.";
            } else {
                course.setInstructor(instructor);
                instructor.addCourse(course);
                return instructor + " assigned to " + course.getName() + ".";
            }
        }
    }

    public static class Instructor extends User {
        private List<Course> coursesManaged;
        private List<String> qualifications;

        public Instructor(String name, String email, String password) {
            super(name, email, password);
            this.coursesManaged = new ArrayList<>();
            this.qualifications = new ArrayList<>();
        }

        public void setQualifications(String[] qualifications) {
            this.qualifications = Arrays.asList(qualifications);
        }

        public void addCourse(Course course) {
            this.coursesManaged.add(course);
        }

        public List<String> getQualifications() { return qualifications; }

        public String viewRegisteredLearners(Course course) {
            return course.getEnrolledLearners().stream()
                .map(User::getName)
                .collect(Collectors.joining());
        }
    }

    public static class Course {
        private String courseId;
        private String name;
        private Instructor instructor;
        private int term;
        private int credits;
        private Course prerequisite;
        private String leastRequiredInstructorQualification;
        private List<Learner> enrolledLearners;

        public Course(String courseId, String name, int term, int credits, String leastRequiredInstructorQualification, Course prerequisite) {
            this.courseId = courseId;
            this.name = name;
            this.term = term;
            this.credits = credits;
            this.leastRequiredInstructorQualification = leastRequiredInstructorQualification;
            this.prerequisite = prerequisite;
            this.enrolledLearners = new ArrayList<>();
        }

        public void addToEnrolledLearners(Learner learner) {
            enrolledLearners.add(learner);
        }

        public String getCourseId() { return courseId; }
        public String getName() { return name; }
        public Instructor getInstructor() { return instructor; }
        public void setInstructor(Instructor instructor) { this.instructor = instructor; }
        public int getTerm() { return term; }
        public int getCredits() { return credits; }
        public Course getPrerequisite() { return prerequisite; }
        public List<Learner> getEnrolledLearners() { return enrolledLearners; }
        public String getLeastRequiredInstructorQualification() { return leastRequiredInstructorQualification; }

        @Override
        public String toString() {
            return "Course{id='" + courseId + "', name='" + name + "', term=" + term + ", credits=" + credits + "}";
        }
    }

    public static class Complaint {
        private String description;
        private String status;
        private LocalDate loggedDate;

        public Complaint(String description, LocalDate loggedDate) {
            this.description = description;
            this.status = "Pending";
            this.loggedDate = loggedDate;
        }

        public void resolveComplaint() {
            this.status = "Resolved";
        }

        public String getDescription() { return description; }
        public String getStatus() { return status; }
        public LocalDate getLoggedDate() { return loggedDate; }

        @Override
        public String toString() {
            return "Status: " + status + ", Description: " + description;
        }
    }
}
