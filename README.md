# RateKeeper - 汇率数据获取与管理工具

'RateKeeper' 是一个简单易用的汇率数据获取与管理工具，它可以从'ShowAPI'获取实时汇率数据，并将其存储在本地SQLite数据库中，方便后续查询和使用。

## 功能特点

- 支持从ShowAPI获取主流货币汇率
- 数据本地化存储，避免频繁请求API
- 自动去重，避免存储重复数据
- 简单易用的API接口

## 安装与依赖
### 配置
创建.env文件，添加你的ShowAPI密钥：

    SHOWAPI_APPKEY=your_real_key

将.env文件放置在项目根目录
注意：如果没有配置SHOWAPI_APPKEY，程序会抛出RuntimeError异常

### 快速开始
#### 初始化数据库

    from ratekeeper import initialize
    initialize()

#### 更新汇率数据

    from ratekeeper import update

#### 更新USD和EUR的汇率
    update(["USD", "EUR"])

#### 默认更新USD和EUR
项目结构

    ratekeeper/
    ├── __init__.py           # 包初始化
    ├── application/          # 应用服务层（对外服务封装）
    │   ├── __init__.py
    │   └── update_service.py # 汇率更新服务实现
    ├── domain/               # 领域模型层
    │   ├── __init__.py
    │   └── models.py         # 领域模型定义
    ├── infrastructure/       # 基础设施层
    │   ├── __init__.py
    │   ├── db.py             # 数据库访问
    │   └── showapi_client.py # ShowAPI客户端
    ├── config.py             # 配置管理
    └── rates.py              # 对外统一接口

#### 数据存储

数据库存储位置(Windows系统)

    %LOCALAPPDATA%\ratekeeper\ratekeeper.db

日志文件

    %LOCALAPPDATA%\ratekeeper\ratekeeper_update.log

#### 初始化（首次使用时调用一次）
    from ratekeeper import initialize
    initialize()

#### 更新汇率数据
    from ratekeeper import update
    update(["USD", "EUR", "JPY", "GBP"])