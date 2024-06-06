import numpy as np
import torch
from io import BytesIO
from matplotlib import pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader

from ii_ecg import analyze_ecg
from test_ii import ECGNet

model = ECGNet()
model.load_state_dict(torch.load('ecg_model.pth', map_location=torch.device('cpu')))
model.eval()

def analyze_ecg_data(ecg_data):
    ecg_data = np.array(ecg_data)
    ecg_data = ecg_data.reshape(-1, 1, 500)
    ecg_tensor = torch.tensor(ecg_data, dtype=torch.float32)

    with torch.no_grad():
        outputs = model(ecg_tensor)
        predictions = torch.softmax(outputs, dim=1).numpy()

    return predictions.tolist()

def interpret_predictions(predictions):
    class_labels = ["Нормальный ритм", "Фибрилляция предсердий", "Тахикардия", "Брадикардия", "Другие аритмии"]
    interpreted = []
    for pred in predictions:
        max_index = np.argmax(pred)
        interpreted.append((class_labels[max_index], pred[max_index]))
    return interpreted

def create_pdf_report(note):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
    c.setFont('DejaVuSans', 12)
    c.drawString(100, height - 80, f"Отчет по полученным данным")
    c.drawString(100, height - 100, f"ID: {note.id}")
    c.drawString(100, height - 120, f"Дата рождения: {note.date_of_birth}")
    c.drawString(100, height - 140, f"Дата загрузки: {note.date_of_upload}")
    c.drawString(100, height - 160, f"Имя: {note.first_name}")
    c.drawString(100, height - 180, f"Фамилия: {note.last_name}")
    y_position = height - 350 
    for title, data_str in note.data.items():
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 5)
        data = [float(val) for val in data_str.split(',') if val.strip()]
        ax.plot(data, label=title)
        ax.legend()
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        img_reader = ImageReader(img)
        c.drawImage(img_reader, 50, y_position, width - 100, 100)
        y_position -= 120
        if y_position < 50:
            c.showPage()
            y_position = height - 120
    c.save()
    buffer.seek(0)
    return buffer
