import asyncio
import datetime
import logging

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, AuthorizationStatus, RemoteStartStopStatus, DataTransferStatus, DiagnosticsStatus

logging.basicConfig(level=logging.INFO)

class ChargePoint(cp):
    async def send_boot_notification(self):
        request = call.BootNottificationPayload(
            charge_point_model="Optimus", charge_point_vendor="The Mobility House"
        )

        response1 = await self.call(request)
        if response1.status == RegistrationStatus.accepted:
            print("Connected to central system.")


    async def send_authorize(self):
        request = call.AuthorizePayload(
            id_tag="ggh"
        )
        response = await self.call(request)
        if response.id_tag_info['status'] == AuthorizationStatus.accepted:
            print("charger Authorize.")


    async def send_remote_start_transaction(self):
        request = call.RemoteStartTransactionPayload(
            id_tag='aaaa'
        )
        response = await self.call(request)
        if response.status== RemoteStartStopStatus.accepted:
            print("remote transaction start")


    async def send_data_transfer(self):
        request = call.DataTransferPayload(
            vendor_id='aaaa'
        )
        response = await self.call(request)
        if response.status == DataTransferStatus.accepted:
             print("data received successful")



    async def send_diagnostics_status_notification(self):
        request = call.DiagnosticsStatusNotificationPayload(
            status = DiagnosticsStatus.idle
        )
        response = await self.call(request)
        print("data received successful", response)
   







    # async def send_meter_values(self):
    #     request = call.MeterValuesPayload(
    #         connector_id = 123,
    #         meter_value:List = field(default_factory=['default']) 
    #     )
    #     response = await self.call(request)

    #     print("data received successful", response)

    #     if response == 'pass':
    #          print("charger are not performing")

   



async def main():
    async with websockets.connect(
        "ws://localhost:5353/CP_1", subprotocols=["ocpp1.6"]
    ) as ws:

        cp = ChargePoint("CP_1", ws)

        await asyncio.gather(cp.start(), cp.send_boot_notification())
        # await asyncio.gather(cp.start(), cp.send_authorize())
        # await asyncio.gather(cp.start(), cp.send_remote_start_transaction())
        # await asyncio.gather(cp.start(), cp.send_data_transfer())
        # await asyncio.gather(cp.start(), cp.send_diagnostics_status_notification())

       
if __name__ == "__main__":
    # asyncio.run() is used when running this example with Python >= 3.7v
    asyncio.run(main())
