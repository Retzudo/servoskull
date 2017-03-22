class DottedDict(dict):
    """A class that let's the user access the keys of
    a dictionary like an object's properties.

    Can be used to mock an instance of any other class.
    E. g. discord.py Messages:
    A Message object has the property `content`.

        message = DottedDict(content='asdf')

    The `message` dict's key content can now be access by dot notation as
    if it were a regular Message object.

        message.content == 'asdf'
    """
    def __getattr__(self, item):
        return self.get(item)