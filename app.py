import shutil
from flask import Flask, request, send_file, after_this_request
from flask_cors import CORS
from decoders.decoder import Decoder
from parsers.style_parser import StyleParser
from parsers.syntax_parser import SyntaxParser
from generators.java_generator import JavaCodeGenerator

app = Flask(__name__)
CORS(app)


@app.route("/api/generate-code", methods=["POST"])
def generate():
    @after_this_request
    def _(response):
        shutil.rmtree("temp", ignore_errors=True)
        return response

    try:
        encoded_xml = request.json["data"]
    except:
        return "No data provided", 400

    decoded_xml = Decoder().convert(encoded_xml)
    style_tree = StyleParser().convert_to_style_tree(decoded_xml)
    syntax_tree = SyntaxParser().convert_to_syntax_tree(style_tree)
    code = JavaCodeGenerator().generate_code(syntax_tree, "temp/code")

    if not decoded_xml or not style_tree or not syntax_tree or not code:
        return "Bad data provided", 400

    shutil.make_archive("temp/generated-code", "zip", "temp/code")
    return send_file("temp/generated-code.zip", as_attachment=True)
