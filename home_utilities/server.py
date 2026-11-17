"""Read-only BACnet/IP server for simulated commissioning."""

import argparse
import asyncio
import logging
import os
from ipaddress import IPv4Interface

from bacpypes3.app import Application
from bacpypes3.errors import ExecutionError
from bacpypes3.local.analog import AnalogValueObject
from bacpypes3.local.binary import BinaryValueObject
from bacpypes3.local.device import DeviceObject
from bacpypes3.local.networkport import NetworkPortObject

from .points import WATER_ANALOGS, WATER_BINARIES

DEVICE_INSTANCE = 6012
DEVICE_NAME = "HOME_UTILITIES"
LOG = logging.getLogger(__name__)


class ReadOnlyApplication(Application):
    async def do_WritePropertyRequest(self, apdu):
        raise ExecutionError("property", "writeAccessDenied")

    async def do_WritePropertyMultipleRequest(self, apdu):
        raise ExecutionError("property", "writeAccessDenied")


def make_application(address: str) -> ReadOnlyApplication:
    device = DeviceObject(
        objectIdentifier=("device", DEVICE_INSTANCE),
        objectName=DEVICE_NAME,
        description="SIMULATED commissioning data",
    )
    network_port = NetworkPortObject(
        address,
        objectIdentifier=("network-port", 1),
        objectName="NetworkPort-1",
    )
    analogs = [
        AnalogValueObject(
            objectIdentifier=("analogValue", point.instance),
            objectName=point.name,
            description=f"SIMULATED: {point.description}",
            presentValue=point.sample,
            units=point.units,
            eventState="normal",
            outOfService=False,
            reliability="unreliableOther",
            covIncrement=0.01,
        )
        for point in WATER_ANALOGS
    ]
    binaries = [
        BinaryValueObject(
            objectIdentifier=("binaryValue", instance),
            objectName=name,
            description=f"SIMULATED: {description}",
            presentValue="inactive",
            eventState="normal",
            outOfService=False,
            reliability="noFaultDetected" if instance == 3 else "unreliableOther",
        )
        for instance, name, description in WATER_BINARIES
    ]
    return ReadOnlyApplication.from_object_list([device, network_port, *analogs, *binaries])


def bind_address(value: str) -> str:
    interface, separator, port = value.partition(":")
    if "/" not in interface:
        raise argparse.ArgumentTypeError("include the IPv4 subnet prefix")
    try:
        interface = IPv4Interface(interface)
        port = int(port) if separator else 47808
        if interface.ip.is_unspecified or interface.ip.is_multicast or not 1 <= port <= 65535:
            raise ValueError
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected a specific IPv4 address/prefix[:port]") from error
    return f"{interface}:{port}"


async def serve(address: str) -> None:
    app = make_application(address)
    LOG.info("Starting %s device %d on %s (SIMULATED)", DEVICE_NAME, DEVICE_INSTANCE, address)
    try:
        await asyncio.Future()
    finally:
        app.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", type=bind_address, default=os.getenv("BACNET_ADDRESS", "127.0.0.1/32"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    try:
        asyncio.run(serve(args.address))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
