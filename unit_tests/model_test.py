from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[2]) + '/deployment')

from deployment import model

def read_text(file):
    test_directory= Path(__file__).parent
    with open(test_directory / file,'rt',encoding = 'utf-8') as f_in:
        return f_in.read().strip()

def read_json(file):
    test_directory= Path(__file__).parent
    with open(test_directory / file,'rt',encoding = 'utf-8') as f:
        return json.load(f)

def test_base64_decode():
    base64_input = read_text('data.b64')

    actual_result=model.base64_decode(base64_input)
    expected_result = read_json('test_data.json')
    assert actual_result == expected_result
