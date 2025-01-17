import pytest
import base64
from datetime import datetime
from datetime import timezone

from cayennelpp.lpp_frame import LppFrame


@pytest.fixture
def frame():
    empty_frame = LppFrame()
    return empty_frame


@pytest.fixture
def frame_hlt():
    hlt = LppFrame()
    hlt.add_humidity(3, 45.6)
    hlt.add_load(1, 160.987)
    hlt.add_temperature(2, 12.3)
    return hlt


def test_empty_frame(frame):
    assert not frame.data
    assert len(frame) == 0
    assert not frame.bytes()


def test_init_invalid_data_nolist():
    with pytest.raises(Exception):
        LppFrame(42)


def test_init_invalid_data_item():
    with pytest.raises(Exception):
        LppFrame([0])


def test_frame_reset(frame):
    frame.add_digital_input(0, 1)
    assert len(frame) == 1
    frame.reset()
    assert len(frame) == 0


def test_frame_size(frame):
    assert frame.size == 0
    frame.add_digital_input(0, 1)
    assert frame.size == 3
    frame.add_digital_output(1, 42)
    assert frame.size == 6


def test_frame_maxsize(frame):
    frame.add_digital_input(0, 1)
    assert frame.maxsize == 0
    frame.maxsize = 6
    assert frame.maxsize == 6


def test_frame_invalid_maxsize(frame):
    frame.add_digital_input(0, 1)
    assert frame.maxsize == 0
    with pytest.raises(Exception):
        frame.maxsize = 1


def test_frame_exceed_maxsize(frame):
    frame.maxsize = 3
    with pytest.raises(Exception):
        frame.add_generic(0, 42)


def test_frame_from_bytes():
    # 03 67 01 10 05 67 00 FF = 27.2C + 25.5C
    buf = bytearray([0x03, 0x67, 0x01, 0x10, 0x05, 0x67, 0x00, 0xff])
    frame = LppFrame.from_bytes(buf)
    assert buf == frame.bytes()
    assert len(frame) == 2


def test_frame_from_bytes_base64():
    base64_str = "AYgILMMBiIMAAAACAAY="
    frame = LppFrame.from_bytes(base64.decodebytes(base64_str.encode('ascii')))
    assert len(frame) == 2


def test_add_digital_io(frame):
    frame.add_digital_input(0, 21)
    frame.add_digital_output(1, 42)
    assert len(frame) == 2
    assert int(frame.data[0].type) == 0
    assert int(frame.data[1].type) == 1


def test_add_analog_io(frame):
    frame.add_analog_input(0, 12.34)
    frame.add_analog_input(1, -12.34)
    frame.add_analog_output(0, 56.78)
    frame.add_analog_output(1, -56.78)
    assert len(frame) == 4
    assert int(frame.data[0].type) == 2
    assert int(frame.data[1].type) == 2
    assert int(frame.data[2].type) == 3
    assert int(frame.data[3].type) == 3


def test_add_sensors(frame):
    frame.add_luminosity(2, 12345)
    frame.add_presence(3, 1)
    frame.add_accelerometer(5, 1.234, -1.234, 0.0)
    frame.add_pressure(6, 1005.5)
    frame.add_barometer(6, 999.0)
    frame.add_gyrometer(7, 1.234, -1.234, 0.0)
    frame.add_gps(8, 1.234, -1.234, 0.0)
    assert len(frame) == 7
    assert int(frame.data[0].type) == 101
    assert int(frame.data[1].type) == 102
    assert int(frame.data[2].type) == 113
    assert int(frame.data[3].type) == 115
    assert int(frame.data[4].type) == 115
    assert int(frame.data[5].type) == 134
    assert int(frame.data[6].type) == 136


def test_add_voltage(frame):
    frame.add_voltage(0, 25.2)
    frame.add_voltage(1, 120.2)
    assert len(frame) == 2
    assert int(frame.data[0].type) == 116
    assert int(frame.data[1].type) == 116
    frame.add_voltage(2, -25)
    with pytest.raises(Exception):
        frame.bytes()


def test_add_load(frame):
    frame.add_load(0, -5.432)
    frame.add_load(1, 160.987)
    assert len(frame) == 2
    assert int(frame.data[0].type) == 122
    assert int(frame.data[1].type) == 122


def test_add_generic(frame):
    frame.add_generic(0, 4294967295)
    frame.add_generic(1, 1)
    assert len(frame) == 2
    assert int(frame.data[0].type) == 100
    assert int(frame.data[1].type) == 100


def test_add_unix_time(frame):
    frame.add_unix_time(0, datetime.now(timezone.utc).timestamp())
    frame.add_unix_time(1, 0)
    assert len(frame) == 2
    assert int(frame.data[0].type) == 133
    assert int(frame.data[1].type) == 133
    frame.bytes()


def test_add_temperature(frame):
    frame.add_temperature(2, 12.3)
    frame.add_temperature(3, -32.1)
    assert len(frame) == 2
    assert int(frame.data[0].type) == 103
    assert int(frame.data[1].type) == 103


def test_add_humidity(frame):
    frame.add_humidity(2, 12.3)
    frame.add_humidity(3, 45.6)
    frame.add_humidity(4, 78.9)
    assert len(frame) == 3
    assert int(frame.data[0].type) == 104
    assert int(frame.data[1].type) == 104
    assert int(frame.data[2].type) == 104


def test_print_empty_frame(frame):
    print(frame)


def test_print_data_frame(frame_hlt):
    print(frame_hlt)


def test_iterator(frame_hlt):
    counter = 0
    for val in frame_hlt:
        print(val)
        counter += 1
    assert counter == len(frame_hlt)


def test_get_by_type(frame_hlt):
    h_list = frame_hlt.get_by_type(104)
    assert len(h_list) == 1
    assert int(h_list[0].type) == 104
    l_list = frame_hlt.get_by_type(122)
    assert len(l_list) == 1
    assert int(l_list[0].type) == 122
    t_list = frame_hlt.get_by_type(103)
    assert len(t_list) == 1
    assert int(t_list[0].type) == 103
    p_list = frame_hlt.get_by_type(102)
    assert len(p_list) == 0


def test_get_by_type_invalid(frame_hlt):
    p_list = frame_hlt.get_by_type(102)
    assert len(p_list) == 0
    i_list = frame_hlt.get_by_type(666)
    assert len(i_list) == 0
