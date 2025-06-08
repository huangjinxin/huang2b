from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import models, schemas, database

# 创建数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="幼儿园管理系统")
templates = Jinja2Templates(directory="app/templates")

# 根路由
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 依赖项：获取数据库会话
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 教师相关接口
@app.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = models.Teacher(name=teacher.name, is_external=teacher.is_external)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@app.get("/teachers/", response_model=list[schemas.Teacher])
def list_teachers(db: Session = Depends(get_db)):
    return db.query(models.Teacher).all()

@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).get(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    return teacher

@app.put("/teachers/{teacher_id}", response_model=schemas.Teacher)
def update_teacher(teacher_id: int, teacher: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    db_teacher = db.query(models.Teacher).get(teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    if teacher.name is not None:
        db_teacher.name = teacher.name
    if teacher.is_external is not None:
        db_teacher.is_external = teacher.is_external
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    db_teacher = db.query(models.Teacher).get(teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    db.delete(db_teacher)
    db.commit()
    return {"ok": True}

# 学生相关接口
@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(name=student.name, age=student.age)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=list[schemas.Student])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@app.get("/students/{student_id}", response_model=schemas.Student)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).get(student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if student.name is not None:
        db_student.name = student.name
    if student.age is not None:
        db_student.age = student.age
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).get(student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(db_student)
    db.commit()
    return {"ok": True}

# 课程相关接口
@app.post("/courses/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == course.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    db_course = models.Course(title=course.title, teacher_id=course.teacher_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.get("/courses/", response_model=list[schemas.Course])
def list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@app.get("/courses/{course_id}", response_model=schemas.Course)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course

@app.put("/courses/{course_id}", response_model=schemas.Course)
def update_course(course_id: int, course: schemas.CourseUpdate, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).get(course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if course.title is not None:
        db_course.title = course.title
    if course.teacher_id is not None:
        teacher = db.query(models.Teacher).get(course.teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")
        db_course.teacher_id = course.teacher_id
    db.commit()
    db.refresh(db_course)
    return db_course

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).get(course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="课程不存在")
    db.delete(db_course)
    db.commit()
    return {"ok": True}

# 财务记录接口
@app.post("/finances/", response_model=schemas.FinanceRecord)
def create_finance(record: schemas.FinanceRecordCreate, db: Session = Depends(get_db)):
    db_record = models.FinanceRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/finances/", response_model=list[schemas.FinanceRecord])
def list_finances(db: Session = Depends(get_db)):
    return db.query(models.FinanceRecord).all()

@app.get("/finances/{record_id}", response_model=schemas.FinanceRecord)
def get_finance(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.FinanceRecord).get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record

@app.put("/finances/{record_id}", response_model=schemas.FinanceRecord)
def update_finance(record_id: int, record: schemas.FinanceRecordUpdate, db: Session = Depends(get_db)):
    db_record = db.query(models.FinanceRecord).get(record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    if record.amount is not None:
        db_record.amount = record.amount
    if record.description is not None:
        db_record.description = record.description
    if record.date is not None:
        db_record.date = record.date
    db.commit()
    db.refresh(db_record)
    return db_record

@app.delete("/finances/{record_id}")
def delete_finance(record_id: int, db: Session = Depends(get_db)):
    db_record = db.query(models.FinanceRecord).get(record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(db_record)
    db.commit()
    return {"ok": True}
