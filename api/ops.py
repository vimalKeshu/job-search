import json


def load_test_data(json_file='./test/data/data.json'):
    data = {}
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(data)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{json_file}': {e}")
    return data


if __name__ == '__main__':
    print(load_test_data())