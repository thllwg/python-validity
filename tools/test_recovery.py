#!/usr/bin/env python3
"""Hardware-free unit test for the crash-only device-error classification.

Exercises validitysensor.usb.is_fatal_device_error(): only a dead USB transport
(usb.core.USBError, incl. its Errno-tagged subclasses) or a desynced protocol
stream (TlsProtocolError) count as fatal (-> supervised restart). A normal
no-match, a cancellation, and unrelated exceptions must NOT be fatal.

Run from the repo root:  python3 tools/test_recovery.py
Does NOT touch fatal_device_exit() (it calls os._exit()).
"""

import os
import sys

# Prefer the in-repo validitysensor over any deployed copy in site-packages, so
# this test always exercises the working-tree code (running the script puts
# tools/ on sys.path[0], not the repo root).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from usb.core import USBError

from validitysensor.usb import (
    CancelledException,
    TlsProtocolError,
    is_fatal_device_error,
)


def main():
    # Fatal: dead USB transport (bare and Errno-tagged, e.g. NoDeviceError [19]).
    assert is_fatal_device_error(USBError('x')) is True
    assert is_fatal_device_error(USBError(19, 'No such device')) is True

    # Fatal: desynced TLS protocol stream.
    assert is_fatal_device_error(
        TlsProtocolError('Unexpected TLS version 4 0')) is True

    # Non-fatal: cancellation, normal no-match, and unrelated errors.
    assert is_fatal_device_error(CancelledException()) is False
    assert is_fatal_device_error(
        Exception('Finger not recognized: 04000200db')) is False
    assert is_fatal_device_error(ValueError('x')) is False

    print('OK: all is_fatal_device_error assertions passed')


if __name__ == '__main__':
    main()
