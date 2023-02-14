import boto3
from flask import Flask, request, render_template, Response
import PyPDF2
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")

cors = CORS(app, resources={"/*": {"origins": "*"}}, support_credentials=True)
polly = boto3.client("polly")

@app.route("/")
def index():
    voices = polly.describe_voices()['Voices']
    list_of_voices = { "voices": voices}
    return list_of_voices

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
@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    source_lang = request.form['source_lang']
    target_lang = request.form['target_lang']

    translate = boto3.client('translate')
    response = translate.translate_text(Text=text, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang)
    output = { "input_text": text,
              "translation_text": response['TranslatedText'],
              "source_lang": source_lang,
              "target_lang": target_lang
              }
    return output

if __name__ == "__main__":
    app.run(debug=True)
