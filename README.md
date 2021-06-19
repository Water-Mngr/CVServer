<!--
 * @Copyrights: ©2021 @Laffery
 * @Date: 2021-05-07 17:31:14
 * @LastEditor: Laffery
 * @LastEditTime: 2021-06-19 16:03:18
-->
# CV Server

> 🔧 | Group @Water Manager

## Summery

本仓库为[Water Manager项目](https://github.com/Water-Mngr)的后端代码仓库

## Structure

- modules // 存放本项目中的CV处理模块
  - plant_id // 植物种类识别模块，源自[开源项目](https://github.com/quarrying/quarrying-plant-id/)
  - plant_cmp // 本项目开发的植物对比模块，对于两张图片，分析是否属于同一盆栽
  - plant_crawler // 本项目开发的植物抓手模块，用于抓取植物信息
  - plant_detect // 本项目开发的植物异常检测模块，用于检测植物是否存在异常
- templates // html模板，便于后端可视化校验正确性
- app.py // flask app
- requirements.txt python模块需求文件
- gunicorn.conf.py | Dockerfile 项目部署配置文件

## Water Model

植物的浇水模型构建：

植物具有以下参数，分别有若干等级

| 属性 | -1 | 0 | 1 |
| - | - | - | - |
| 温度 | 喜阴 | 默认 | 喜阳 |
| 水分 | 喜旱 | 默认 | 喜湿 |

对于每一个植物，有一个距离下一次浇水的时间$t$，当$t \le 0$时，认为需要浇水。我们认为喜湿的的植物$t=2$，喜旱的植物$t=7$，默认植物$t=4$

我们根据当日的天气

- 如果是高温，喜阴植物浇水时间缩短2天，一般植物浇水时间缩短1天，喜阳植物浇水时间不变
- 如果是大雨，喜旱植物浇水时间延长5天，一般植物浇水时间延长3天，喜湿植物浇水时间延长2天
- 如果是中雨，喜旱植物浇水时间延长4天，一般植物浇水时间延长2天，喜湿植物浇水时间延长1天
- 如果是小雨，喜旱植物浇水时间延长3天，一般植物浇水时间延长1天，喜湿植物浇水时间不变

需要注意用户并不是每天都向后端发送请求，所以我们需要记录历史天气情况进行 预测，使用`flask-apschedule`模块实现定时任务

## Tech Stack

- flask
- opencv
- gunicorn gevent
- Docker

## Usage

You can visit <http://kuqiochi.cn:5000>.

More Details see [API](api.md)
