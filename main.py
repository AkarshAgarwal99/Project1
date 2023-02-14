import boto3
from flask import Flask, request, render_template, Response
import PyPDF2

app = Flask(__name__)
polly = boto3.client("polly")

@app.route("/")
def index():
    voices = polly.describe_voices()['Voices']
    return render_template("index.html", voices=voices)

@app.route("/polly", methods=['POST'])
def generate_audio_from_pdf():
    file = request.files['file']
    voice_id = request.form['voice']
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice_id
    )
    
    return Response(
        response['AudioStream'].read(),
        mimetype="audio/mpeg",
        headers={"Content-Disposition": "attachment;filename=sound.mp3"}
    )

if __name__ == "__main__":
    app.run(debug=True)
