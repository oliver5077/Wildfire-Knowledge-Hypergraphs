import json
import os
import random
import ast
import pandas as pd
import re
import openai
import time

from sympy.parsing.sympy_parser import null

df_access = [
    ('sk-abcd')
]
df_nert = {
'english': [
        'Emergency Response Tasks: Emergency response behaviours that need to be done before, during, and after a forest fire occurs, which should be specific actions, not a thing, place, person, etc.re.',
        ],
}

#阶段实体抽取
stage_entity_alerts = {
    'english': '''
      I need to ask you to help me extract from a piece of text phase entities related to forest fire emergency response related to phases, phases refer to different stages of the forest fire emergency response process in terms of chronological order and type of events, each phase usually involves a specific set of actions, objectives and tasks and contains multiple fire events.
    I will give you the text that needs to be extracted and the type of stage entity that needs to be extracted. Please extract the corresponding actual entities in the text based on the descriptions of the entity types and match the corresponding descriptive statements from the original text paragraph for each entity based on the entities you have extracted. \n
    The given sentence and its description is: “{}”\n\n
    Stage entity type and its description: {}\n
    The output format is json data, including: entity, entity_type, entity_description three fields.
    Please note, please try to split the original text as entity_description, no need for you to summarize or generate
    Please output them one by one and do not merge them. Other than that, please do not enter any other information. \n
    Please do not output any, if it does not exist
    If the original text is in English, please output the English result.
    The output data should be in strict json format, no matter how many data are in the array
    ''',
    }
#要素实体抽取
element_entity_alerts = {
    'english': '''
     I need to ask you to help me extract from a piece of text the elemental entities related to a forest fire emergency, the elements are the specific fire elements, people, places, elements, etc. involved in a forest fire emergency
    I will give you the text that needs to be extracted and the type of elemental entity that needs to be extracted. Please extract the corresponding actual entities in the text according to the descriptions of the entity types, and match the corresponding descriptive statements from the original text paragraph for each entity according to the entities you have extracted. Please do not generate your own descriptions\n
    The given sentence and its description is: “{}”\n\n
    Element entity type and description: {}\n
    The output format is json data, including: entity, entity_type, entity_description three fields.
    Please output them one by one and do not merge them. Please do not input any other information. Note that please carefully distinguish between elements and events and do not extract event entities. \n
Please note that please try to split the original text as entity_description without you summarizing or generating If it does not exist, please do not output any.
    If the original text is in English, please output the English result.
    The output data should be in strict json format, regardless of how many data items are in the array
    ''',
   }
#事件实体抽取
event_entity_alerts = {
    'english': '''
    I need to ask you to help me extract from a piece of text the entity of an event related to a forest fire emergency, where an event refers to a specific behavior, action, or change in condition that occurs during a forest fire emergency. It contains multiple elements.
    I will give you the text that needs to be extracted and the type of event entity that needs to be extracted. Please extract the actual entities corresponding to the text based on the descriptions of the entity types and match the corresponding description statements from the original text paragraph for each entity based on the entities you have extracted. Please do not generate your own descriptions\n
    The given sentence and its description is: “{}”\n\n
    Event entity type and its description: {}\n
    The output format is json data, including: entity, entity_type, entity_description three fields.
Please note, please try to split the original text as entity_description, no need for you to summarize or generate Please output one by one do not merge. Please do not enter any other information. Note Please carefully distinguish between events and elements and do not extract element entities. \n
    Please do not output any, if they do not exist
    If the original text is in English, please output the result in English.
    The output data should be in strict json format, regardless of how many data are in the array
    ''',
  }
#关系抽取
rel_alerts = {
    'english': '''
    Next we build the relationship between the entities, the relationship we are going to build is a multivariate relationship.
    I will provide you with the text, the list of available entities, and the list of available relationships, and ask you to extract the relationships from the text based on the information I provide. \n
    The given text and its description is: “{}”\n
    The available entities are: {}\n
    Relationship type and its description: {}\n
    The output data is in the data format: (“Relationship Type_Number of Entities”,Entity1,Entity2,... , entity n)
    If the original text is in English, please output the result in English.
    Please do not enter any other information. The relationships are only considered to be strongly correlated.
    If no relationship exists, please do not output any text.
    \n
    # ''',
 }
folder_path = "./KnowledgeSource"
#知识源获取
def read_txt(folder_path,name):
    file_path = os.path.join(folder_path, name)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {file} not found in .data directory.")
        return None
#层级抽取知识源获取
def read_json(folder_path,name):
    file_path = os.path.join(folder_path, name)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # 解析JSON文件
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

