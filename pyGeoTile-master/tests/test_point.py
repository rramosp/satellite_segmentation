import pytest

from pygeotile.meta import ORIGIN_SHIFT
from pygeotile.point import Point


@pytest.fixture(scope='module')
def latitude_longitude():
    return 47.0, 8.0


def test_from_coordinates(latitude_longitude):
    latitude, longitude = latitude_longitude
    point = Point.from_latitude_longitude(latitude=latitude, longitude=longitude)
    assert point.latitude_longitude == latitude_longitude


def test_from_meters(chicago_latitude_longitude, chicago_meters):
    meter_x, meter_y = chicago_meters

    point = Point.from_meters(meter_x=meter_x, meter_y=meter_y)

    assert point.meters == pytest.approx(chicago_meters, abs=0.1)
    assert point.latitude_longitude == pytest.approx(chicago_latitude_longitude, abs=0.1)


def test_from_pixel_chicago(chicago_latitude_longitude, chicago_pixel, chicago_zoom):
    pixel_x, pixel_y = chicago_pixel

    point = Point.from_pixel(pixel_x=pixel_x, pixel_y=pixel_y, zoom=chicago_zoom)

    assert point.pixels(zoom=chicago_zoom) == chicago_pixel
    assert point.latitude_longitude == pytest.approx(chicago_latitude_longitude, abs=0.2)


@pytest.mark.parametrize("pixel_x, pixel_y,zoom, expected", [
    (0, 0, 1, (-ORIGIN_SHIFT, ORIGIN_SHIFT)),
    (256, 0, 1, (0, ORIGIN_SHIFT)),
    (512, 0, 1, (ORIGIN_SHIFT, ORIGIN_SHIFT)),
    (0, 256, 1, (-ORIGIN_SHIFT, 0)),
    (256, 256, 1, (0, 0)),
    (512, 256, 1, (ORIGIN_SHIFT, 0)),
    (0, 512, 1, (-ORIGIN_SHIFT, -ORIGIN_SHIFT)),
    (256, 512, 1, (0, -ORIGIN_SHIFT)),
    (512, 512, 1, (ORIGIN_SHIFT, -ORIGIN_SHIFT)),
])
def test_pixels_to_meters(pixel_x, pixel_y, zoom, expected):
    point = Point.from_pixel(pixel_x=pixel_x, pixel_y=pixel_y, zoom=zoom)

    assert point.meters == pytest.approx(expected, abs=0.1)
    assert point.pixels(zoom=zoom) == (pixel_x, pixel_y)


@pytest.mark.parametrize("pixel_x, pixel_y,zoom, expected", [
    (0, 0, 1, (85.05, -180.0)),
    (256, 0, 1, (85.05, 0)),
    (512, 0, 1, (85.05, 180.0)),
    (0, 256, 1, (0, -180.0)),
    (256, 256, 1, (0.0, 0.0)),
    (512, 256, 1, (0.0, 180.0)),
    (0, 512, 1, (-85.05, -180.0)),
    (256, 512, 1, (-85.05, 0.0)),
    (512, 512, 1, (-85.05, 180.0)),
])
def test_pixels_to_latitude_longitude(pixel_x, pixel_y, zoom, expected):
    point = Point.from_pixel(pixel_x=pixel_x, pixel_y=pixel_y, zoom=zoom)

    assert point.latitude_longitude == pytest.approx(expected, abs=0.1)
    assert point.pixels(zoom=zoom) == (pixel_x, pixel_y)


@pytest.mark.parametrize("meter_x, meter_y, expected", [
    (-ORIGIN_SHIFT, ORIGIN_SHIFT, (85.05, -180.0)),
    (0, ORIGIN_SHIFT, (85.05, 0)),
    (ORIGIN_SHIFT, ORIGIN_SHIFT, (85.05, 180.0)),
    (-ORIGIN_SHIFT, 0, (0, -180.0)),
    (0, 0, (0.0, 0.0)),
    (ORIGIN_SHIFT, 0, (0.0, 180.0)),
    (-ORIGIN_SHIFT, -ORIGIN_SHIFT, (-85.05, -180.0)),
    (0, -ORIGIN_SHIFT, (-85.05, 0.0)),
    (ORIGIN_SHIFT, -ORIGIN_SHIFT, (-85.05, 180.0)),
])
def test_meters_to_pixels(meter_x, meter_y, expected):
    point = Point.from_meters(meter_x=meter_x, meter_y=meter_y)

    assert point.latitude_longitude == pytest.approx(expected, abs=0.1)
    assert point.meters == pytest.approx((meter_x, meter_y), abs=0.1)


