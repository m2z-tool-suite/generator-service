from copy import deepcopy
from generators.data_generator import DataGenerator


class DocumentGenerator(DataGenerator):
    """
    This class is responsible for generating the document from meta description.
    """

    def __init__(self, meta):
        self.meta = meta
        del self.meta["_id"]

    @property
    def meta_keys(self):
        return list(self.meta.keys())

    def generate(self, rows):
        """
        Generate the document from the meta description and the rows.

        Parameters:
            rows: the rows from the database
        """

        if rows == None or len(rows) == 0:
            return None

        root_key = self.meta_keys[0]
        root = self.fill_meta_description(
            root_key, rows[0], self.meta[root_key]["props"]
        )

        for row in rows:
            items = [root]
            for key, value in self.meta.items():
                if key == root_key:
                    continue

                items.append(self.fill_meta_description(key, row, value["props"]))

            for i in range(1, len(items)):
                items[i] = self.add_child_if_not_exists(
                    items[i - 1], items[i], self.meta_keys[i]
                )

        return items[0]

    def fill_meta_description(self, meta_type, row, columns):
        """
        Fill the meta description with the data from the row.

        Parameters:
            meta_type: the type of the meta description
            row: the row from the database
            columns: the columns from the database
        """

        data = {column: row[column] for column in columns}
        selected_meta = deepcopy(self.meta[meta_type])["template"]

        for key, value in data.items():
            for meta_key, meta_value in selected_meta.items():
                selected_meta[meta_key] = self.replace_placeholder(
                    meta_value, key, value
                )

                # this is going only one level deep, if we need more levels, we need to refactor this
                if type(meta_value) is dict:
                    for meta_key_nested, meta_value_nested in meta_value.items():
                        selected_meta[meta_key][
                            meta_key_nested
                        ] = self.replace_placeholder(meta_value_nested, key, value)

        return selected_meta

    def replace_placeholder(self, meta_value, key, value):
        """
        Replace the placeholder in the meta description with the data from the row.

        Parameters:
            meta_value: the value from the meta description
            key: the key from the row
            value: the value from the row
        """

        if f"<<<{key}>>>" == meta_value:
            return value
        elif type(meta_value) is str and f"<<<{key}>>>" in meta_value:
            return meta_value.replace(f"<<<{key}>>>", str(value))

        return meta_value

    def add_child_if_not_exists(self, parent, child, key):
        """
        Add the child to the parent if it does not exist.

        Parameters:
            parent: the parent
            child: the child
            key: the key of the child
        """

        exists = False
        for c in parent[key]:
            if c["id"] == child["id"]:
                exists = True
                child = c
                break

        if not exists and child["id"] != None:
            parent[key].append(child)

        return child
