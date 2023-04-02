import traceback
import re
import os
from generators.code_generator import CodeGenerator


class JavaCodeGenerator(CodeGenerator):
    """
    Generate Java code
    """

    def __init__(self):
        self.__classes = list()
        self.__properties = list()
        self.__methods = list()
        self.__files = list()

    def generate_code(self, syntax_tree, file_path):
        """
        Use the syntax tree to generate code files for the UML class diagrams

        Parameters:
            syntax_tree: syntax_tree of the drawio file
            file_path: path for the code files to be written to
        """

        print("<<< GENERATING CODE FILES FROM SYNTAX TREE >>>")

        self.__classes.clear()
        self.__properties.clear()
        self.__methods.clear()
        self.__files.clear()

        try:
            for _, _class in syntax_tree.items():
                file = ""

                inheritance = ""
                if len(_class["relationships"]["extends"]) > 0:
                    inheritance += "extends "
                    inheritance += ",".join(
                        [
                            syntax_tree[r]["name"]
                            for r in _class["relationships"]["extends"]
                        ]
                    ).strip(",")

                implementation = ""
                if len(_class["relationships"]["implements"]) > 0:
                    implementation += "implements "
                    implementation += ",".join(
                        [
                            syntax_tree[r]["name"]
                            for r in _class["relationships"]["implements"]
                        ]
                    ).strip(",")

                abstract_methods = list()
                self.get_abstract_methods(
                    syntax_tree,
                    _class["relationships"]["implements"],
                    _class["relationships"]["extends"],
                    abstract_methods,
                )
                abstract_methods.reverse()  # reverse the list so that the abstract methods are in the correct order
                abstract_methods = [
                    m
                    for i, m in enumerate(abstract_methods)
                    if m not in abstract_methods[:i]
                ]  # remove duplicate abstract methods

                associations = self.get_associations(
                    syntax_tree, _class["relationships"]
                )
                aggregation_children = self.get_aggregation_children(
                    syntax_tree, _class["relationships"]
                )
                aggregation_parents = self.get_aggregation_parents(
                    syntax_tree, _class["relationships"]
                )
                composition_children = self.get_composition_children(
                    syntax_tree, _class["relationships"]
                )
                composition_parents = self.get_composition_parents(
                    syntax_tree, _class["relationships"]
                )
                # join all associations
                all_associations = (
                    associations
                    + aggregation_children
                    + aggregation_parents
                    + composition_children
                    + composition_parents
                )

                file += self.generate_classes(
                    _class["type"], _class["name"], inheritance, implementation
                )
                file += "\n"
                file += self.generate_properties(_class["properties"], all_associations)
                if (
                    _class["properties"]
                    or _class["relationships"]["association"]
                    or _class["relationships"]["aggregationChildren"]
                    or _class["relationships"]["aggregationParents"]
                    or _class["relationships"]["compositionChildren"]
                    or _class["relationships"]["compositionParents"]
                ):
                    file += "\n"
                file += self.generate_methods(
                    _class["methods"],
                    _class["properties"],
                    all_associations,
                    _class["type"],
                    abstract_methods,
                )
                file += "}\n"
                self.__files.append([_class["name"], file])

            self.generate_files(file_path.strip("/"))
            return True

        except Exception as e:
            traceback.print_exc()
            print(f"JavaCodeGenerator.generate_code ERROR: {e}")
            return False

    def generate_classes(self, class_type, class_name, extends, implements):
        """
        Generate the class header

        Parameters:
            class_type: type of class; 'class', 'abstract', 'interface'
            class_name: name of class
            extends: the classes extended by this class
            implements: the interfaces implemented by this class

        Returns:
            class_header: class header string
        """

        type_of_class = "public class" if class_type == "class" else class_type
        type_of_class = (
            class_type + " class" if class_type == "abstract" else type_of_class
        )

        class_header = f"{type_of_class} {class_name} {extends} {implements}" + " {\n"
        class_header = re.sub(" +", " ", class_header)
        self.__classes.append(class_header)
        return class_header

    def get_classes(self):
        """
        Getter for classes
        """

        return self.__classes

    def generate_properties(self, properties, all_asssociations):
        """
        Generate properties for the class

        Parameters:
            properties: dictionary of properties
            all_asssociations: list of associations, aggreatation children, aggregation parents, composition children, composition parents

        Returns:
            properties_string: string of the properties
        """

        properties_string = ""
        for _, _property_value in properties.items():
            p = f"\t{_property_value['access']} {_property_value['type']} {_property_value['name']};\n"
            self.__properties.append(p)
            properties_string += p

        for association in all_asssociations:
            p = f"\tprivate {association} {association[0].lower() + association[1:]};\n"
            self.__properties.append(p)
            properties_string += p

        return properties_string

    def get_properties(self):
        """
        Getter for properties
        """

        return self.__properties

    def get_associations(self, syntax_tree, relationships):
        """
        Get the associations for the class

        Parameters:
            syntax_tree: syntax_tree of the drawio file
            relationships: dictionary of relationships

        Returns:
            associations: list of associations
        """

        associations = list()
        for association in relationships["association"]:
            associations.append(syntax_tree[association]["name"])

        return associations

    def get_aggregation_children(self, syntax_tree, relationships):
        """
        Get the aggregation children for the class

        Parameters:
            syntax_tree: syntax_tree of the drawio file
            relationships: dictionary of relationships

        Returns:
            aggregation_children: list of aggregation children
        """

        aggregation_children = list()
        for aggregation in relationships["aggregationChildren"]:
            aggregation_children.append(syntax_tree[aggregation]["name"])

        return aggregation_children

    def get_aggregation_parents(self, syntax_tree, relationships):
        """
        Get the aggregation parents for the class

        Parameters:
            syntax_tree: syntax_tree of the drawio file
            relationships: dictionary of relationships

        Returns:
            aggregation_parents: list of aggregation parents
        """

        aggregation_parents = list()
        for aggregation in relationships["aggregationParents"]:
            aggregation_parents.append(syntax_tree[aggregation]["name"])

        return aggregation_parents

    def get_composition_children(self, syntax_tree, relationships):
        """
        Get the composition children for the class

        Parameters:
            syntax_tree: syntax_tree of the drawio file
            relationships: dictionary of relationships

        Returns:
            composition_children: list of composition children
        """

        composition_children = list()
        for composition in relationships["compositionChildren"]:
            composition_children.append(syntax_tree[composition]["name"])

        return composition_children

    def get_composition_parents(self, syntax_tree, relationships):
        """
        Get the composition parents for the class

        Parameters:
            syntax_tree: syntax_tree of the drawio file
            relationships: dictionary of relationships

        Returns:
            composition_parents: list of composition parents
        """

        composition_parents = list()
        for composition in relationships["compositionParents"]:
            composition_parents.append(syntax_tree[composition]["name"])

        return composition_parents

    def generate_methods(
        self, methods, properties, all_asssociations, class_type, abstract_methods
    ):
        """
        Generate methods for the class

        Parameters:
            methods: dictionary of methods
            properties: dictionary of properties
            all_asssociations: list of associations, aggreatation children, aggregation parents, composition children, composition parents
            class_type: type of current class
            abstract_methods: list of abstract methods

        Returns:
            methods_string: string of the methods
        """

        # getter and setter methods
        methods_string = ""
        if class_type == "class" or class_type == "abstract":
            # normal properties
            for _, _property_value in properties.items():
                if _property_value["access"] == "private":
                    getter = (
                        f"\tpublic {_property_value['type']} get{_property_value['name'][0].upper() + _property_value['name'][1:]}()"
                        f" {{\n \t\treturn this.{_property_value['name']}; \n\t}}\n"
                    )
                    methods_string += getter + "\n"
                    self.__methods.append(getter)

                    setter = (
                        f"\tpublic void set{_property_value['name'][0].upper() + _property_value['name'][1:]}({_property_value['type']} {_property_value['name']})"
                        f" {{\n \t\tthis.{_property_value['name']} = {_property_value['name']}; \n\t}}\n"
                    )
                    methods_string += setter + "\n"
                    self.__methods.append(setter)

            # all association properties
            for association in all_asssociations:
                getter = (
                    f"\tpublic {association} get{association[0].upper() + association[1:]}()"
                    f" {{\n \t\treturn this.{association[0].lower() + association[1:]}; \n\t}}\n"
                )
                methods_string += getter + "\n"
                self.__methods.append(getter)

                setter = (
                    f"\tpublic void set{association[0].upper() + association[1:]}({association} {association[0].lower() + association[1:]})"
                    f" {{\n \t\tthis.{association[0].lower() + association[1:]} = {association[0].lower() + association[1:]}; \n\t}}\n"
                )
                methods_string += setter + "\n"
                self.__methods.append(setter)

        # abstract methods
        if class_type == "class":
            for abstract_method in abstract_methods:
                comment = "// TODO: Must be implemented!"
                m = (
                    f"\t{abstract_method['access']} {abstract_method['return_type']} {abstract_method['name']}()"
                    f" {{\n \t\t{comment} \n\t}}\n"
                )
                methods_string += m + "\n"
                self.__methods.append(m)

        # normal methods
        for _, method_value in methods.items():
            if not method_value["parameters"]:
                params = "()"
            else:
                params = (
                    "("
                    + ", ".join(
                        [
                            f"{p['type']} {p['name']}"
                            for p in method_value["parameters"].values()
                        ]
                    )
                    + ")"
                )

            if method_value["abstract"] == "true" and class_type != "interface":
                m = f"\t{method_value['access']} abstract {method_value['return_type']} {method_value['name']}{params};\n"
            elif method_value["abstract"] == "true" and class_type == "interface":
                m = f"\t{method_value['access']} {method_value['return_type']} {method_value['name']}{params};\n"
            else:
                m = f"\t{method_value['access']} {method_value['return_type']} {method_value['name']}{params} {{\n\n\t}}\n"

            methods_string += m + "\n"
            self.__methods.append(m)

        return methods_string

    def get_methods(self):
        """
        Getter for the methods
        """

        return self.__methods

    def get_abstract_methods(self, syntax_tree, implements, extends, abstract_methods):
        """
        Get the abstract methods that require implementation

        Parameters:
            implements: list of interfaces
            syntax_tree: syntax_tree of the drawio file
            extends: list of classes
            abstract_methods: list of interface methods
        """

        for i in implements:
            interface_obj = syntax_tree[i]
            methods = list(
                interface_obj["methods"].values()
            )  # take all methods from interface
            methods.reverse()  # reverse the list so that the methods are in the correct order
            abstract_methods += methods
            self.get_abstract_methods(
                syntax_tree,
                interface_obj["relationships"]["extends"],
                interface_obj["relationships"]["extends"],
                abstract_methods,
            )

        for e in extends:
            class_obj = syntax_tree[e]
            methods = [
                m for m in class_obj["methods"].values() if m["abstract"] == "true"
            ]  # take only abstract methods from class
            methods.reverse()  # reverse the list so that the methods are in the correct order
            abstract_methods += methods
            self.get_abstract_methods(
                syntax_tree,
                class_obj["relationships"]["implements"],
                class_obj["relationships"]["extends"],
                abstract_methods,
            )

    def generate_files(self, file_path):
        """
        Write generated code to file

        Returns:
            boolean: True if successful, False if unsuccessful
            file_path: path for the code files to be written to
        """

        print(f"<<< WRITING FILES TO {file_path} >>>")

        try:
            os.makedirs(file_path, exist_ok=True)
            for file in self.get_files():
                file_name = file[0] + ".java"
                file_contents = file[1]
                with open(file_path + f"/{file_name}", "w") as f:
                    f.write(file_contents)
        except Exception as e:
            traceback.print_exc()
            print(f"JavaCodeGenerator.generate_files ERROR: {e}")

    def get_files(self):
        """
        Getter for the files
        """

        return self.__files
