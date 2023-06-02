import os
import json
from uuid import uuid4
from copy import deepcopy
from generators.data_generator import DataGenerator


class GraphGenerator(DataGenerator):
    """
    This class is responsible for generating the graph from meta description.
    """

    def __init__(self, meta, arango_db):
        self.meta = meta
        del self.meta["_id"]
        self.arango_db = arango_db

    def generate(self, rows, file_path):
        """
        Generate the graph from the meta description and the rows.

        Parameters:
            rows: the rows from the database
            file_path: path for the graph files to be written to

        Returns:
            graph_name: the name of the graph
        """

        if rows == None or len(rows) == 0:
            return None

        graph_name = rows[0][self.meta["graph_name"]]
        _id = uuid4()

        graph = self.arango_db.create_graph(f"{graph_name}_{_id}")
        vertex_collections = {}
        for vertex_name in self.meta["vertex_collections"]:
            vertex_collections[vertex_name] = graph.create_vertex_collection(
                f"{graph_name}_{vertex_name}_{_id}"
            )

        edge_definitions = {}
        for edge_name, edge_definition in self.meta["edge_definitions"].items():
            edge_definitions[edge_name] = graph.create_edge_definition(
                edge_collection=f"{graph_name}_{edge_name}_{_id}",
                from_vertex_collections=list(
                    map(
                        lambda x: f"{graph_name}_{x}_{_id}",
                        edge_definition["from_vertex_collections"],
                    )
                ),
                to_vertex_collections=list(
                    map(
                        lambda x: f"{graph_name}_{x}_{_id}",
                        edge_definition["to_vertex_collections"],
                    )
                ),
            )

        for row in rows:
            for vertex_name, vertex_collection in vertex_collections.items():
                data_list = self.meta["vertex_collections"][vertex_name]["data"]
                for data in data_list:
                    if not vertex_collection.get({"_key": str(row[data["_key"]])}):
                        vertex_collection.insert(
                            self.fill_meta_description(
                                data["template"], row, data["props"]
                            )
                        )

            for edge_name, edge_definition in edge_definitions.items():
                data_list = self.meta["edge_definitions"][edge_name]["data"]
                for data in data_list:
                    if not edge_definition.get({"_key": str(row[data["_key"]])}):
                        row_with_vertex_names = {
                            **row,
                            "from_vertex_collection": f"{graph_name}_{data['from_vertex_collection']}_{_id}",
                            "to_vertex_collection": f"{graph_name}_{data['to_vertex_collection']}_{_id}",
                        }
                        edge_definition.insert(
                            self.fill_meta_description(
                                data["template"], row_with_vertex_names, data["props"]
                            )
                        )

        documents = {}
        for collection in {**vertex_collections, **edge_definitions}.values():
            cursor = collection.all()
            sub_documents = []
            for result in cursor:
                sub_documents.append(result)
            documents[collection.name] = sub_documents

        self.generate_files(file_path, documents)

        return graph.name

    def fill_meta_description(self, template, row, columns):
        """
        Fill the meta description with the data from the row.

        Parameters:
            template: the template from the meta description
            row: the row from the database
            columns: the columns from the database
        """

        filtered_row = {column: row[column] for column in columns}
        document = deepcopy(template)

        for row_key, row_value in filtered_row.items():
            for meta_key, meta_value in document.items():
                document[meta_key] = str(
                    self.replace_placeholder(meta_value, row_key, row_value)
                )

        return document

    def replace_placeholder(self, meta_value, row_key, row_value):
        """
        Replace the placeholder in the meta description with the data from the row.

        Parameters:
            meta_value: the value from the meta description
            row_key: the key from the row
            row_value: the value from the row
        """

        if f"<<<{row_key}>>>" == meta_value:
            return row_value
        elif type(meta_value) is str and f"<<<{row_key}>>>" in meta_value:
            return meta_value.replace(f"<<<{row_key}>>>", str(row_value))

        return meta_value

    def generate_files(self, file_path, documents):
        """
        Write generated document to the file system.

        Parameters:
            file_path: path for the graph files to be written to
            documents: the generated documents
        """

        os.makedirs(file_path, exist_ok=True)
        for document_name, document_value in documents.items():
            with open(f"{file_path}/{document_name}.json", "w") as file:
                file.write(json.dumps(document_value, indent=4, default=str))
