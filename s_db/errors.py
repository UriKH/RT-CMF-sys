# --------------------------- Database Errors ---------------------------
class DBError(Exception):
    pass


class ConstantDoesNotExist(DBError):
    message_prefix = 'Constant does not exist: '
    pass


class FunctionAlreadyExists(DBError):
    pass


class FunctionDoesNotExist(DBError):
    pass


class ConstantAlreadyExists(DBError):
    pass


class NoSuchInspirationFunction(DBError):
    pass


# --------------------------- JSON Errors ---------------------------
class JSONError(Exception):
    default_msg = """Invalid JSON file, please check the syntax of the file:
    {
        "command": <"update" or "replace" or "insert"">,
        "data":
        [   
            {
                "constant": <constant>,
                "data": {
                    "<type config>": <type class>
                    "<data config>": <data>
                    "extras": {<kwargs>}
                }
            },
            {...}
        ]
    }
    """
    pass
