import os
import json
from config import mysql, mongo, arango
from database.mappings import (
    class_type_map,
    access_type_map,
    relationship_type_map,
    boolean_map,
)
from generators.document_generator import DocumentGenerator
from generators.graph_generator import GraphGenerator
from dotenv import load_dotenv

load_dotenv()


class Repository:
    """
    This class is responsible for saving the data to the database.
    """

    def get_document_meta(self):
        """
        Get the meta for document from the database
        """

        db = mongo[os.getenv("MONGODB_DATABASE")]
        collection = db["meta"]
        meta = collection.find_one({"_id": "meta-document"})
        return meta

    def get_graph_meta(self):
        """
        Get the meta for document from the database
        """

        db = mongo[os.getenv("MONGODB_DATABASE")]
        collection = db["meta"]
        meta = collection.find_one({"_id": "meta-graph"})
        return meta

    def save_document_meta(self):
        """
        Save the meta for document to the database
        """

        if self.get_document_meta():
            return

        with open("meta/meta-document.json", "r") as f:
            db = mongo[os.getenv("MONGODB_DATABASE")]
            collection = db["meta"]
            meta_document = json.load(f)
            collection.insert_one(meta_document)

    def save_graph_meta(self):
        """
        Save the meta for graph to the database
        """

        if self.get_graph_meta():
            return

        with open("meta/meta-graph.json", "r") as f:
            db = mongo[os.getenv("MONGODB_DATABASE")]
            collection = db["meta"]
            meta_graph = json.load(f)
            collection.insert_one(meta_graph)

    def save_classes(self, diagram_id, syntax_tree):
        """
        Save the classes to the database

        Parameters:
            diagram_id: the id of the diagram
            syntax_tree: the syntax tree of the diagram
        """

        db = mysql.get_db()
        cursor = db.cursor()

        cursor.execute("DELETE FROM class WHERE diagram_id = %s", (diagram_id,))

        for class_id, class_data in syntax_tree.items():
            cursor.execute(
                "INSERT INTO class (id, class_type_id, name_, inner_class, diagram_id) VALUES (%s, %s, %s, %s, %s)",
                (
                    class_id,
                    class_type_map[class_data["type"]],
                    class_data["name"],
                    boolean_map[class_data["inner"]],
                    diagram_id,
                ),
            )

            for _, property_data in class_data["properties"].items():
                cursor.execute(
                    "INSERT INTO property (access_type_id, name_, type_, class_id) VALUES (%s, %s, %s, %s)",
                    (
                        access_type_map[property_data["access"]],
                        property_data["name"],
                        property_data["type"],
                        class_id,
                    ),
                )

            for _, method_data in class_data["methods"].items():
                cursor.execute(
                    "INSERT INTO method (access_type_id, abstract, name_, return_type, class_id) VALUES (%s,  %s, %s, %s, %s)",
                    (
                        access_type_map[method_data["access"]],
                        boolean_map[method_data["abstract"]],
                        method_data["name"],
                        method_data["return_type"],
                        class_id,
                    ),
                )
                method_id = cursor.lastrowid

                for _, parameter_data in method_data["parameters"].items():
                    cursor.execute(
                        "INSERT INTO parameter (name_, type_, method_id) VALUES (%s, %s, %s)",
                        (parameter_data["name"], parameter_data["type"], method_id),
                    )

        # Create relationships after all classes have been created
        for class_id, class_data in syntax_tree.items():
            for class_in_relationship in class_data["relationships"]["implements"]:
                cursor.execute(
                    "INSERT INTO relationship (relationship_type_id, parent_class_id, child_class_id) VALUES (%s, %s, %s)",
                    (
                        relationship_type_map["implements"],
                        class_in_relationship,
                        class_id,
                    ),
                )

            for class_in_relationship in class_data["relationships"]["extends"]:
                cursor.execute(
                    "INSERT INTO relationship (relationship_type_id, parent_class_id, child_class_id) VALUES (%s, %s, %s)",
                    (relationship_type_map["extends"], class_in_relationship, class_id),
                )

            for class_in_relationship in class_data["relationships"]["association"]:
                cursor.execute(
                    "INSERT INTO relationship (relationship_type_id, parent_class_id, child_class_id) VALUES (%s, %s, %s)",
                    (
                        relationship_type_map["association"],
                        class_in_relationship,
                        class_id,
                    ),
                )

            for class_in_relationship in class_data["relationships"][
                "aggregationParents"
            ]:
                cursor.execute(
                    "INSERT INTO relationship (relationship_type_id, parent_class_id, child_class_id) VALUES (%s, %s, %s)",
                    (
                        relationship_type_map["aggregation"],
                        class_in_relationship,
                        class_id,
                    ),
                )

            for class_in_relationship in class_data["relationships"][
                "compositionParents"
            ]:
                cursor.execute(
                    "INSERT INTO relationship (relationship_type_id, parent_class_id, child_class_id) VALUES (%s, %s, %s)",
                    (
                        relationship_type_map["composition"],
                        class_in_relationship,
                        class_id,
                    ),
                )

            for class_in_relationship in class_data["relationships"]["inner"]:
                cursor.execute(
                    "INSERT INTO relationship (relationship_type_id, parent_class_id, child_class_id) VALUES (%s, %s, %s)",
                    (relationship_type_map["inner"], class_id, class_in_relationship),
                )

        db.commit()

    def save_document(self, project, class_type):
        """
        Save the document to the database

        Parameters:
            project: the project name
            class_type: the class type
        """

        mysql_db = mysql.get_db()
        cursor = mysql_db.cursor()
        cursor.callproc("document_generate_table", (project, class_type))
        cursor.execute("SELECT * FROM document_table")
        rows = cursor.fetchall()

        mongo_db = mongo[os.getenv("MONGODB_DATABASE")]
        collection = mongo_db["documents"]
        document = DocumentGenerator(self.get_document_meta()).generate(rows)
        if document:
            collection.insert_one(document)
        return document

    def save_graph(self, project, file_path):
        """
        Save the graph to the database

        Parameters:
            project: the project name
            file_path: the file path

        Returns:
            graph_name: the name of the graph
        """

        mysql_db = mysql.get_db()
        cursor = mysql_db.cursor()
        cursor.callproc("graph_generate_table", (project,))
        cursor.execute("SELECT * FROM graph_table")
        rows = cursor.fetchall()

        arango_db = arango.db(
            os.getenv("ARANGODB_DATABASE"),
            os.getenv("ARANGODB_USERNAME"),
            os.getenv("ARANGODB_PASSWORD"),
        )

        graph_name = GraphGenerator(self.get_graph_meta(), arango_db).generate(
            rows, file_path
        )
        return graph_name
