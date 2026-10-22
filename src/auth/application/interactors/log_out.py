from auth.application.interfaces.client_session_transport import ClientSessionTransport
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.application.interfaces.transaction_manager import TransactionManager


class LogOutInteractor:
    def __init__(
        self,
        session_data_gateway: SessionDataGateway,
        client_session_transport: ClientSessionTransport,
        session_token_hasher: SessionTokenHasher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._session_data_gateway = session_data_gateway
        self._client_session_transport = client_session_transport
        self._session_token_hasher = session_token_hasher
        self._transaction_manager = transaction_manager

    async def __call__(self) -> None:
        token = await self._client_session_transport.get_session()
        if token is not None:
            session = await self._session_data_gateway.read_by_token_hash(
                self._session_token_hasher.hash(token)
            )
            if session is not None:
                await self._session_data_gateway.delete(session)
                await self._transaction_manager.commit()

        await self._client_session_transport.clear_session()
