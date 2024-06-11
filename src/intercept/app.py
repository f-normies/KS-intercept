import click
import subprocess
import os
import signal
import json
from datetime import datetime

PID_FILE = 'proxy.pid'

@click.group()
def cli():
    pass

@click.command()
@click.option('-q', '--quiet', is_flag=True, help='Suppress mitmproxy logs')
def start(quiet):
    if os.path.exists(PID_FILE):
        print("Proxy is already running.")
        return
    
    print("Starting proxy...")
    args = ['mitmdump', '--listen-port', '44700', '-s', 'intercept.py']
    if quiet:
        args.append('--quiet')
    proxy_process = subprocess.Popen(args)
    
    # Save the PID to a file
    with open(PID_FILE, 'w') as f:
        f.write(str(proxy_process.pid))
    
    print("Proxy started. Listening for browser requests...")

@click.command()
def stop():
    if not os.path.exists(PID_FILE):
        print("Proxy is not running.")
        return

    # Read the PID from the file
    with open(PID_FILE, 'r') as f:
        pid = int(f.read())
    
    print("Stopping proxy...")
    os.kill(pid, signal.SIGINT)
    
    # Remove the PID file
    os.remove(PID_FILE)
    print("Proxy stopped.")

def deduplicate_questions(questions_list):
    seen = {}
    deduplicated_list = []
    
    for question in questions_list:
        key = (question['text'], tuple(sorted(answer['uid'] for answer in question['answers'])))
        if key not in seen:
            seen[key] = True
            deduplicated_list.append(question)
    
    return deduplicated_list

@click.command()
def save():
    if not os.path.exists('intercepted_data.json'):
        print("No data to save.")
        return

    with open('intercepted_data.json', 'r', encoding='utf-8-sig') as file:
        questions_list = json.load(file)

    if not questions_list:
        print("No data to save.")
        return

    from intercept import render_questions_to_text

    questions_list = deduplicate_questions(questions_list)

    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_txt_path = os.path.join('output', f"{timestamp}.txt")
    output_json_path = os.path.join('output', f"{timestamp}.json")

    os.makedirs('output', exist_ok=True)

    questions_text = render_questions_to_text(questions_list)
    with open(output_txt_path, 'w', encoding='utf-8-sig') as file:
        file.write(questions_text)

    with open(output_json_path, 'w', encoding='utf-8-sig') as file:
        json.dump(questions_list, file, ensure_ascii=False, indent=4)

    os.remove('intercepted_data.json')

    print(f"Data saved to {output_txt_path} and {output_json_path}")

cli.add_command(start)
cli.add_command(stop)
cli.add_command(save)

if __name__ == "__main__":
    cli()
