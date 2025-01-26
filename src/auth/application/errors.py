from auth.domain.errors import Error


class ApplicationError(Error): ...


class AuthenticationError(ApplicationError): ...


class DoesNotExists(ApplicationError): ...


class AlreadyExists(ApplicationError): ...


class InvalidPassword(ApplicationError): ...
