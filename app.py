import shutil
from bson import json_util
from flask import request, send_file, after_this_request, jsonify
from config import app, aws_auth
from decoders.decoder import Decoder
from parsers.style_parser import StyleParser
from parsers.syntax_parser import SyntaxParser
from generators.java_generator import JavaCodeGenerator
from database.repository import Repository
from utilities.security import get_user_projects


@app.route("/api/generate-code", methods=["POST"])
@aws_auth.authentication_required
def generate_code():
    @after_this_request
    def _(response):
        shutil.rmtree("temp", ignore_errors=True)
        return response

    try:
        encoded_xml = request.json["data"]
    except:
        return "No data provided", 400

    decoded_xml = Decoder().convert(encoded_xml)
    style_tree = StyleParser().parse(decoded_xml)
    syntax_tree = SyntaxParser().parse(style_tree)
    code = JavaCodeGenerator().generate_code(syntax_tree, "temp/code")

    if not decoded_xml or not style_tree or not syntax_tree or not code:
        return "Bad data provided", 400

    diagram_id = request.json["id"]
    diagram_title = request.json["title"]
    Repository().save_classes(diagram_id, syntax_tree)

    shutil.make_archive("temp/generated-code", "zip", "temp/code")
    return send_file(
        "temp/generated-code.zip",
        as_attachment=True,
        download_name=f"{diagram_title}.zip",
    )


@app.route("/api/generate-document", methods=["POST"])
@aws_auth.authentication_required
def generate_document():
    project, class_type = request.json["project"], request.json["classType"]
    projects = get_user_projects(aws_auth)
    if project not in map(lambda p: p["name"], projects):
        return "Not allowed to generate documents for this project", 403

    document = Repository().save_document(project, class_type)
    if not document:
        return "No data available to generate document", 400

    return jsonify(json_util.dumps(document))


@app.route("/api/generate-graph", methods=["POST"])
@aws_auth.authentication_required
def generate_graph():
    @after_this_request
    def _(response):
        shutil.rmtree("temp", ignore_errors=True)
        return response

    project = request.json["project"]
    projects = get_user_projects(aws_auth)
    if project not in map(lambda p: p["name"], projects):
        return "Not allowed to generate graphs for this project", 403

    graph_name = Repository().save_graph(project, "temp/graph")
    if not graph_name:
        return "No data available to generate graph", 400

    shutil.make_archive(f"temp/generated-graph", "zip", "temp/graph")
    return send_file(
        f"temp/generated-graph.zip",
        as_attachment=True,
        download_name=f"{graph_name}.zip",
    )


Repository().save_document_meta()
Repository().save_graph_meta()
