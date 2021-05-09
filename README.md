# CV Server

> 🔧 | Group @Water Manager

## Summery

本仓库为[Water Manager项目](https://github.com/Water-Mngr)的后端代码仓库

## Structure

- modules // 存放本项目中的CV处理模块
  - plant_id // 植物种类识别模块，源自[开源项目](https://github.com/quarrying/quarrying-plant-id/)
- templates // html模板，便于后端可视化校验正确性
- app.py // flask app
- requirements.txt python模块需求文件
- gunicorn.conf.py | Dockerfile 项目部署配置文件

## Tech Stack

- flask
- opencv
- gunicorn gevent
- Docker

## Usage

You can visit <http://kuqiochi.cn:5000>.

More Details see [API](api.md)
