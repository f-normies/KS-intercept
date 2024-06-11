from mitmproxy import http
from bs4 import BeautifulSoup
import json
import os

questions_list = []

def response(flow: http.HTTPFlow) -> None:
    if flow.request.pretty_url == "https://ks2.rsmu.ru/tests2/questions":
        response_text = flow.response.text

        soup = BeautifulSoup(response_text, 'html.parser')
        questions_tag = soup.find('questions')

        questions_data = questions_tag['v-bind:questions']
        questions_type = {v: k for k, v in json.loads(questions_tag['v-bind:question-types']).items()}

        new_questions_list = json.loads(questions_data)
        for question in new_questions_list:
            question['type'] = questions_type[question['type']][14:]

        global questions_list
        questions_list.extend(new_questions_list)

        with open('intercepted_data.json', 'w', encoding='utf-8-sig') as file:
            json.dump(questions_list, file, ensure_ascii=False, indent=4)

        print("Received request and processed data.")

def render_questions_to_text(questions):
    lines = []
    question_image_base_url = 'https://ks.rsmu.ru/upload/l_btz_filequestion/'
    answer_image_base_url = 'https://ks.rsmu.ru/upload/l_btz_fileanswer/'

    for question in questions:
        question_type = question['type']
        if question['images']:
            lines.append(f"{question_type} {question['text']}")
            for i, image in enumerate(question['images'], start=1):
                lines.append(f"КАРТИНКА ВОПРОСА {i}: {question_image_base_url}{image}")
        else:
            lines.append(f"{question_type} {question['text']}")
        
        if question_type == 'MATCHING':
            try:
                answers = question['answers']
                answers_draggable = question['answers_draggable']
            except KeyError:
                print(f"Error in question: {question}")
                continue

            for answer in answers:
                answer_text = answer['answer']
                image_ids = ', '.join(answer['images']) if answer['images'] else ''
                lines.append(f"{answer_text} ({answer_image_base_url}{image_ids})" if image_ids else answer_text)
            
            max_answer_length = max(
                max((len(x['answer']) for x in answers), default=0),
                max((len(x['answer']) for x in answers_draggable), default=0)
            )
            lines.append('-' * max_answer_length)

            for answer in answers_draggable:
                answer_text = answer['answer']
                image_ids = ', '.join(answer['images']) if answer['images'] else ''
                lines.append(f"{answer_text} ({answer_image_base_url}{image_ids})" if image_ids else answer_text)
        else:
            for answer in question['answers']:
                answer_text = answer['answer']
                image_ids = ', '.join(answer['images']) if answer['images'] else ''
                lines.append(f"{answer_text} ({answer_image_base_url}{image_ids})" if image_ids else answer_text)
        
        lines.append('')
    return '\n'.join(lines)
