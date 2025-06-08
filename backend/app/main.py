from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, database

# 创建数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="幼儿园管理系统")

# 根路由
@app.get("/")
def read_root():
    return {"message": "欢迎使用幼儿园管理系统"}

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
