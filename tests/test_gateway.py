import asyncio
import unittest

from bacpypes3.apdu import ErrorRejectAbortNack
from bacpypes3.app import Application
from bacpypes3.local.device import DeviceObject
from bacpypes3.local.networkport import NetworkPortObject
from bacpypes3.pdu import Address

from home_utilities.server import make_application


class GatewayTest(unittest.IsolatedAsyncioTestCase):
    async def test_directed_discovery_read_and_denied_write(self):
        address = Address("127.0.0.1:48762")
        server = make_application("127.0.0.1/32:48762")
        self.addCleanup(server.close)
        client = Application.from_object_list(
            [
                DeviceObject(objectIdentifier=("device", 6013), objectName="TEST_CLIENT"),
                NetworkPortObject(
                    "127.0.0.1/32:48763",
                    objectIdentifier=("network-port", 1),
                    objectName="Test port",
                ),
            ]
        )
        self.addCleanup(client.close)

        responses = await client.who_is(6012, 6012, address, timeout=2)
        self.assertEqual(len(responses), 1)
        self.assertEqual(str(responses[0].iAmDeviceIdentifier), "device,6012")

        async def read(object_id, property_id):
            return await asyncio.wait_for(client.read_property(address, object_id, property_id), 3)

        self.assertEqual(await read("device,6012", "object-name"), "HOME_UTILITIES")
        self.assertEqual(len(await read("device,6012", "object-list")), 16)
        self.assertEqual(await read("analog-value,1", "present-value"), 12.0)
        self.assertEqual(str(await read("analog-value,1", "units")), "us-gallons")
        self.assertEqual(str(await read("binary-value,3", "present-value")), "inactive")
        with self.assertRaises(ErrorRejectAbortNack) as result:
            await asyncio.wait_for(
                client.write_property(address, "analog-value,1", "present-value", 99.0),
                3,
            )
        self.assertEqual(str(result.exception.errorCode), "write-access-denied")
        self.assertEqual(await read("analog-value,1", "present-value"), 12.0)
