import json

BASE_URL = 'http://localhost:8000'


def get_code_samples(route, method):
    nl = '\n'  # new line character to use in f-strings.
    if method in ['POST', 'PUT', 'DELETE'] and route.body_field:
        print(f"Path:{route.path}")
        try:
            example_schema = route.body_field.type_.Config.schema_extra.get('example')
            payload = f"json.dumps({example_schema})"
            data_raw = f"\\{nl} --data-raw '" + f"{json.dumps(example_schema)} " + "'"
        except Exception as e:
            print(f"Path:{route.path} Error:{e}")
            payload = None
            data_raw = ''
    else:
        payload = None
        data_raw = ''
    return [
        {
            'lang': 'Shell',
            'source': f"curl --location\\{nl} "
            f"--request {method} '{BASE_URL}{route.path}'\\{nl} "
            f"--header 'Authorization: Bearer <your-token>'"
            f"{data_raw}",
            'label': 'cURL',
        },
        {
            'lang': 'Python',
            'source': f"""import requests{nl}{f'import json{nl}' if method.lower() == 'post' else ''}{nl}url = \"{BASE_URL}{route.path}\"{nl}{str(f'{nl}payload = {payload}') if payload else ''}{nl}headers = {{'Authorization': 'Bearer <your-token>'}}{nl}response = requests.request(\"{method}\", url, headers=headers{', data=payload' if payload else ''}){nl*2}print(response.text)""",
            'label': 'Python',
        },
    ]
