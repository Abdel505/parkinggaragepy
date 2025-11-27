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
    # it will use the mock instead of the real method
    def test_check_occupancy_true(self, distance_sensor: Mock):  
        distance_sensor.return_value = True 
        garage = ParkingGarage()
        outcome = garage.check_occupancy(garage.INFRARED_PIN2)
        self.assertTrue(outcome)# check that outcome is True if False test fails

    def test_check_occupancy_raises_error(self):
        garage = ParkingGarage()
        self.assertRaises(ParkingGarageError, garage.check_occupancy, garage.LED_PIN)

    @patch.object(GPIO, "input") 
    def test_check_number_occupied_spots_no_occupied(self, distance_sensor: Mock):
        distance_sensor.side_effect = [True, True, False]
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
    def test_calcuate_parking_fee_in_weekend(self, rtc: Mock):
        garage = ParkingGarage()
        rtc.return_value = datetime(2025, 11, 22, 15, 30)
        entry_time = datetime(2025, 11, 22, 12, 30)
        fee = garage.calculate_parking_fee(entry_time)
        self.assertEqual(9.375, fee)

    @patch.object(ParkingGarage, "change_servo_angle")
    def test_open_garage_door(self, motor:Mock):
        garage = ParkingGarage()
        garage.open_garage_door()
        garage.door_open = True
        self.assertTrue(garage.door_open)
        motor.assert_called_with(12)
        
    @patch.object(ParkingGarage, "change_servo_angle")
    def test_close_garage_door(self, motor:Mock):
        garage = ParkingGarage()
        garage.close_garage_door()
        garage.door_open = False
        self.assertFalse(garage.door_open)
        motor.assert_called_with(2)

    @patch.object(GPIO, "output")
    def test_turn_on_red_light(self, light: Mock):
        garage = ParkingGarage()
        garage.turn_on_red_light()
        #garage.red_light_on = True
        self.assertTrue(garage.red_light_on)
        light.assert_called_with(garage.LED_PIN, True)

    @patch.object(GPIO, "output")
    def test_turn_off_red_light(self,light: Mock):
        garage = ParkingGarage()
        garage.turn_off_red_light()
        #garage.red_light_on = True
        self.assertFalse(garage.red_light_on)
        light.assert_called_with(garage.LED_PIN, False)

    @patch.object(GPIO,"input")
    @patch.object(GPIO, "output")
    def test_manage_light_parking_full(self, light:Mock, mock_input:Mock):
        garage = ParkingGarage()
        mock_input.side_effect = [True, True, False]
        garage.manage_red_light()
        light.assert_called_once_with(garage.LED_PIN, True) # observation that light is on when parking is full
        self.assertTrue(garage.red_light_on)