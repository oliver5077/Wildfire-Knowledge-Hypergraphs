项目概述
本项目实现从文本知识到知识超图的自动化构建流程，包含知识抽取、超图生成和可视化分析三个核心模块。

项目结构
├── KnowledgeSource/                   # 原始文本知识库
│   └── *.txt                          # 文本源文件
├── StructuredKnowledgeJSON/           # JSON格式结构化知识
│   ├── StructuredKnowledgeTxt/        # TXT格式结构化知识  
│   └── KnowledgeHypergraphs/          # 生成的知识超图
├── accessKnowledge.py                 # 知识抽取模块
├── generateKH.py                      # 超图生成模块
└──  visualization.py                  # 可视化分析模块

1. 知识抽取模块 (accessKnowledge.py)
从KnowledgeSource/的txt文件中抽取：
实体识别（命名实体、概念实体等）
关系抽取（实体间的语义关系）
2. 超图生成模块 (generateKH.py)
generateKH.py用于从StructuredKnowledgeTxt文件夹中的结构化知识中生成json格式的知识超图
3. 
3. 可视化分析模块 (visualization.py)
visualization.py用于将KnowledgeHypergraphs文件夹中的知识超图进行可视化以及定量化分析
