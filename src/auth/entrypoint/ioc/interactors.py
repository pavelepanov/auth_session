from dishka import Provider, Scope, provide

from auth.application.interactors.admin_hello_world import AdminHelloWorldInteractor
from auth.application.interactors.log_in import LogInInteractor
from auth.application.interactors.log_out import LogOutInteractor
from auth.application.interactors.sign_up import SignUpInteractor
from auth.application.interactors.user_hello_world import UserHelloWorldInteractor
from auth.application.interactors.verification import VerificationInteractor


class InteractorProvider(Provider):
    scope = Scope.REQUEST

    log_in = provide(LogInInteractor)
    log_out = provide(LogOutInteractor)
    sign_up = provide(SignUpInteractor)
    user_hello_world = provide(UserHelloWorldInteractor)
    admin_hello_world = provide(AdminHelloWorldInteractor)
    verification = provide(VerificationInteractor)
