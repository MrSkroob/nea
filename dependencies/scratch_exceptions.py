class TooManySprites(Exception):
    def __init__(self):
        message = "Only 1 sprite or stage per script file"
        super().__init__(message)


class CouldNotFindSprite(Exception):
    def __init__(self, sprite_name: str):
        message = f"Could not find a sprite or stage with the name: {sprite_name}"
        super().__init__(message)


class NoReturn(Exception):
    def __init__(self):
        message = "Scratch limitation - procedures only"
        super().__init__(message)


class MissingSpriteOrStudio(Exception):
    def __init__(self,):
        message = "Couldn't find Sprite or Studio object"
        super().__init__(message)


class UnsupportedMethod(Exception):
    def __init__(self):
        message = "Couldn't find an equivalent Scratch block for this method"
        super().__init__(message)


class UnsupportedFeature(Exception):
    def __init__(self, feature_name: str):
        message = f"Scratch limitation - Scratch does not support '{feature_name}'"
        super().__init__(message)


class NoAnonymousProcedures(Exception):
    def __init__(self):
        message = "Scratch limitation - procedures must have names!"
        super().__init__(message)


class MissingArgumentType(Exception):
    def __init__(self):
        message = "Please give a type for each argument: e.g. : int"
        super().__init__(message)   


class InvalidArgumentType(Exception):
    def __init__(self, arg_type: str):
        message = f"Scratch limitation - scratch does not support the type '{arg_type}'"
        super().__init__(message) 
        