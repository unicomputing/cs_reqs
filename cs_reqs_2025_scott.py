# check degree requirements for BS in CSE at SBU

from typing import NamedTuple, Set, List
from enum import Enum
from statistics import mean

#Grade = Enum('Grade', 'A A- B+ B B- C+ C C- D+ D F I I/F P NC S U Q W')

def C_or_higher(grade):
    return grade in {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}

# convert letter grade to numeric grade
grade_to_int = {
    'A': 4.00,
    'A-': 3.67,
    'B+': 3.33,
    'B': 3.00,
    'B-': 2.67,
    'C+': 2.33,
    'C': 2.00,
    'C-': 1.67,
    'D+': 1.33,
    'D': 1.00,
    'F': 0.00,
    'I/F': 0.00,
    'Q': 0.00
}

# a class taken.
class ClassTaken(NamedTuple):
    course: str  # Example: 'CSE 113'
    credits: int
    grade: str
    transfer: bool # true if this is a transfer class.

class Student(NamedTuple):
    classesTaken: Set[ClassTaken]

# test whether a class is upper-division, i.e., 300=level and above
def upper_division(course):
    return int(course[4:]) >= 300

# return the GPA for a set of classes taken
# The following grades are not calculated into the g.p.a.: P, NC, NR, R, S, U, W.  Also I.
# https://catalog.stonybrook.edu/content.php?catoid=7&navoid=81#view-gpa
def GPA(taken):
    return mean([ grade_to_int.get(c.grade) for c in taken if c.grade in grade_to_int.keys() ])

# Fall 2025 degree requirements for the CS major
# https://catalog.stonybrook.edu/preview_program.php?catoid=7&poid=318&returnto=224

# each requirement for the CS Major is evaluated by a function below.
# the argument is the set of classes or courses taken by the student and passed with a grade of C or higher.
# the function returns a Boolean indicating whether the requirement is satisfied.

