import os
import fitz  # PyMuPDF
import openai
import json
import random

# 初始化OpenAI客户端
client = openai.OpenAI(
    api_key="",
    base_url='https://api.ai-gaochao.cn/v1'
)

# 定义一个函数来提取有用的信息
def extract_useful_information(content):
    system_message = (
        "Analyze the following text to determine if it contains useful knowledge or "
        "information. If it does, reorganize the information into a coherent and logically "
        "structured paragraph, maintaining the original meaning of the text, and directly "
        "return the coherent and logically structured paragraph. Don’t return anything "
        "useless. If the text does not contain useful knowledge or information, return 'False'."
    )
    user_message = f"The text to be analyzed is: '{content}'"
    
    response = client.chat.completions.create(
        model="gpt-4o",
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
        "[format]: "
        "{ "
        "'question': 'the question', "
        "'options': {"
        "'A': 'option A', "
        "'B': 'option B', "
        "'C': 'option C', "
        "'D': 'option D' "
        "}, "
        #"'correct_option': 'The letter of the correct option' "
        "} "
        "Output in this format in JSON. "
        "You should incorporate specific scenarios or contexts in the <question>, allowing the professional knowledge in <text> to serve as a comprehensive and "
        "precise answer. Ensure that the <question> is formulated in English language. "
        "The <question> is a close-book question that is used to evaluate human experts, please ensure the difficulty of the <question> is really challenging and has no "
        "dependence on <text>, that is, please pay more attention to the professional "
        "information of the field rather than the methods designed in <text>. "
        "Most importantly, the correct answer of the <question> must can be found in "
        "<text>. "
        "<text>: "
        f"{content}"
        "# Question: "
        "Again, DO NOT let your questions focus on information that relies on <text>. Now "
        "create the challenging multiple choice <question>: "
        "<question>:"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    result = response.choices[0].message.content
    result = result.replace("json", "")
    return result

# 定义一个函数来生成选择题答案
def generate_mcq_answer(mcq, content):
    system_message = (
        "Provide a detailed and accurate answer to the following question based on the provided text snippet. "
        "First, indicate the correct option (A, B, C, or D), then provide a detailed explanation. "
        "Output the answer in the following format: "
        "{ "
        "'correct_option': 'A', "
        "'explanation': 'The detailed explanation here.' "
        "}"
    )
    user_message = f"Question: {mcq}\n\nContent: {content}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    result = response.choices[0].message.content
    result = result.replace("json", "")
    return result

# 定义一个函数将内容分成若干部分
def split_content(content, max_length=1000):
    paragraphs = content.split('\n\n')
    parts = []
    current_part = []
    current_length = 0

    for paragraph in paragraphs:
        if current_length + len(paragraph) <= max_length:
            current_part.append(paragraph)
            current_length += len(paragraph)
        else:
            parts.append('\n\n'.join(current_part))
            current_part = [paragraph]
            current_length = len(paragraph)
    if current_part:
        parts.append('\n\n'.join(current_part))
    
    return parts

# 定义一个函数从PDF文件中提取文本
def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# 读取文件夹中的所有PDF文件
folder_path = r"D:\AAMy_program\test\AutoQuestion\ref"  # 替换为你的文件夹路径

def save_questions_and_answers(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 存储所有问题和回答的列表
all_questions_and_answers = []

# 遍历文件夹中的每个PDF文件
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):  # 确保是PDF文件
        try:
            content = extract_text_from_pdf(file_path)
            parts = split_content(content)
            for i, part in enumerate(parts):
                print(f"正在处理文件: {file_path} 的第 {i+1} 部分")
                useful_info = extract_useful_information(part)
                if useful_info != 'False':
                    print(f"有用的信息提取自文件: {file_path} 的第 {i+1} 部分")
                    print(useful_info)
                    mcq_question = generate_mcq(useful_info)
                    print(f"生成的选择题: {mcq_question}\n")
                    mcq_answer = generate_mcq_answer(mcq_question, useful_info)
                    print(f"生成的答案: {mcq_answer}\n")
                    all_questions_and_answers.append({"question": mcq_question, "answer": mcq_answer,"category": "materials science", "type": "multiple-choice"})
                else:
                    print(f"文件 {file_path} 的第 {i+1} 部分中没有有用的信息")
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")

# 将所有问题和回答保存到文件
save_questions_and_answers("all_questions_answers.json", all_questions_and_answers)

print("所有文件处理完成。")
