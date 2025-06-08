from datetime import date
from pydantic import BaseModel

class TeacherBase(BaseModel):
    name: str
    is_external: bool = False

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    name: str | None = None
    is_external: bool | None = None

class Teacher(TeacherBase):
    id: int

    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    name: str
    age: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: str | None = None
    age: int | None = None

class Student(StudentBase):
    id: int

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    title: str
    teacher_id: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: str | None = None
    teacher_id: int | None = None

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

class FinanceRecordUpdate(BaseModel):
    amount: float | None = None
    description: str | None = None
    date: date | None = None

class FinanceRecord(FinanceRecordBase):
    id: int

    class Config:
        orm_mode = True
