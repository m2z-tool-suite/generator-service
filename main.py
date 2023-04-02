import json
from decoders.decoder import Decoder
from parsers.style_parser import StyleParser
from parsers.syntax_parser import SyntaxParser
from generators.java_generator import JavaCodeGenerator

def read_file(file_name):
    with open(file_name, "r") as f:
        return f.read()

def save_to_file(file_name, data):
    with open(file_name, "w") as f:
        f.write(data)

def json_to_file(file_name, data):
    save_to_file(file_name, json.dumps(data, indent=2))

def create_examples():
    encoded_xml = read_file("examples/example_diagram.drawio")

    decoder = Decoder()
    decoded_xml = decoder.convert(encoded_xml)
    save_to_file("examples/example_diagram.xml", decoded_xml)

    style_parser = StyleParser()
    style_tree = style_parser.convert_to_style_tree(decoded_xml)
    json_to_file("examples/example_style_tree.json", style_tree)

    syntax_parser = SyntaxParser()
    syntax_tree = syntax_parser.convert_to_syntax_tree(style_tree)
    json_to_file("examples/example_syntax_tree.json", syntax_tree)

    java_code_gen = JavaCodeGenerator(syntax_tree, "examples/code")
    java_code_gen.generate_code()

create_examples()