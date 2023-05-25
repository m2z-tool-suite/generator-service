from database.mappings import class_type_map, invert_map

def generate_document(rows, project, class_type):
    document = create_document(project, invert_map(class_type_map)[class_type])

    for row in rows:
        diagram = create_diagram(row['diagram_id'], row['diagram_title'], row['diagram_description'])
        class_ = create_class(row['class_id'], row['class_name'], row['class_inner_class'], row['class_type_id'], row['class_type_name'])
        method = create_method(row['method_id'], row['method_abstract'], row['method_name'], row['method_return_type'], row['method_access_type_id'], row['access_type_name'])
        parameter = create_parameter(row['parameter_id'], row['parameter_name'], row['parameter_type'])

        add_row_to_document(document, diagram, class_, method, parameter)

    return document


def create_document(project, class_type):
    return {
        'title': f"List of all methods and their parameters from class type <{class_type}> in project <{project}>",
        'diagrams':[]
    }

def create_diagram(diagram_id, diagram_title, diagram_description):
    return {
        'id': diagram_id,
        'title': diagram_title,
        'description': diagram_description,
        'classes': []
    }

def create_class(class_id, class_name, class_inner_class, class_type_id, class_type_name):
    return {
        'id': class_id,
        'name': class_name,
        'inner': class_inner_class,
        'type': {
            'id': class_type_id,
            'name': class_type_name
        },
        'methods': []
    }

def create_method(method_id, method_abstract, method_name, method_return_type, method_access_type_id, method_access_type_name):
    return {
        'id': method_id,
        'abstract_': method_abstract,
        'name': method_name,
        'return_type': method_return_type,
        'access_type': {
            'id': method_access_type_id,
            'name': method_access_type_name
        },
        'parameters': []
    }

def create_parameter(parameter_id, parameter_name, parameter_type):
    return {
        'id': parameter_id,
        'name': parameter_name,
        'type': parameter_type
    }


def add_row_to_document(document, diagram, class_, method, parameter):
    diagram_exists = False
    for d in document['diagrams']:
        if d['id'] == diagram['id']:
            diagram_exists = True
            diagram = d
            break

    if not diagram_exists:
        document['diagrams'].append(diagram)

    class_exists = False
    for c in diagram['classes']:
        if c['id'] == class_['id']:
            class_exists = True
            class_ = c
            break

    if not class_exists:
        diagram['classes'].append(class_)

    # check if method exists in class
    method_exists = False
    for m in class_['methods']:
        if m['id'] == method['id']:
            method_exists = True
            method = m
            break

    if not method_exists:
        class_['methods'].append(method)

    # check if parameter exists in method
    parameter_exists = False
    for p in method['parameters']:
        if p['id'] == parameter['id']:
            parameter_exists = True
            parameter = p
            break

    if not parameter_exists and parameter['id'] != None:
        method['parameters'].append(parameter)