# 幼儿园管理系统示例

该仓库提供一个基础的示例，展示如何使用 **FastAPI** 构建幼儿园管理系统的后端，并通过 `docker-compose` 快速启动数据库与服务。

## 快速开始

```bash
# 克隆仓库后，在项目根目录执行

docker compose up
```

首次启动会自动在数据库中创建表，完成后在浏览器访问 `http://localhost:8000` 即可看到简单的 Web 界面，可在页面上管理教师、学生、课程和财务记录。

常用接口示例：

- `POST /teachers/` 新增教师
- `GET /teachers/` 查看教师列表
- `POST /students/` 新增学生
- `GET /students/` 查看学生列表
- `POST /courses/` 新增课程
- `GET /courses/` 查看课程列表
- `POST /finances/` 新增财务记录
- `GET /finances/` 查看财务记录

## 目录结构

- `backend/`：后端代码目录
  - `app/`：FastAPI 应用及模型
  - `requirements.txt`：后端依赖列表
- `docker-compose.yml`：开发环境使用的服务编排文件

## 兼容性

本项目基于 Python 3.11 与 Postgres 15，在 macOS（包括 m 系列芯片）及 Linux 上均可通过 Docker 运行。

## 后续计划

- 添加用户与权限管理
- 接入数据库模型
- 完善课程、财务、后勤等模块
