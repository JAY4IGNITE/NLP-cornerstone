// Prompts checked against the bundled curriculum and academic regulations.
export const TOPICS = [
  {
    id: 'attendance',
    title: 'Attendance requirements',
    description: 'Minimum attendance and exam eligibility in the academic regulations.',
    prompt: 'What is the minimum attendance requirement?',
    icon: 'CalendarCheck',
  },
  {
    id: 'courses',
    title: 'Courses & curriculum',
    description: 'CSE subjects, semester structure, and course information.',
    prompt: 'What are the subjects in semester 5?',
    icon: 'BookOpen',
  },
  {
    id: 'exams',
    title: 'Exams & assessment',
    description: 'How internal assessments and end-semester exams are weighted.',
    prompt: 'What is the examination assessment pattern?',
    icon: 'ClipboardList',
  },
  {
    id: 'grading',
    title: 'Grades & passing marks',
    description: 'The letter grading scale and minimum marks needed to pass.',
    prompt: 'What is the grading system?',
    icon: 'GraduationCap',
  },
  {
    id: 'prerequisites',
    title: 'Course prerequisites',
    description: 'The prior courses listed for subjects in the CSE handbook.',
    prompt: 'What are the prerequisites for Machine Learning?',
    icon: 'Route',
  },
  {
    id: 'objectives',
    title: 'Learning objectives',
    description: 'Course objectives, learning outcomes, and syllabus topics.',
    prompt: 'What are the course objectives of Database Management Systems?',
    icon: 'Target',
  },
];
