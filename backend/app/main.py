from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import models, schemas, database

# 创建数据库表
models.Base.metadata.create_all(bind=database.engine)

def init_admin():
    db = database.SessionLocal()
    try:
        if not db.query(models.User).filter_by(username="admin").first():
            admin = models.User(username="admin", hashed_password=get_password_hash("admin"), role="admin")
            db.add(admin)
            db.commit()
    finally:
        db.close()

app = FastAPI(title="幼儿园管理系统")
app.add_middleware(SessionMiddleware, secret_key="very-secret")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="app/templates")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

init_admin()

# 根路由
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "用户名或密码错误"}, status_code=400)
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    return RedirectResponse(url="/", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# 依赖项：获取数据库会话
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return user

# 教师相关接口
@app.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(
    teacher: schemas.TeacherCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_teacher = models.Teacher(name=teacher.name, is_external=teacher.is_external)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@app.get("/teachers/", response_model=list[schemas.Teacher])
def list_teachers(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return db.query(models.Teacher).all()

@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    teacher = db.query(models.Teacher).get(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    return teacher

@app.put("/teachers/{teacher_id}", response_model=schemas.Teacher)
def update_teacher(
    teacher_id: int,
    teacher: schemas.TeacherUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
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
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_teacher = db.query(models.Teacher).get(teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    db.delete(db_teacher)
    db.commit()
    return {"ok": True}

# 学生相关接口
@app.post("/students/", response_model=schemas.Student)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_student = models.Student(name=student.name, age=student.age)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=list[schemas.Student])
def list_students(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return db.query(models.Student).all()

@app.get("/students/{student_id}", response_model=schemas.Student)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    student = db.query(models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(
    student_id: int,
    student: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
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
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_student = db.query(models.Student).get(student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(db_student)
    db.commit()
    return {"ok": True}

# 课程相关接口
@app.post("/courses/", response_model=schemas.Course)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == course.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    db_course = models.Course(title=course.title, teacher_id=course.teacher_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.get("/courses/", response_model=list[schemas.Course])
def list_courses(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return db.query(models.Course).all()

@app.get("/courses/{course_id}", response_model=schemas.Course)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course

@app.put("/courses/{course_id}", response_model=schemas.Course)
def update_course(
    course_id: int,
    course: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
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
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_course = db.query(models.Course).get(course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="课程不存在")
    db.delete(db_course)
    db.commit()
    return {"ok": True}

# 财务记录接口
@app.post("/finances/", response_model=schemas.FinanceRecord)
def create_finance(
    record: schemas.FinanceRecordCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_record = models.FinanceRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/finances/", response_model=list[schemas.FinanceRecord])
def list_finances(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return db.query(models.FinanceRecord).all()

@app.get("/finances/{record_id}", response_model=schemas.FinanceRecord)
def get_finance(
    record_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    record = db.query(models.FinanceRecord).get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record

@app.put("/finances/{record_id}", response_model=schemas.FinanceRecord)
def update_finance(
    record_id: int,
    record: schemas.FinanceRecordUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
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
def delete_finance(
    record_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_record = db.query(models.FinanceRecord).get(record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(db_record)
    db.commit()
    return {"ok": True}

# 用户管理接口（仅管理员可用）

@app.post("/users/", response_model=schemas.User)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    if db.query(models.User).filter_by(username=user_in.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    db_user = models.User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=list[schemas.User])
def list_users(
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    return db.query(models.User).all()


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    db_user = db.query(models.User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user_update.username is not None:
        db_user.username = user_update.username
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)
    if user_update.role is not None:
        db_user.role = user_update.role
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    db_user = db.query(models.User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(db_user)
    db.commit()
    return {"ok": True}
