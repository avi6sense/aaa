import asyncio
import keyword
import logging
from ast import List
from dataclasses import field
from datetime import datetime
from operator import call
from typing import Optional

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys

    sys.exit(1)

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import (
    Action,
    AuthorizationStatus,
    ChargePointErrorCode,
    ChargePointStatus,
    ConfigurationStatus,
    DataTransferStatus,
    DiagnosticsStatus,
    RegistrationStatus,
    RemoteStartStopStatus,
    ReservationStatus
)

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(Action.BootNotification)
    def on_boot_notification(
        self, charge_point_vendor: str, charge_point_model: str, **kwargs
    ):
        return call_result.BootNotificationPayload(
            current_time='2023-01-13T05:10:41Z',
            interval=10,
            status=RegistrationStatus.accepted,
        )

    @on(Action.StatusNotification)
    def on__status_notification(
        self,
        connector_id: int,
        error_code: ChargePointErrorCode,
        status: ChargePointStatus, ** kwargs
    ): return call_result.StatusNotificationPayload(

    )

    @on(Action.Heartbeat)
    def on__heartbeat(
        self, **kwargs
    ): return call_result.HeartbeatPayload(
        current_time='2023-01-13T05:10:41Z'
    )

    @on(Action.Authorize)
    def on_authorize(
        self,  id_tag: str, **kwargs
    ): return call_result.AuthorizePayload(

        {"status": AuthorizationStatus.accepted}
    )

    @on(Action.StartTransaction)
    def on_send_start_transaction(
        self,
        connector_id: int,
        id_tag: str,
        meter_start: int,
        timestamp: str,
        reservation_id: Optional[int] = None,
        **kwargs
    ): return call_result.StartTransactionPayload(
        transaction_id=123456,
        id_tag_info={"status": AuthorizationStatus.accepted}
    )

    @on(Action.StopTransaction)
    def on_send_stop_transaction(
        self,
        meter_stop: int,
        timestamp: str,
        transaction_id: int, **kwargs
    ): return call_result.StopTransactionPayload(

    )

    @on(Action.MeterValues)
    def on_send_meter_values(
        self,
        connector_id: int,
        meter_value: List = field(default_factory=list),
        **kwargs
    ): return call_result.MeterValuesPayload(

    )

    @on(Action.ChangeConfiguration)
    def on_send_change_configuration(
        self,
        status: ConfigurationStatus,
        **kwargs
    ): return call_result.ChangeConfigurationPayload(
        {"status": ConfigurationStatus.accepted}

    )

    @on(Action.GetConfiguration)
    def on_send_get_configuration(
        self,
        configuration_key: Optional[List] = None,
        unknown_key: Optional[List] = None,
        **kwargs
    ): return call_result.GetConfigurationPayload(
    )

    @on(Action.GetConfiguration)
    def on_send_get_configuration(
        self,
        configuration_key: Optional[List] = None,
        unknown_key: Optional[List] = None,
        **kwargs
    ): return call_result.GetConfigurationPayload(
    )

    @on(Action.RemoteStartTransaction)
    def on_send_remote_start_transaction(
        self,  id_tag: str, **kwargs
    ): return call_result.RemoteStartTransactionPayload(

        status=RemoteStartStopStatus.accepted
    )

    @on(Action.ReserveNow)
    def on_send_remote_now(
        self,
        connector_id: int,
        expiry_date: str,
        id_tag: str,
        reservation_id: int,
        **kwargs
    ): return call_result.ReserveNowPayload(
        status=ReservationStatus.rejected
    )

    @on(Action.DataTransfer)
    def on_send_data_transfer(
        self,  vendor_id: str, **kwargs
    ): return call_result.DataTransferPayload(

        status=DataTransferStatus.accepted
    )

    # @on(Action.DiagnosticsStatusNotification)
    # def on_send_diagnostics_status_notification(
    #     self,  status=DiagnosticsStatus, **kwargs
    # ):
    #     if (status == "Idle"):

    #         print('charger are not working')

    #     return call_result.DiagnosticsStatusNotificationPayload(

    #     )


async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect, "0.0.0.0", 5353, subprotocols=["ocpp1.6"]
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


if __name__ == "__main__":
    # asyncio.run() is used when running this example with Python >= 3.7v
    asyncio.run(main())