# 1. Required Introductory Courses
def required_introductory_courses(taken_crs):
    return (('CSE 113' in taken_crs or 'CSE 150' in taken_crs) 
            and ({'CSE 114', 'CSE 214'} <= taken_crs or {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'} <= taken_crs)
            and 'CSE 220' in taken_crs
        # Students pursuing Honors may substitute CSE 350 - Theory of Computation: Honors for CSE 213.
            and ('CSE 213' in taken_crs or 'CSE 350' in taken_crs))

# 2. Required Advanced Courses
def required_advanced_courses(taken_crs):
    return (('CSE 307' in taken_crs or {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'} <= taken_crs)
            and {'CSE 316', 'CSE 320'} <= taken_crs
            and ('CSE 373' in taken_crs or 'CSE 385' in taken_crs) 
            and ('CSE 356' in taken_crs or 'CSE 416' in taken_crs))

item_1_courses = {'CSE 113', 'CSE 150', 'CSE 114', 'CSE 214', 'CSE 160', 'CSE 161', 'CSE 261', 'CSE 220', 'CSE 213', 'CSE 350'}

item_2_courses = {'CSE 260', 'CSE 307', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 385', 'CSE 356', 'CSE 416'}

# 3. Computer Science Electives
# Six additional upper-division technical CSE courses, each of which must carry at least three credits. Courses used to satisfy the required advanced courses requirement may not be used to satisfy the computer science electives requirement. Technical electives do not include teaching practica (CSE 475), the first part of the senior honors project (CSE 495), and courses designated as non-technical in the course description (such as CSE 301). Students may only use 3 credits from the following courses to satisfy one upper-division technical elective for the CSE major requirements: CSE 487, CSE 496, VIP 395, VIP 396, VIP 495, VIP 496. 

# return the set of classes that contribute to satisfying the CS electives requirement.
def electives(taken):
    electives_taken = {c for c in taken if c.course[:3] == 'CSE' and upper_division(c.course) and c.credits >= 3 and c.course not in item_2_courses 
                       and c.course not in {'CSE 475', 'CSE 495', 'CSE 300', 'CSE 301', 'CSE 312'}}
    # "surplus" advanced courses can be used to satisfy the electives requirement.  
    # such a surplus arises if a student takes CSE 356 and CSE 416, or takes the honors sequence CSE 160,161,260,261 and CSE 307.
    # add surplus advanced courses to electives_taken.
    taken_crs = {c.course for c in taken}
    if 'CSE 356' in taken_crs and 'CSE 416' in taken_crs:
        electives_taken = electives_taken | {c for c in taken if c.course == 'CSE 416'}
    if {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'} <= taken_crs and 'CSE 307' in taken_crs:
        electives_taken = electives_taken | {c for c in taken if c.course == 'CSE 307'}
    project_courses = {'CSE 487', 'CSE 496', 'VIP 395', 'VIP 396', 'VIP 495', 'VIP 496'}
    projects = {c for c in electives_taken if c.course in project_courses}
    # count at most 3 credits from at most one of the project courses, by (arbitrarily) selecting one project elective taken
    # and capping it at 3 credits (this affects the requirement for number of credits taken at SB).
    return (electives_taken - projects) + set(list(projects)[0]._replace(credits=3)) if projects else electives_taken

# check the CS electives requirement
def computer_science_electives(taken):
    return len(electives(taken)) >= 6

# 4. One of the following calculus course sequences:
def calculus(taken_crs):
    return ({'AMS 151', 'AMS 161'} <= taken_crs
            or {'MAT 125', 'MAT 126', 'MAT 127'} <= taken_crs
            or {'MAT 131', 'MAT 132'} <= taken_crs)

# 5. One of the following linear algebra courses
def linear_algebra(taken_crs):
    return  'MAT 211' in taken_crs or 'AMS 210' in taken_crs

# 6. Required Upper-Division Statistics Course
def statistics(taken_crs):
    return 'AMS 310' in taken_crs

# 7. At least one of the following science lecture/laboratory combinations:
science_lecture_lab_combs = {frozenset({'BIO 201', 'BIO 204'}), frozenset({'BIO 202', 'BIO 204'}), frozenset({'BIO 203', 'BIO 204'}),
                              frozenset({'CHE 131', 'CHE 133'}), frozenset({'CHE 152', 'CHE 154'}), frozenset({'PHY 126', 'PHY 133'}), 
                              frozenset({'PHY 131', 'PHY 133'}), frozenset({'PHY 141', 'PHY 133'})}

# 8. One additional natural science courses selected from below.
# Note: One may not take science courses that are deemed equivalent to satisfy 7 and 8 (e.g., PHY 125 and PHY 131). Please review course descriptions for more information. 
additional_science_courses = {'AST 203', 'AST 205', 'BIO 201', 'BIO 202', 'BIO 203', 'CHE 131', 'CHE 132', 'CHE 152', 'CHE 321', 
                              'CHE 322', 'CHE 331', 'CHE 332', 'PHY 125', 'PHY 126', 'PHY 127', 'PHY 131', 'PHY 132', 'PHY 142',
                              'PHY 251'} 

# Evaluate requirements 7 and 8 together, to check the average GPA requirement.
# Grading: The grade point average for the courses in Requirements 7 and 8 must be at least 2.00.
def science(taken):
    return any({lec.course,lab.course} in science_lecture_lab_combs and additional.course in additional_science_courses
                and GPA({lec,lab,additional}) >= 2.0 and additional not in {lec,lab}
                for lec in taken for lab in taken for additional in taken)
    
# 9. Required Non-Technical Courses
def non_technical_courses(taken_crs):
    return {'CSE 300', 'CSE 312'} <= taken_crs

# At least 24 credits from items 1 to 3 below, and at least 18 credits from items 2 and 3, must be completed at Stony Brook.
# Note: if a student replaces CSE 114,214,307 with 8 credits of CSE 160,161,260,261, the 3 credits for cse260 are counted as item 2 (replacing the 3 credits for CSE 307), and the rest are counted as item 1; this is done by including CSE 260 in item_2_courses and the other 3 in item_1_courses.
def credits_at_SB(taken):
    taken_at_SB = {c for c in taken if not c.transfer}
    electives_at_SB = electives(taken_at_SB)
    item_1_credits = sum([c.credits for c in taken_at_SB if c.course in item_1_courses])
    items_2_and_3_credits = sum([c.credits for c in taken_at_SB if (c.course in item_2_courses or c in electives_at_SB)])
    return item_1_credits + items_2_and_3_credits >= 24 and items_2_and_3_credits >= 18

# check whether the given student satisfies all degree requirements for BS in CSE
def degree_requirements(student):
    # Grading: All courses taken to satisfy Requirements 1 through 9 must be taken for a letter grade. 
    # The courses in Requirements 1-6, and 9 must be passed with a letter grade of C or higher. 
    taken = {c for c in student.classesTaken if C_or_higher(c.grade)}
    taken_crs = {c.course for c in taken}
    print("required_introductory_courses:", required_introductory_courses(taken_crs))
    print("required_advanced_courses:", required_advanced_courses(taken_crs))
    print("computer_science_electives:", computer_science_electives(taken))
    print("calculus:", calculus(taken_crs))
    print("linear_algebra:", linear_algebra(taken_crs))
    print("statistics:", statistics(taken_crs))
    print("science:", science(taken))
    print("non_technical_courses:", non_technical_courses(taken_crs))
    print("credits_at_SB:", credits_at_SB(taken))
    return (required_introductory_courses(taken_crs)
            and required_advanced_courses(taken_crs)
            and computer_science_electives(taken)
            and calculus(taken_crs)
            and linear_algebra(taken_crs)
            and statistics(taken_crs)
            and science(taken)
            and non_technical_courses(taken_crs)
            and credits_at_SB(taken))

def test():
    classes = {ClassTaken(crs, 4, 'A', False)
               for crs in{'CSE 113','CSE 114', 'CSE 213','CSE 214', 'CSE 220', 'CSE 307', 'CSE 316', 'CSE 320', 
                          'CSE 373', 'CSE 416', 'MAT 131', 'MAT 132', 'AMS 210', 'AMS 310','CSE 300', 'CSE 312',
                          # electives
                          'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',
                          # science
                          'PHY 131', 'PHY 133', 'AST 203'}}
    student = Student(classes)
    print('degree_requirements:', degree_requirements(student))

test()
