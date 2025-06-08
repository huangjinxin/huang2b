from datetime import date
from pydantic import BaseModel

class TeacherBase(BaseModel):
    name: str
    is_external: bool = False

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: int

    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    name: str
    age: int

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    title: str
    teacher_id: int

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int

    class Config:
        orm_mode = True

class FinanceRecordBase(BaseModel):
    amount: float
    description: str | None = None
    date: date

class FinanceRecordCreate(FinanceRecordBase):
    pass

class FinanceRecord(FinanceRecordBase):
    id: int

    class Config:
        orm_mode = True
