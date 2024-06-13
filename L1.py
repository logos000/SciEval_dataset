import os
import openai
import json
import re
import random

# 初始化OpenAI客户端
client = openai.OpenAI(
    api_key="",
    base_url=''
)

# 定义一个函数来提取有用的信息
def extract_useful_information(content):
    system_message = (
        "Analyze the following text to determine if it contains useful knowledge or "
        "information about material science. If it does, reorganize the information into a coherent and logically "
        "structured paragraph, maintaining the original meaning of the text, and directly "
        "return the coherent and logically structured paragraph. Don't return anything "
        "useless. If the text does not contain useful knowledge or information, return 'False'."
    )
    user_message = f"The text to be analyzed is: '{content}'"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    result = response.choices[0].message.content
    return result

# 定义一个函数来生成选择题
def generate_mcq(content):
    system_message = (
        "You are a brilliant assistant."
    )
    user_message = (
        "Please create a multiple choice question (MCQ) that is closely related to the "
        "domain professional knowledge in provided <text>. Ensure that the correct option "
        "of the MCQ can be found in <text>. Your created <question> should include 4 "
        "multiple choice options, as the following format: "
        "{ "
        "\"question\": \"the question\", "
        "\"options\": {"
        " \"correct_option\": \"the correct option that can be found in <text>\","
        " \"wrong_option_1\":\"the wrong option 1\", "
        " \"wrong_option_2\":\"the wrong option 2\", "
        " \"wrong_option_3\":\"the wrong option 3\", "
        "} "
        "} "
        "Output in this format in JSON. "
        "You should incorporate specific scenarios or contexts in the <question>, allowing the professional knowledge in <text> to serve as a comprehensive and "
        "precise answer. Ensure that the question is formulated in English language. "
        "The <question> is a close-book question that is used to evaluate human experts, please ensure the difficulty of the <question> is really challenging and has no "
        "dependence on <text>, that is, please pay more attention to the professional "
        "information of the field rather than the methods designed in <text>. "
        "Most importantly, the correct answer of the <question> must can be found in "
        "<text>. "
        "<text>: "
        f"{content}"
        "# Question: "
        "Again, DO NOT let your questions focus on information that relies on text, DO NOT show text in your question. Now "
        "create the challenging multiple choice <question>: "
        "<question>:"
    )

    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_object"
    },
    )
    result = response.choices[0].message.content
    #return result
    return json.loads(result)

# 定义一个函数来生成选择题答案
#def generate_mcq_answer(mcq, content):
#    system_message = (
#        "Given a question and four options, please select the right answer. "
#        "Your answer should be 'A', 'B', 'C' or 'D'. Please directly give the answer without any explanation. "
#        "Do not include any other text, just the single letter answer."
#    )
#    user_message = f"Question: {mcq}\n\nContent: {content}"
#    
#    response = client.chat.completions.create(
#        model="gpt-3.5-turbo",
#        messages=[
#            {"role": "system", "content": system_message},
#            {"role": "user", "content": user_message}
#        ]
#    )
#    result = response.choices[0].message.content
#    # 后处理
#    if result not in ['A', 'B', 'C', 'D']:
#        result = re.search(r'[A-D]', result)
#        if result:
#            return result.group(0)
#        else:
#            raise ValueError(f"Invalid answer: {result}")
#    
#    return result

# 定义一个函数将内容分成若干部分
def split_content(content, max_length=1024):
    paragraphs = content.split('\n\n')
    parts = []
    current_part = ''
    current_length = 0

    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        for line in lines:
            if current_length + len(line) <= max_length:
                current_part += line + '\n'
                current_length += len(line)
            else:
                parts.append(current_part.strip())
                current_part = line + '\n'
                current_length = len(line)
        current_part += '\n'  # 添加段落之间的空行

    if current_part.strip():
        parts.append(current_part.strip())
    
    return parts


# 定义一个函数从mmd文件中提取文本
def extract_text_from_mmd(mmd_path):
    with open(mmd_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


# 读取文件夹中的所有MMD文件
folder_path = r"D:\AAMy_program\test\AutoQuestion"  # 替换为你的文件夹路径

def save_questions_and_answers(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 存储所有问题和回答的列表
all_questions_and_answers = []

# 遍历文件夹中的每个MMD文件
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path) and filename.lower().endswith('.mmd'):  # 确保是MMD文件
        
        content = extract_text_from_mmd(file_path)
        #print(content)
        parts = split_content(content)
        question_count = 0  # 初始化计数器
        for i, part in enumerate(parts):
            try:    
                if question_count >= 6:
                    break  # 如果问题数量达到6个，停止生成
                print(f"正在处理文件: {file_path} 的第 {i+1} 部分")
                #print(part)
                useful_info = extract_useful_information(part)
                if useful_info != 'False':
                    print(f"有用的信息提取自文件: {file_path} 的第 {i+1} 部分")
                    print(useful_info)
                    mcq_question_data = generate_mcq(useful_info)
                    mcq_question = mcq_question_data["question"]
                    print(f"生成的选择题: {mcq_question}\n")
                    choice_raw = mcq_question_data["options"]
                    choices_text = list(mcq_question_data["options"].values())  # 只保存冒号后的選項
                    random.shuffle(choices_text)
                    choices_label = ["A", "B", "C", "D"]
                    print(f"原始的选项: {choice_raw}\n")
                    print(f"生成的选项: {choices_text}\n")
                    mcq_answer = mcq_question_data["options"]["correct_option"]
                    correct_choice = choices_label[choices_text.index(mcq_answer)]
                    print(f"生成的答案: {correct_choice}\n")
                    
                    question_and_answer = {
                                "prompt": {"default": "Given a question and four options, please select the right answer. Your answer should be \"A\", \"B\", \"C\" or \"D\". Please directly give the answer without any explanation."},
                                "question": mcq_question,
                                "choices": {"text": choices_text, "label": choices_label},
                                "answerKey": correct_choice,
                                "type": "mcq-4-choices",
                                "domain": "Material",
                                "details": {
                                    "level": "L1",
                                    "task": "literature_multi_choice_question",
                                    "subtask": "MaterialRxiv_QA",
                                    "source": "MaterialRxiv"
                                }
                            }

                    all_questions_and_answers.append(question_and_answer)
                    question_count += 1  # 增加计数器
                    #all_questions_and_answers.append({"question": mcq_question, "answer": mcq_answer,"category": "materials science", "type": "multiple-choice"})
                else:
                    print(f"文件 {file_path} 的第 {i+1} 部分中没有有用的信息")
            except Exception as e:
                print(f"读取文件 {file_path}第 {i+1} 部分 时出错: {e}")

# 将所有问题和回答保存到文件
save_questions_and_answers("all_questions_answers.json", all_questions_and_answers)

print("所有文件处理完成。")