#基于LLM的关系抽取
def chat_rel(inda, chatbot,relclass,file_name):
    print("---RE---")
    rel_result = ""
    mess = [{"role": "system",
             "content": "你是一个知识超图构建的专家。"}, ]  # chatgpt对话历史
    sent = inda['sentence']
    lang = inda['lang']
    datajson = read_json("./result", file_name + "_"+relclass+"_entity.json")
    if datajson == null :
        return rel_result, mess
    datas = datajson["nodelist"]
    out = []  # 输出列表 [(e1,r1,e2)]
    try:
        print('---stage1---')
        # 构造prompt
        mess = [{"role": "system",
                 "content": "你是一个知识超图构建的专家，你会根据我所提示的内容，逐步构建一个野火灾害相关的知识图谱。"}, ]  # chatgpt对话历史
        global stList

        sent = inda['sentence']
        lang = inda['lang']

        if relclass == "stage":
            rel_schema = read_txt("./schema", "stage_rel.txt")
            s1p = rel_alerts[lang].format(sent, datas,str(rel_schema))
        elif relclass == "event":
            rel_schema = read_txt("./schema", "event_rel.txt")
            s1p = rel_alerts[lang].format(sent, datas,str(rel_schema))
        elif relclass == "elementary":
            rel_schema = read_txt("./schema", "elementary_rel.txt")
            s1p = rel_alerts[lang].format(sent, datas , str(rel_schema))
        elif relclass == "decision":
            rel_schema = read_txt("./schema", "decision_rel.txt")
            s1p = rel_alerts[lang].format(sent, datas , str(rel_schema))
        # 请求chatgpt
        mess.append({"role": "user", "content": s1p})
        rel_result = chatbot(mess)
        mess.append({"role": "assistant", "content": rel_result})
    except Exception as e:
        print(e)
        print('ner stage 1 none out or error')
        return ['error-stage1:' + str(e)], mess
    return rel_result, mess
#基于LLM的实体抽取
def chat_entity(inda, chatbot,entityClass):
    print("---NER---")
    mess = [{"role": "system",
             "content": "你是一个知识超图构建的专家，你会根据我所提示的内容，逐步构建一个野火灾害相关的知识图谱。"}, ]  # chatgpt对话历史
    global stList
    typelist = df_nert['E']
    sent = inda['sentence']
    lang = inda['lang']
    out = []  # 输出列表 [(e1,et1)]
    json_data = {
        "nodelist": [],
        "nodes": []
    }
    try:
        print('---stage1---')
        # 构造prompt
        stage1_tl = typelist

        if entityClass == "stage":
            stage_entity_schema = read_txt("./schema","stage.txt")
            s1p = stage_entity_alerts[lang].format(sent, str(stage_entity_schema))
        elif entityClass == "event":
            event_entity_schema = read_txt("./schema", "event.txt")
            s1p = event_entity_alerts[lang].format(sent, str(event_entity_schema))
        elif entityClass == "elementary":
            elementary_entity_schema = read_txt("./schema", "elementary.txt")
            s1p = element_entity_alerts[lang].format(sent, str(elementary_entity_schema))
        elif entityClass == "decision":
            elementary_entity_schema = read_txt("./schema", "decision.txt")
            s1p = element_entity_alerts[lang].format(sent, str(elementary_entity_schema))
        # 请求chatgpt
        mess.append({"role": "user", "content": s1p})
        entity_result = chatbot(mess)
        mess.append({"role": "assistant", "content": entity_result})
        data = json.loads(entity_result)

        if(entity_result != null):

            data = json.loads(entity_result)

        # 构建节点列表
            nodelist = [entity["entity"] for entity in data]
            print("stList")
            json_data = {
                "nodelist": nodelist,
                "nodes": data
            }
    except Exception as e:
        print(e)
        print('ner stage 1 none out or error')
        return json_data, mess
    return json_data,mess
def chat(mess):
    openai.api_base = "https://api.pumpkinaigc.online/v1"
    openai.api_key = "sk-QtsRETYpX6lMnU8iE9A81c237f46454bAa5549C047B57359"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=mess
    )
    res = response['choices'][0]['message']['content']
    return res
