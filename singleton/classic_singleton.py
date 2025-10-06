class Singleton:
    """
    Classic Singleton using __new__.

    Note: __init__ runs every time Singleton() is called, even though
    __new__ returns the same instance. This can cause re-initialization issues.

    To prevent re-initialization, see the commented class below.
    """

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


# Alternative implementation to prevent re-initialization:
#
# class Singleton:
#     """Singleton with re-initialization prevention."""
#
#     _instance = None
#
#     def __new__(cls):
#         if not cls._instance:
#             cls._instance = super().__new__(cls)
#             cls._instance._initialized = False
#         return cls._instance
#
#     def __init__(self):
#         if not self._initialized:
#             # Your initialization code here
#             self._initialized = True
