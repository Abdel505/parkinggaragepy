import sys
import os
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mock import GPIO
from mock.SDL_DS3231 import SDL_DS3231
from src.parking_garage import ParkingGarage
from src.parking_garage import ParkingGarageError

class TestParkingGarage(TestCase):

    @patch.object(GPIO, "input")
    def test_check_occupancy_true(self, distance_sensor: Mock):
        # This is an example of test where I want to mock the GPIO.input() function
        distance_sensor.return_value = True
        garage = ParkingGarage()
        outcome = garage.check_occupancy(ParkingGarage.INFRARED_PIN1)
        self.assertTrue(outcome)
    def test_check_occupancy_raises_error(self):
        garage = ParkingGarage()
        self.assertRaises(ParkingGarageError, garage.check_occupancy, garage.LED_PIN)

    @patch.object(GPIO, "input")
    def test_get_number_occupied_spots(self, distance_sensor: Mock):
        distance_sensor.side_effect = [True, False, True] 
        garage = ParkingGarage()
        number_occupied_spots = garage.get_number_occupied_spots()
        self.assertEqual(2, number_occupied_spots)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee(self, rtc: Mock):
        rtc.return_value = datetime(2025, 11, 20, 15, 30)
        garage = ParkingGarage()
        entry_time = datetime(2025, 11, 20, 12, 30)
        fee = garage.calculate_parking_fee(entry_time)
        self.assertEqual(7.5, fee)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee_in_weekend(self, rtc: Mock):
        rtc.return_value = datetime(2025, 12, 20, 15, 30)
        garage = ParkingGarage()
        entry_time = datetime(2025, 12, 20, 12, 30)
        fee = garage.calculate_parking_fee(entry_time)
        self.assertEqual(9.375, fee)