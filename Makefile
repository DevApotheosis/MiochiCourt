.PHONY: all build clean run install help

all: help

build:
	@echo "正在构建项目..."
	@python build.py

clean:
	@echo "正在清理构建产物..."
	@if exist "dist" rmdir /s /q "dist"
	@if exist "build" rmdir /s /q "build"
	@if exist "spec" rmdir /s /q "spec"
	@echo "清理完成"

run:
	@echo "正在运行游戏..."
	@python run.py

install:
	@echo "正在安装依赖..."
	@pip install pillow requests
	@echo "依赖安装完成"

help:
	@echo "澪地审判庭 - 项目构建命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make build        - 构建可执行文件"
	@echo "  make clean        - 清理构建产物"
	@echo "  make run          - 运行游戏"
	@echo "  make install      - 安装依赖"
	@echo "  make help         - 显示帮助信息"
	@echo ""