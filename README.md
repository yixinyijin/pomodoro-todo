# Pomodoro Todo - 番茄时钟 + 待办事项

一个结合番茄工作法和待办事项管理的跨平台桌面应用。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 功能特性

### 番茄时钟模块
- 标准番茄钟 (25分钟工作 + 5分钟休息)
- 长休息模式 (15分钟)
- 自定义时长设置
- 计时器倒计时显示
- 系统通知/托盘图标提醒
- 番茄完成统计
- 声音提醒

### 待办事项模块
- 创建/编辑/删除任务
- 设置任务标题、描述
- 优先级设置 (高/中/低)
- 状态管理 (待办/进行中/已完成)
- 按状态筛选
- 番茄钟关联 (为任务计时)

### 数据管理
- SQLite 本地数据库存储
- 数据导出 (JSON格式)
- 主题切换 (浅色/深色)

## 界面预览

```
┌─────────────────────────────────────────┐
│  [ 番茄时钟 ]          [ 待办事项 ]      │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────┐ │
│  │             │    │ [+ 新建任务]     │ │
│  │   25:00     │    │ ├─ 任务1  [高]  │ │
│  │             │    │ │  [▶ 开始]      │ │
│  │  [▶ 开始]   │    │ ├─ 任务2  [中]  │ │
│  │  [⏸ 暂停]   │    │ │  [▶ 开始]      │ │
│  │  [↺ 重置]   │    │ └─ 任务3  [低]  │ │
│  │             │    │  ...            │ │
│  └─────────────┘    └─────────────────┘ │
│                                         │
│  今日完成: 4 个番茄钟    累计: 32:15     │
└─────────────────────────────────────────┘
```

## 安装

### 环境要求
- Python 3.9+
- PyQt6

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/你的用户名/pomodoro-todo.git
cd pomodoro-todo
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 使用说明

### 番茄时钟
1. 点击"开始"按钮启动计时器
2. 工作25分钟后会自动提醒
3. 可选择短休息(5分钟)或长休息(15分钟)
4. 暂停后可继续，重置可重新开始

### 待办事项
1. 在输入框输入任务标题
2. 选择优先级
3. 点击"添加任务"
4. 点击任务可查看详情、开始或完成

### 快捷键
| 快捷键 | 功能 |
|--------|------|
| `Ctrl + T` | 切换主题 |
| `Ctrl + Q` | 退出应用 |

## 项目结构

```
pomodoro_todo/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖
├── core/                   # 核心模块
│   ├── database.py         # 数据库操作
│   ├── pomodoro.py         # 番茄时钟逻辑
│   └── todo_manager.py     # 待办事项管理
├── ui/                     # 界面模块
│   ├── main_window.py      # 主窗口
│   ├── pomodoro_widget.py  # 番茄时钟组件
│   ├── todo_widget.py      # 待办列表组件
│   └── styles.py           # 样式主题
├── models/                 # 数据模型
│   ├── pomodoro_models.py  # 番茄数据模型
│   └── todo_models.py      # 待办数据模型
└── data/                   # 数据存储
    └── app.db              # SQLite数据库
```

## 数据库设计

### tasks 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | TEXT | 任务标题 |
| description | TEXT | 任务描述 |
| priority | INTEGER | 优先级 (1:高, 2:中, 3:低) |
| status | INTEGER | 状态 (0:待办, 1:进行中, 2:已完成) |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### pomodoros 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 关联任务ID |
| duration | INTEGER | 专注时长(秒) |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |

## 后续扩展

- [ ] 数据统计图表
- [ ] 多标签页/分类
- [ ] 快捷键支持
- [ ] 数据导出 CSV 格式
- [ ] 番茄历史记录查看

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
