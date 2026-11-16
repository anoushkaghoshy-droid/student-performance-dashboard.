"""
StudentRecord Module
====================
Provides encapsulation, validation, and letter grade conversion for student
assessment records.

Design:
- is_valid_score(): Validates whether an assessment score lies in [0, 100].
- score_to_grade(): Maps numerical marks into standard letter grades (A, B, C, D, F).
- StudentRecord: Encapsulates student identifier, course name, weekly study hours,
  score, and derived grade with strict validation.
"""

from typing import Any, Dict


def is_valid_score(score: Any) -> bool:
    """Check if the given score is a numeric value within [0, 100]."""
    try:
        val = float(score)
        return 0.0 <= val <= 100.0
    except (ValueError, TypeError):
        return False


def score_to_grade(score: Any) -> str:
    """
    Convert a numerical score to a letter grade based on standard institutional thresholds:
    - A: 70 - 100
    - B: 60 to below 70
    - C: 50 to below 60
    - D: 40 to below 50
    - F: below 40

    Raises:
        ValueError: If score is non-numeric or outside [0, 100].
    """
    if not is_valid_score(score):
        raise ValueError(f"Invalid score: {score}. Score must be a numeric value between 0 and 100.")
    
    val = float(score)
    if val >= 70.0:
        return 'A'
    elif val >= 60.0:
        return 'B'
    elif val >= 50.0:
        return 'C'
    elif val >= 40.0:
        return 'D'
    else:
        return 'F'


class StudentRecord:
    """
    Encapsulates student assessment details, weekly study hours, and letter grade.
    
    Attributes:
        student_id (str): Anonymised student identifier (e.g., 'S001').
        course (str): Subject or programme label (e.g., 'Computing', 'Maths').
        study_hours (float): Self-reported weekly study hours (0.0 to 168.0).
        score (float): Assessment score (0.0 to 100.0).
        grade (str): Derived letter grade ('A', 'B', 'C', 'D', 'F').
    """

    def __init__(self, student_id: str, course: str, study_hours: float, score: float):
        # Validate student_id
        if not isinstance(student_id, str) or not student_id.strip():
            raise ValueError(f"Invalid student_id: '{student_id}'. Identifier must be a non-empty string.")
        
        # Validate course
        if not isinstance(course, str) or not course.strip():
            raise ValueError(f"Invalid course: '{course}'. Course must be a non-empty string.")
        
        # Validate study_hours (0 to 168 hours in a 7-day week)
        try:
            hours_val = float(study_hours)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid study_hours: '{study_hours}'. Must be numeric.")
        if not (0.0 <= hours_val <= 168.0):
            raise ValueError(f"Invalid study_hours: {hours_val}. Must be between 0 and 168 hours/week.")
            
        # Validate score
        if not is_valid_score(score):
            raise ValueError(f"Invalid score: '{score}'. Must be a numeric value between 0 and 100.")
        score_val = float(score)

        self.student_id = student_id.strip()
        self.course = course.strip()
        self.study_hours = hours_val
        self.score = score_val
        self.grade = score_to_grade(self.score)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentRecord":
        """
        Factory method to instantiate a StudentRecord from a dictionary (e.g., CSV row).
        Required keys: student_id, course, study_hours, score.
        """
        required_keys = ("student_id", "course", "study_hours", "score")
        for k in required_keys:
            if k not in data or data[k] is None or str(data[k]).strip() == "":
                raise ValueError(f"Missing required field '{k}' in record data: {data}")
        
        return cls(
            student_id=str(data["student_id"]),
            course=str(data["course"]),
            study_hours=float(data["study_hours"]),
            score=float(data["score"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the StudentRecord instance into a dictionary."""
        return {
            "student_id": self.student_id,
            "course": self.course,
            "study_hours": self.study_hours,
            "score": self.score,
            "grade": self.grade,
        }

    def __repr__(self) -> str:
        return (
            f"StudentRecord(id='{self.student_id}', course='{self.course}', "
            f"study_hours={self.study_hours:.1f}, score={self.score:.1f}, grade='{self.grade}')"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StudentRecord):
            return False
        return (
            self.student_id == other.student_id and
            self.course == other.course and
            abs(self.study_hours - other.study_hours) < 1e-5 and
            abs(self.score - other.score) < 1e-5 and
            self.grade == other.grade
        )
