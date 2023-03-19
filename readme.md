# 中文医疗问答系统

## 预览
![image-20230319192224207](https://github.com/Jezemy/MASystem/blob/main/assets/image-20230319192224207.png)

![image-20230319192207463](https://github.com/Jezemy/MASystem/blob/main/assets/image-20230319192207463.png)

## 介绍

本项目为本人的本科毕业设计，基于知识图谱的中文医疗问答系统，通过爬虫工具从公开的医疗网站获取医疗知识并利用Neo4j图数据库构建知识图谱。问句意图利用Fasttext文本分类算法识别，并简单编写了一个槽位记忆功能辅助记住上下文信息，最后利用Django框架搭建了一个简单的前端对话界面。

## 使用步骤

### 1. 下载本项目并安装必备环境依赖

### 必备

- JDK 15以上
- Neo4j 4.2.1
- Python3.6以上
- Django 2.1.7
- jieba 0.42.1
- fasttext 0.9.2
- py2neo 2020.1.1

### 爬虫相关

- requests 2.25.1 
- lxml 4.3.0
- retrying 1.3.3
- vthread 0.1.1
- cchardet 2.1.7

### 其他

- pyTelegramBotAPI 3.7.4 （用于连接TelegramBot）

### 2. 安装Neo4j数据库

[Neo4j安装教程](https://blog.csdn.net/qq_38335648/article/details/115027676)

### 3. 还原Neo4j数据

点击[医疗知识图谱数据](链接：https://pan.baidu.com/s/1UculLeRm7-9g7K7t7VtPtQ)下载数据，提取码：a04c

下载后执行下面的命令进行数据还原

```shell
# 如果没有把neo4j的命令加进环境变量，请到neo4j的安装目录下的bin文件中执行
# 假设neo4j.dum的路径是:G:/dump/neo4j.dump
# neo4j数据库的名称是graph

neo4j-admin load --from=G:/dump/neo4j.dump --database=graph.db --force
```



### 4. 修改用户名密码

打开项目中的contextual/KGQuery.py文件，修改连接的用户名和密码

![image-20230319200606840](https://github.com/Jezemy/MASystem/blob/main/assets/image-20230319200606840.png)

### 5. 启动Neo4j服务

```shell
# 在命令行中启动Neo4j
neo4j.bat console
```

### 6. 启动Django服务访问默认地址

```Shell
# 定位到MASystem目录下，执行manage.py
python manage.py runserver
```

### Telegram Bot说明

TelegramBot需要到官网申请创建机器人，并将生成的Token复制到telegramBot.py的Token变量即可运行。

## 项目模块

![image-20230319192131382](https://github.com/Jezemy/MASystem/blob/main/assets/image-20230319192131382.png)

## 代码文件结构

主要代码存放在MASystem文件夹中

- Crawler 爬虫代码以及爬取到的医疗信息
  - dict 实体字典列表
  - entities 爬取的所有数据，整理成json格式
  - build_dict.py 从爬取后的数据中提取实体字典
  - buIld_graph.py 依靠爬取的数据连接neo4j构建知识图谱
  -  request_disease.py 爬取疾病分类数据
  - request_others.py 爬取其他分类数据
- classifier 意图分类器相关代码
  - dict 部分意图语料和实体字典
  - intent 意图语料
  - models 存储训练好的模型
  - fasttext_data.txt Fasttext库能够识别的语料
  - intent.txt 所有意图的举例解释文件
  - stopwords.txt 停用词语料
  - train_intents_fasttext.py 训练Fasttext分类器的代码
  - vocabs.txt 训练Fasttext过程中留下的字典，不重要
  - word2vec-test.py 采用word2vec的尝试，不重要
- contextual 处理上下文信息的代码
  - IntentDetector.py 调用模型识别意图代码
  - IntentProcessor.py 记忆上下文实体，处理对应意图的回复
  - KGQuery.py 提供从图数据库查询的各类方法
- telegramBot.py 支持机器人在telegram上运行的相关代码
- static中存放网页相关的静态文件
- 其他文件均为 Django框架生成或依赖的文件

### 
