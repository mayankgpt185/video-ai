import pyjson5
import re

class OutputParserService:

            @staticmethod
            def json5toJson(text: str):
                try:
                    # Greedy search for 1st json candidate.
                    match = re.search(
                        r"\{.*}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
                    )
                    json_str = ""
                    if match:
                        json_str = match.group()
                    json_object = pyjson5.loads(json_str, strict=False)
                    return pyjson5.dumps(json_object)
                except:
                    return text