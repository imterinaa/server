from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify, render_template_string
from models import Note
from helpers import analyze_ecg_data, interpret_predictions, create_pdf_report

bp = Blueprint('main', __name__)

@bp.route('/')
def hello():
    all_notes = Note.get_all_notes()
    notes = all_notes[:5]
    return render_template('dashboard.html', notes=notes, all_notes=all_notes)

@bp.route('/graph/<int:note_id>')
def graph(note_id):
    note = Note.get_note_by_id(note_id)
    if note:
        return render_template('detail.html', note=note)
    else:
        return "Запись не найдена", 404

@bp.route('/read_numbers')
def read_numbers():
    file_path = 'numbers.txt' 
    positive_numbers = read_and_filter_positive_numbers(file_path)
    create_chart(positive_numbers) 
    return render_template('numbers.html', numbers=positive_numbers)

@bp.route('/all_once')
def once():
    graph_data = parse_xml_file("./sample.xml")
    graphs = []
    fig, ax = plt.subplots()
    fig.set_size_inches(20, 5) 
    for title, data_str in graph_data.items():
        data = [float(val) for val in data_str.split(',') if val.strip()]
        ax.plot(data, label=title)
    ax.legend()
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    graph_url = base64.b64encode(img.getvalue()).decode()
    strings = ["Строка 1", "Строка 2", "Строка 3"]
    template_string = '''
    <!doctype html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>График и список текста</title>
    </head>
    <body>
        <h1>График и список текста</h1>
        <div>
            <h2>График</h2>
            <img src="data:image/png;base64,{{ graph_url }}" alt="График">
        </div>
        <div>
            <h2>Список текста</h2>
            <ul>
                {% for string in strings %}
                    <li>{{ string }}</li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    '''
    rendered_html = render_template_string(template_string, graph_url=graph_url)
    return rendered_html

@bp.route('/diff')
def diff():
    graph_data = parse_xml_file("./sample.xml")
    graphs = []
    for title, data_str in graph_data.items():
        data = [float(val) for val in data_str.split(',') if val.strip()]
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 5) 
        ax.plot(data)
        ax.set_title(title)
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        graph_url = base64.b64encode(img.getvalue()).decode()
        graphs.append(graph_url)
    return render_template('index.html', graphs=graphs, num_graphs=len(graphs))

@bp.route('/show_chart')
def show_chart():
    return render_template('chart.html')

@bp.route('/dashboard/all_json')
def dashboard_all_json():
    try:
        all_notes = Note.query.all()
        notes_list = [note.to_dict() for note in all_notes]
        return jsonify(notes_list)
    except Exception as e:
        app.logger.error(f"Error in /dashboard/all_json: {notes_list}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/dashboard/first_five_json')
def dashboard_first_five_json():
    try:
        first_five_notes = Note.query.limit(5).all()
        notes_list = [note.to_dict() for note in first_five_notes]
        return jsonify(notes_list)
    except Exception as e:
        app.logger.error(f"Error in /dashboard/first_five_json: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/search_notes', methods=['POST'])
def search_notes():
    data = request.json
    last_name = data.get('lastName')
    first_name = data.get('firstName')
    birth_date = data.get('birthDate')
    upload_date = data.get('uploadDate')
    query = Note.query
    if last_name:
        query = query.filter(Note.last_name.contains(last_name))
    if first_name:
        query = query.filter(Note.first_name.contains(first_name))
    if birth_date:
        query = query.filter(Note.date_of_birth == datetime.strptime(birth_date, '%Y-%m-%d').date())
    if upload_date:
        query = query.filter(Note.date_of_upload == datetime.strptime(upload_date, '%Y-%m-%d').date())
    results = query.all()
    notes = [note.to_dict() for note in results]
    return jsonify(notes)

@bp.route('/search', methods=['POST'])
def search():
    data = request.json
    last_name = data.get('lastName')
    first_name = data.get('firstName')
    birth_date = data.get('birthDate')
    upload_date = data.get('uploadDate')
    results = Note.search_notes(last_name=last_name, first_name=first_name, birth_date=birth_date, upload_date=upload_date)
    return jsonify([note.to_dict() for note in results])

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "failure", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "failure", "message": "No selected file"}), 400
    if file and file.filename.endswith('.xml'):
        file.save(os.path.join("./", file.filename))
        data = parse_xml_file("./"+file.filename)
        return jsonify({"status": "success", "message": "File received", "filename": file.filename}), 200
    else:
        return jsonify({"status": "failure", "message": "Invalid file type"}), 400

@bp.route('/detail/<int:note_id>')
def detail_view(note_id):
    note = Note.get_note_by_id(note_id)
    graph_data = note.data
    graph_urls = []
    for title, data_str in graph_data.items():
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 5)
        data = [float(val) for val in data_str.split(',') if val.strip()]
        ax.plot(data, label=title)
        ax.legend()
        img = BytesIO()
        plt.savefig(img, format='png',bbox_inches='tight')
        img.seek(0)
        plt.close()
        graph_url = base64.b64encode(img.getvalue()).decode()
        graph_urls.append(graph_url)
    if note:
        return render_template('detail.html', note=note, graph_urls=graph_urls)
    else:
        return "Запись не найдена", 404

@bp.route('/download_report/<int:note_id>')
def download_report(note_id):
    note = Note.get_note_by_id(note_id)
    if not note:
        return "Запись не найдена", 404
    buffer = create_pdf_report(note)
    return send_file(buffer, as_attachment=True, download_name='report.pdf', mimetype='application/pdf')

@bp.route('/analyze/<int:note_id>', methods=['GET'])
def analyze_ecg1(note_id):
    note = Note.get_note_by_id(note_id)
    if not note:
        return jsonify({"error": "Запись не найдена"}), 404
    ecg_data = note.data
    ecg_samples = []
    for lead, data_str in ecg_data.items():
        np_array = np.array([float(x) for x in data_str.split(',') if x.strip()])
        ecg_samples.append(np_array[:500])
    ecg_samples = np.stack(ecg_samples).reshape(-1, 1, 500)
    predictions = analyze_ecg_data(ecg_samples)
    interpreted_predictions = interpret_predictions(predictions)
    return jsonify({"ecg_data": interpreted_predictions})

@bp.route('/submit', methods=['POST'])
def submit():
    data = request.json
    Note.create_note(
        date_of_birth=data.get('date_of_birth'),
        date_of_upload=data.get('date_of_upload'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        data=data.get('data')
    )
    return redirect(url_for('main.hello'))

@bp.route('/search_form')
def search_form():
    return render_template('search1.html')

@bp.route('/download_file')
def download_file():
    file_path = generate_file()
    response = send_file(file_path, as_attachment=True)
    os.remove(file_path)
    return response

def generate_file():
    notes = Note.query.all()
    file_path = 'temp.txt'
    with open(file_path, 'w') as file:
        for note in notes:
            file.write(f"{note.first_name} {note.last_name}\n")
    return file_path

@bp.route('/upload_file')
def upload_file_template():
    return render_template('upload.html')