def chatie(input_data,entityClass,file_name):
    # 参数处理，默认参数
    task = input_data['task']
    lang = input_data['lang']
    typelist = df_nert['english']
    access = input_data['access']
    ## account
    if access == "":
        print('using default access token')
        tempes = random.choice(df_access)
        input_data['access'] = tempes[1] + tempes[0][1:]

    ## chatgpt
    try:
        openai.api_base = "https://api.pumpkinaigc.online/v1"
        openai.api_key = input_data['access']
        chatbot = chat
    except Exception as e:
        print('---chatbot---')
        print(e)
        input_data['result'] = ['error-chatbot']
        return input_data  # 没必要进行下去
    ## typelist, 空或者出错就用默认的
    try:
        typelist = ast.literal_eval(typelist)
        input_data['type'] = typelist
    except Exception as e:
        print('---typelist---')
        print(e)
        print(typelist)
        print('using default typelist')

        if task == 'NER':
            typelist = df_nert[lang]
            input_data['type'] = typelist
    print(time.localtime(time.time()))
    # get output from chatgpt
    input_data['ner_result'], input_data['mess'] = chat_entity(input_data, chatbot,entityClass)
    write_json(input_data['ner_result'], file_name + "_"+entityClass+"_entity.json")
    input_data['re_result'], input_data['mess'] = chat_rel(input_data, chatbot,entityClass,file_name)
    print(time.localtime(time.time()))
    print(input_data)

    return input_data
import json
import os
#json结果文件写入
def write_json(content, file_path):
    """
    将给定的内容写入指定路径的 JSON 文件。如果文件存在，则追加数据；如果文件不存在，则创建并写入数据。

    :param content: 要写入文件的 JSON 数据（Python 字典或列表）
    :param file_path: 文件的路径，包含文件名和扩展名
    """
    output_dir = './StructuredKnowledge/'
    os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
    file_path = os.path.join(output_dir, file_path)
    try:
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 如果文件存在，先读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    # 尝试将文件内容解析为 JSON
                    data = json.load(file)
                    if isinstance(data, dict):
                        # 如果文件已有数据结构，追加新数据
                        if "nodelist" in data:
                            data["nodelist"].extend(content["nodelist"])  # 添加nodelist
                        else:
                            data["nodelist"] = content["nodelist"]

                        if "nodes" in data:
                            data["nodes"].extend(content["nodes"])  # 添加nodes
                        else:
                            data["nodes"] = content["nodes"]
                    else:
                        print(f"Error: The existing file {file_path} does not have the correct format.")
                        return
                except json.JSONDecodeError:
                    print(f"Error: The file {file_path} does not contain valid JSON data.")
                    return
        else:
            # 如果文件不存在，创建新的数据结构
            data = {
                "nodelist": content["nodelist"],  # 传入的nodelist
                "nodes": content["nodes"]  # 传入的nodes
            }

        # 将更新后的数据写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Data successfully written to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

#txt结果文件写入
def write_txt(content, filename):
    output_dir = './StructuredKnowledge/'
    os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
    file_path = os.path.join(output_dir, filename)
    try:
        # 打开文件，如果文件不存在会创建一个新的文件
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(content)  # 写入内容
            file.write('\n')
        print(f"Content successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
#知识获取
def getReturnData(sen):

    global stlistresult
    stlistresult = {
        "nodelist": [],
        "nodes": []
    }
    # global tir
    tir = ''
    directoryData = './data'
    directoryResult = './result'
    file_names = [f for f in os.listdir(directoryData) if os.path.isfile(os.path.join(directoryData, f))]
    for file_name in file_names:
    # 阶段知识抽取
        data = read_txt(directoryData,file_name)
        ind = {
            "sentence": data,
            "type": "",
            "access": "sk-cz27DCphBGqE4BR0B7444272171f479a8fD22d72753b66D0",
            "task": "",
            "lang": "english",
            'ner_result': {},
            're_result': [],
        }
        post_data = chatie(ind,"event",file_name)
        write_txt(post_data['re_result'],file_name+"_event_rel.txt")
        # 要素知识抽取
        datajson = read_json(directoryResult, file_name + "_event_entity.json")
        datas = datajson["nodes"]
        for data in datas:
            ind = {
                "sentence": data["entity_description"],
                "type": "",
                "access": "sk-cz27DCphBGqE4BR0B7444272171f479a8fD22d72753b66D0",
                "task": "",
                "lang": "english",
                'ner_result': [],
                're_result': [],
            }
            post_data = chatie(ind, "elementary",file_name)
            nodelist = datajson["nodelist"]
            nownodes = read_json(directoryResult, file_name + "_elementary_entity.json")["nodelist"]
            renode = data["entity"]
            nodelist_length = len(nownodes)
            # 构造最终的字符串
            result_string = f"{{'Component'_{nodelist_length}, {renode}, {', '.join([repr(item) for item in nownodes])}}}"
            write_txt(result_string, file_name + "_elementary_rel.txt")
            write_txt(post_data['re_result'], file_name + "_elementary_rel.txt")

    return post_data['ner_result'], post_data['re_result']

if __name__=="__main__":

    getReturnData("")
