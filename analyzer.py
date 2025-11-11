import gc
import json
from PIL import Image
import google.generativeai as genai

def process_image(file_path='', prompt='', type=None):
    model = genai.GenerativeModel('gemini-1.5-flash-002')
    try:
        if type == 'image':
            with Image.open(file_path) as img:
                response = model.generate_content([prompt, img])
        elif type == 'text':
            response = model.generate_content([prompt, json.dumps(file_path, indent=2)])
        else:
            return {}
        if hasattr(response, 'candidates') and response.candidates:
            text = response.candidates[0].content.parts[0].text
            text = text.replace('```','').replace('json','')
            try:
                return json.loads(text)
            except:
                return {'response_text': text}
        return {}
    finally:
        gc.collect()
