import openai
import io
import base64
from PIL import Image
import os
import sys

from dotenv import load_dotenv

# Load environment variables
openaikey = './.env'
load_dotenv(openaikey)
openai.api_key = os.getenv("OPENAI_API_KEY")
log_file_path = os.path.join("./", "process_log.txt")

def log_message(message):
    print(message)
    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")

def process_and_encode_image(image, resize_factor=0.9):
    MAX_SIZE = 20 * 1024 * 1024  # 20MB
    original_width, original_height = image.size

    for attempt in range(5):
        buffered = io.BytesIO()
        new_width = int(original_width * (resize_factor ** attempt))
        new_height = int(original_height * (resize_factor ** attempt))
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        resized_image.save(buffered, format="JPEG")

        if buffered.tell() < MAX_SIZE:
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        else:
            print(f"Attempt {attempt + 1}: Image size is {buffered.tell()} bytes, too large. Resizing...")

    raise ValueError("Unable to reduce image size within 5 attempts")

def analyze_images_with_gpt4_vision(prompt_text, encoded_images, temperature=0):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY_JY"))

    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            image_contents = [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                for encoded_image in encoded_images
            ]
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            *image_contents
                        ],
                    }
                ],
                max_tokens=1024,
                temperature=temperature,
            )
            response_result = response.choices[0]

            if response_result.message.content.startswith("I'm sorry, but"):
                print(f"I'm sorry, attempting again. Attempt {attempt + 1}/{max_attempts}")
                continue

            return response_result

        except Exception as e:
            print(f"BadRequestError: {e}")
            if "exceeded" in str(e).lower():
                sys.exit()
            if "image_parse_error" in str(e).lower() and attempt < max_attempts - 1:
                resized_encoded_images = [
                    process_and_encode_image(Image.open(io.BytesIO(base64.b64decode(encoded_image))), 0.9)
                    for encoded_image in encoded_images
                ]
                print(f"Resizing images and retrying. Attempt {attempt + 1}/{max_attempts}")
                encoded_images = resized_encoded_images

    return None

def find_image_paths(directory):
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    return [os.path.join(directory, file) for file in os.listdir(directory) if os.path.splitext(file)[1].lower() in image_extensions]

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def encode_images_from_paths(image_paths):
    return [
        process_and_encode_image(Image.open(image_path), 0.9)
        for image_path in image_paths
        if Image.open(image_path).size > (150, 150)
    ]

temperatures = [0, 0.5, 1]
base_result_folder = "gpt4v_result/gpt4v_result"

def create_result_folder(base_folder, temperature, try_number):
    folder_name = f"{base_folder}_temp_{str(temperature).replace('.', '_')}_try{try_number}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

for temperature in temperatures:
    for try_number in range(1, 6):
        result_folder = create_result_folder(base_result_folder, temperature, try_number)

        for case_number in range(1, 319):
            result_file_path = os.path.join(result_folder, f"case-{case_number}.txt")

            if os.path.exists(result_file_path):
                print(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): skip")
                continue

            case_folder = f"output/case-{case_number}"
            history_file_path = os.path.join(case_folder, "history_texts.txt")
            figure_legends_file_path = os.path.join(case_folder, "figure_legends.txt")

            if os.path.exists(history_file_path) and os.path.exists(figure_legends_file_path):
                history_text = read_text_file(history_file_path)
                figure_legends_text = read_text_file(figure_legends_file_path)

                prompt_text = f"""
                You are tasked with solving a quiz on a special medical case involving a complex and rare disease. \
                Your challenge is to use the patient's provided medical history and imaging data to identify possible diagnostic candidates. \
                Your goal is to perform a differential diagnosis.\
                Here are the hints for the imaging data:

                Original text and image included in the page image (page_xx.png)
                Additional enlarged image versions (page_xx_image_xx.jpeg)
                Consider the Figure Legends corresponding to each image thoughtfully, as they pertain to the specific page.
                Quiz:
                Based on this information, present three possible disease candidates. Keep in mind that the correct answer may be a unique or rare disease.

                History:{history_text}
                Figure Legends:{figure_legends_text}

                Output: For each disease candidate, provide the following information:
                1. Names of three possible disease candidates.
                2. A likelihood score for each candidate, considering whether it's a rare or unique case (on a scale of 1-10).
                3. Detailed reasons for considering each disease as a potential diagnosis.
                """

                image_paths = find_image_paths(case_folder)
                encoded_images = encode_images_from_paths(image_paths)

                result = analyze_images_with_gpt4_vision(prompt_text, encoded_images, temperature)

                result_file_path = os.path.join(result_folder, f"case-{case_number}.txt")

                if result:
                    with open(result_file_path, "w", encoding='utf-8') as result_file:
                        result_file.write(result.message.content)
                    print(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): Result has been saved.")
                else:
                    print(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): Unable to find result.")
                    log_message(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): Unable to find result.")
            else:
                print(f"Case {case_number}: Necessary text files are missing.")