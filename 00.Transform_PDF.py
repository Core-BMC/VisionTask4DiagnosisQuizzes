from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import re
import os
from PIL import Image
import io


def save_images_from_page(doc, page_number, output_folder):
    images = []
    for img in doc.get_page_images(page_number):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_size = base_image["width"], base_image["height"]

        # Check if the image size is greater than 120x120
        if all(size > 120 for size in image_size):
            image_path = os.path.join(output_folder, f"page_{page_number + 1}_image_{xref}.{image_ext}")
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            images.append(image_path)
    return images


def process_pdf(new_pdf_path, output_folder):
    new_pdf = PdfReader(new_pdf_path)
    doc = fitz.open(new_pdf_path)

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    page_images = [convert_page_to_image(doc, i, output_folder) for i in range(len(doc))]
    history_texts = extract_history_text(new_pdf)
    figure_legends = find_figure_legends(new_pdf)
    extracted_images = [save_images_from_page(doc, i, output_folder) for i in range(len(doc))]

    doc.close()

    return page_images, history_texts, figure_legends, extracted_images


def convert_page_to_image(doc, page_number, output_folder):
    page = doc.load_page(page_number)
    # Create a matrix for the desired scale
    matrix = fitz.Matrix(0.9, 0.9)  # Scale down to reduce file size
    pix = page.get_pixmap(matrix=matrix)

    # JPEG image path
    output = os.path.join(output_folder, f"page_{page_number + 1}.jpeg")

    # Convert Pix object to JPEG image data
    img_data = pix.tobytes("jpeg")

    # Create and save Image object
    image = Image.open(io.BytesIO(img_data))
    image.save(output, "JPEG", quality=85)  # Set JPEG quality to 85

    print(f"Saved JPEG image: {output}")
    return output


def extract_history_text(pdf):
    history_texts = []
    history_pattern = re.compile(r'\bHistory\b', re.IGNORECASE)
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            start_index = re.search(history_pattern, text)
            if start_index:
                history_texts.append(text[start_index.start():])
    return history_texts


def find_figure_legends(pdf):
    figure_legends = []
    # Updated pattern to find 'Figure' followed by a number, anywhere in the text
    figure_pattern = re.compile(r'Figure.*', re.IGNORECASE | re.DOTALL)

    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            # Find all occurrences of the figure pattern in the text
            figures = re.findall(figure_pattern, text)
            if figures:
                # Add each figure legend along with the page number
                figure_legends.extend([(figure, i + 1) for figure in figures])

    return figure_legends


# Function to process all PDFs
def process_all_pdfs(base_folder, start_case, end_case):
    all_history_texts = {}
    all_figure_legends = {}

    for case_number in range(start_case, end_case + 1):
        input_pdf = os.path.join(base_folder, f"case-{case_number}.pdf")
        output_folder = os.path.join("output", f"case-{case_number}")

        if os.path.exists(input_pdf):
            print(f"Processing {input_pdf}...")
            page_images, history_texts, figure_legends, extracted_images = process_pdf(input_pdf, output_folder)

            # Save results in dictionaries
            all_history_texts[f"case-{case_number}"] = history_texts
            all_figure_legends[f"case-{case_number}"] = figure_legends
        else:
            print(f"File {input_pdf} does not exist. Skipping.")

    return all_history_texts, all_figure_legends


# Process PDFs from case-1.pdf to case-318.pdf
base_folder = "pdfs"
start_case = 1
end_case = 4
all_history_texts, all_figure_legends = process_all_pdfs(base_folder, start_case, end_case)

# Save results to files
for case, history_texts in all_history_texts.items():
    history_file_path = os.path.join("output", case, "history_texts.txt")
    with open(history_file_path, "w", encoding='utf-8') as file:
        for text in history_texts:
            file.write(text + "\n\n")

for case, figure_legends in all_figure_legends.items():
    figure_legends_file_path = os.path.join("output", case, "figure_legends.txt")
    with open(figure_legends_file_path, "w", encoding='utf-8') as file:
        for figure, page in figure_legends:
            file.write(f"{figure} (Page {page})\n")
