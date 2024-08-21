from dotenv import load_dotenv
import os

# export env variable
# export OPENAI_API_KEY=sk-proj-ZCpwbzsyhm0wdEf_M3db5ghH-ArWdHXZgOlFa4JZOjdki1IBIMlX_-jwl2T3BlbkFJu1v7O7mC5mb5b3GiAg_8jKyyA-F3vU5DGnbfJqVgpiw--DwfcBbmLcZsAAA
# export OPENAI_ASSISTANT_ID=asst_rBsu7u3vfM5q4CAyCr2eWEdee

load_dotenv()
key = os.environ.get("OPENAI_ASSISTANT_ID")

print(key)