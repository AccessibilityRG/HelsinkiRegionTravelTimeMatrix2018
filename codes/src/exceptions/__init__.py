class NotParameterGivenException(Exception):
    """
    Thrown when some paramenters have not been given.
    """

    def __init__(self, message):
        super(NotParameterGivenException, self).__init__(message)


class IncorrectGeometryTypeException(Exception):
    """
    The input json file must be a multipoint geometry type, in case the file do not accomplish with the geometry type
    then the application throw this exception.
    """

    def __init__(self, message):
        super(IncorrectGeometryTypeException, self).__init__(message)