@pytest.mark.parametrize("longitude", [-180.1, -200, -181, 181, 180.01, 200])
def test_assert_longitude(longitude):
    latitude = 0.0

    with pytest.raises(AssertionError) as assertion_info:
        _ = Point.from_latitude_longitude(latitude=latitude, longitude=longitude)

    assert 'Longitude needs to be a value between -180.0 and 180.0.' in str(assertion_info.value)


@pytest.mark.parametrize("longitude", [180, -180, 180.0, -180.0, 0, 0.0, 90])
def test_no_assert_longitude(longitude):
    latitude = 10.0
    _ = Point.from_latitude_longitude(latitude=latitude, longitude=longitude)
    assert "No assertion raise :)"


@pytest.mark.parametrize("latitude", [-90.1, -91, 90.1, 91, 200, -200])
def test_assert_latitude(latitude):
    longitude = 0.0

    with pytest.raises(AssertionError) as assertion_info:
        _ = Point.from_latitude_longitude(latitude=latitude, longitude=longitude)

    assert 'Latitude needs to be a value between -90.0 and 90.0.' in str(assertion_info.value)


@pytest.mark.parametrize("latitude", [90, -90, 90.0, -90.0, 0, 0.0, 90])
def test_no_assert_latitude(latitude):
    longitude = 10.0
    _ = Point.from_latitude_longitude(latitude=latitude, longitude=longitude)
    assert "No assertion raise :)"


assert_pixels = [(-10, 1), (-0.1, 1), (512.1, 1), (1024.1, 2)]
no_assert_pixels = [(10, 1), (0.1, 1), (512.0, 1), (1024.0, 2)]


@pytest.mark.parametrize("pixel_x, zoom", assert_pixels)
def test_assert_pixel_x(pixel_x, zoom):
    pixel_y = 1

    with pytest.raises(AssertionError) as assertion_info:
        _ = Point.from_pixel(pixel_x=pixel_x, pixel_y=pixel_y, zoom=zoom)

    assert 'Point X needs to be a value between 0 and (2^zoom) * 256.' in str(assertion_info.value)


@pytest.mark.parametrize("pixel_x, zoom", no_assert_pixels)
def test_no_assert_pixel_x(pixel_x, zoom):
    pixel_y = 10.0
    _ = Point.from_pixel(pixel_x=pixel_x, pixel_y=pixel_y, zoom=zoom)
    assert "No assertion raise :)"


@pytest.mark.parametrize("pixel_y, zoom", assert_pixels)
def test_assert_pixel_y(pixel_y, zoom):
    pixel_x = 1

    with pytest.raises(AssertionError) as assertion_info:
        _ = Point.from_pixel(pixel_x=pixel_x, pixel_y=pixel_y, zoom=zoom)

    assert 'Point Y needs to be a value between 0 and (2^zoom) * 256.' in str(assertion_info.value)


@pytest.mark.parametrize("pixel_y, zoom", no_assert_pixels)
def test_no_assert_pixel_y(pixel_y, zoom):
    pixel_x = 10.0
    _ = Point.from_pixel(pixel_x=pixel_x, pixel_y=pixel_y, zoom=zoom)
    assert "No assertion raise :)"


assert_meters = [-0.1 - ORIGIN_SHIFT, -200 - ORIGIN_SHIFT, ORIGIN_SHIFT + 0.1, 6378137000]
no_assert_meters = [-ORIGIN_SHIFT, -ORIGIN_SHIFT + 0.1, ORIGIN_SHIFT, ORIGIN_SHIFT - 0.1]


@pytest.mark.parametrize("meter_x", assert_meters)
def test_assert_meter_x(meter_x):
    meter_y = 0.0

    with pytest.raises(AssertionError) as assertion_info:
        _ = Point.from_meters(meter_x=meter_x, meter_y=meter_y)

    assert 'Meter X needs to be a value between -{0} and {0}.'.format(ORIGIN_SHIFT) in str(assertion_info.value)


@pytest.mark.parametrize("meter_x", no_assert_meters)
def test_no_assert_meter_x(meter_x):
    meter_y = 10.0
    _ = Point.from_meters(meter_x=meter_x, meter_y=meter_y)
    assert "No assertion raise :)"


@pytest.mark.parametrize("meter_y", assert_meters)
def test_assert_meter_y(meter_y):
    meter_x = 0.0

    with pytest.raises(AssertionError) as assertion_info:
        _ = Point.from_meters(meter_x=meter_x, meter_y=meter_y)

    assert 'Meter Y needs to be a value between -{0} and {0}.'.format(ORIGIN_SHIFT) in str(assertion_info.value)


@pytest.mark.parametrize("meter_y", no_assert_meters)
def test_no_assert_meter_y(meter_y):
    meter_x = 10.0
    _ = Point.from_meters(meter_x=meter_x, meter_y=meter_y)
    assert "No assertion raise :)"
