from auth.domain.errors import Error


class ApplicationError(Error): ...


class AuthenticationError(ApplicationError): ...


class DoesNotExists(ApplicationError): ...
