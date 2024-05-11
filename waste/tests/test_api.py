import datetime
from decimal import Decimal

from django.db import connection
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ErrorDetail


class APITest(TestCase):
    """
    Test case for the API endpoints.
    """

    def setUp(self):
        """
        Set up test data for the API tests.
        """
        self.maxDiff = None
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bin (
                    bin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    lat DECIMAL(9,6) NOT NULL,
                    lon DECIMAL(9,6) NOT NULL,
                    waste_type VARCHAR(50) NOT NULL,
                    capacity DECIMAL(10,2) NOT NULL,
                    collect_freq VARCHAR(50) NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste (
                    waste_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bin_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    level NUMERIC(6,2) NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_api (
                    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    location TEXT NOT NULL,
                    lat NUMERIC(9,6) NOT NULL,
                    lon NUMERIC(9,6) NOT NULL,
                    temp NUMERIC(5,2) NOT NULL,
                    precip NUMERIC(5,2) NOT NULL,
                    humid NUMERIC(5,2) NOT NULL
                )
            """)

            cursor.execute("""
                INSERT INTO bin (name, location, lat, lon, waste_type, capacity, collect_freq)
                VALUES 
                    ('Bin 1', 'Thanyaburi', 13.9864, 100.6183, 'General', 100.00, 'Daily'),
                    ('Bin 2', 'Lam Luk Ka', 13.9729, 100.6375, 'Recyclable', 120.00, 'Weekly')
            """)

            cursor.execute("""
                INSERT INTO waste (bin_id, timestamp, level)
                VALUES 
                    (1, '2024-04-23 10:00:00', 70.50),
                    (2, '2024-04-23 10:00:00', 40.25),
                    (1, '2024-04-23 09:00:00', 60.00),
                    (2, '2024-04-23 09:00:00', 30.75),
                    (1, '2024-04-23 08:00:00', 50.25),
                    (2, '2024-04-23 08:00:00', 20.50),
                    (1, '2024-04-23 07:00:00', 40.75),
                    (2, '2024-04-23 07:00:00', 10.25),
                    (1, '2024-04-23 06:00:00', 30.25),
                    (2, '2024-04-23 06:00:00', 5.50)
            """)

            cursor.execute("""
                INSERT INTO weather_api (timestamp, location, lat, lon, temp, precip, humid)
                VALUES 
                    ('2024-04-23 10:00:00', 'Thanyaburi', 13.9864, 100.6183, 30.0, 0.0, 60.0),
                    ('2024-04-23 09:00:00', 'Thanyaburi', 13.9864, 100.6183, 29.5, 0.0, 65.0),
                    ('2024-04-23 08:00:00', 'Thanyaburi', 13.9864, 100.6183, 29.0, 0.0, 70.0),
                    ('2024-04-23 07:00:00', 'Thanyaburi', 13.9864, 100.6183, 28.5, 0.0, 75.0),
                    ('2024-04-23 06:00:00', 'Thanyaburi', 13.9864, 100.6183, 28.0, 0.0, 80.0),
                    ('2024-04-23 10:00:00', 'Lam Luk Ka', 13.9729, 100.6375, 32.0, 0.0, 55.0),
                    ('2024-04-23 09:00:00', 'Lam Luk Ka', 13.9729, 100.6375, 31.5, 0.0, 60.0),
                    ('2024-04-23 08:00:00', 'Lam Luk Ka', 13.9729, 100.6375, 31.0, 0.0, 65.0),
                    ('2024-04-23 07:00:00', 'Lam Luk Ka', 13.9729, 100.6375, 30.5, 0.0, 70.0),
                    ('2024-04-23 06:00:00', 'Lam Luk Ka', 13.9729, 100.6375, 30.0, 0.0, 75.0)
            """)

    def test_list_bins_api(self):
        """
        Test the endpoint for retrieving a list of bins.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = [
            {"bin_id": 1, "name": "Bin 1", "location": "Thanyaburi",
             "lat": "13.986400", "lon": "100.618300", "waste_type": "General",
             "capacity": "100.00", "collect_freq": "Daily"},
            {"bin_id": 2, "name": "Bin 2", "location": "Lam Luk Ka",
             "lat": "13.972900", "lon": "100.637500",
             "waste_type": "Recyclable", "capacity": "120.00",
             "collect_freq": "Weekly"}
        ]
        response = self.client.get('/api/bins/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_bin_api(self):
        """
        Test the endpoint for retrieving a specific bin.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {"bin_id": 1, "name": "Bin 1",
                             "location": "Thanyaburi", "lat": "13.986400",
                             "lon": "100.618300", "waste_type": "General",
                             "capacity": "100.00", "collect_freq": "Daily"}
        response = self.client.get('/api/bins/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_bin_api(self):
        """
        Test the endpoint for retrieving a specific bin that does not exist.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {
            "detail": ErrorDetail(string='No Bin matches the given query.',
                                  code='not_found')}
        response = self.client.get('/api/bins/3/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_list_latest_wastes_api(self):
        """
        Test the endpoint for retrieving the latest waste data for all bins.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = [
            {
                "bin": 1,
                "total_waste": Decimal("251.75"),
                "min_temp": Decimal("28"),
                "max_temp": Decimal("30"),
                "avg_temp": Decimal("29"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("60"),
                "max_humid": Decimal("80"),
                "avg_humid": Decimal("70"),
            },
            {
                "bin": 2,
                "total_waste": Decimal("107.25"),
                "min_temp": Decimal("30"),
                "max_temp": Decimal("32"),
                "avg_temp": Decimal("31"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("55"),
                "max_humid": Decimal("75"),
                "avg_humid": Decimal("65"),
            },
        ]
        response = self.client.get('/api/waste/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_latest_waste_bin_api(self):
        """
        Test the endpoint for retrieving the latest waste data for a specific bin.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "bin": 1,
            "date": datetime.date(2024, 4, 23),
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/latest/bin/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_latest_waste_bin_api(self):
        """
        Test the endpoint for retrieving the latest waste data for a specific bin that does not exist.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Bin ID"}
        response = self.client.get('/api/waste/latest/bin/3/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_latest_waste_location_api(self):
        """
        Test the endpoint for retrieving the latest waste data for a specific location.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "location": "Thanyaburi",
            "date": datetime.date(2024, 4, 23),
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/latest/location/Thanyaburi/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_latest_waste_location_api(self):
        """
        Test the endpoint for retrieving the latest waste data for a specific location that does not exist.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Location"}
        response = self.client.get('/api/waste/latest/location/Undefined/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_list_period_wastes_api(self):
        """
        Test the endpoint for retrieving waste data for a specific date.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = [
            {
                "bin": 1,
                "total_waste": Decimal("251.75"),
                "min_temp": Decimal("28"),
                "max_temp": Decimal("30"),
                "avg_temp": Decimal("29"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("60"),
                "max_humid": Decimal("80"),
                "avg_humid": Decimal("70"),
            },
            {
                "bin": 2,
                "total_waste": Decimal("107.25"),
                "min_temp": Decimal("30"),
                "max_temp": Decimal("32"),
                "avg_temp": Decimal("31"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("55"),
                "max_humid": Decimal("75"),
                "avg_humid": Decimal("65"),
            },
        ]
        response = self.client.get('/api/waste/2024/4/23/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_period_waste_bin_api(self):
        """
        Test the endpoint for retrieving waste data for a specific bin on a specific date.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "bin": 1,
            "year": 2024,
            "month": 4,
            "day": 23,
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/2024/4/23/bin/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_period_waste_bin_api(self):
        """
        Test the endpoint for retrieving waste data for a specific bin on a specific date when the bin ID is invalid.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Bin ID"}
        response = self.client.get('/api/waste/2024/4/23/bin/3/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_period_waste_location_api(self):
        """
        Test the endpoint for retrieving waste data for a specific location on a specific date.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "location": "Thanyaburi",
            "year": 2024,
            "month": 4,
            "day": 23,
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/2024/4/23/location/Thanyaburi/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_period_waste_location_api(self):
        """
        Test the endpoint for retrieving waste data for a specific location on a specific date when the location is invalid.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Location"}
        response = self.client.get('/api/waste/2024/4/23/location/Undefined/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_list_period_wastes_api_year_month(self):
        """
        Test the endpoint for retrieving waste data for a specific year and month.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = [
            {
                "bin": 1,
                "total_waste": Decimal("251.75"),
                "min_temp": Decimal("28"),
                "max_temp": Decimal("30"),
                "avg_temp": Decimal("29"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("60"),
                "max_humid": Decimal("80"),
                "avg_humid": Decimal("70"),
            },
            {
                "bin": 2,
                "total_waste": Decimal("107.25"),
                "min_temp": Decimal("30"),
                "max_temp": Decimal("32"),
                "avg_temp": Decimal("31"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("55"),
                "max_humid": Decimal("75"),
                "avg_humid": Decimal("65"),
            },
        ]
        response = self.client.get('/api/waste/2024/4/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_period_waste_bin_api_year_month(self):
        """
        Test the endpoint for retrieving waste data for a specific bin in a specific year and month.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "bin": 1,
            "year": 2024,
            "month": 4,
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/2024/4/bin/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_period_waste_bin_api_year_month(self):
        """
        Test the endpoint for retrieving waste data for a specific bin in a specific year and month when the bin ID is invalid.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Bin ID"}
        response = self.client.get('/api/waste/2024/4/bin/3/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_period_waste_location_api_year_month(self):
        """
        Test the endpoint for retrieving waste data for a specific location in a specific year and month.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "location": "Thanyaburi",
            "year": 2024,
            "month": 4,
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/2024/4/location/Thanyaburi/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_period_waste_location_api_year_month(self):
        """
        Test the endpoint for retrieving waste data for a specific location in a specific year and month when the location is invalid.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Location"}
        response = self.client.get('/api/waste/2024/4/location/Undefined/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_list_period_wastes_api_year(self):
        """
        Test the endpoint for retrieving waste data for a specific year.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = [
            {
                "bin": 1,
                "total_waste": Decimal("251.75"),
                "min_temp": Decimal("28"),
                "max_temp": Decimal("30"),
                "avg_temp": Decimal("29"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("60"),
                "max_humid": Decimal("80"),
                "avg_humid": Decimal("70"),
            },
            {
                "bin": 2,
                "total_waste": Decimal("107.25"),
                "min_temp": Decimal("30"),
                "max_temp": Decimal("32"),
                "avg_temp": Decimal("31"),
                "min_precip": Decimal("0"),
                "max_precip": Decimal("0"),
                "sum_precip": Decimal("0"),
                "min_humid": Decimal("55"),
                "max_humid": Decimal("75"),
                "avg_humid": Decimal("65"),
            },
        ]
        response = self.client.get('/api/waste/2024/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_period_waste_bin_api_year(self):
        """
        Test the endpoint for retrieving waste data for a specific bin in a specific year.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "bin": 1,
            "year": 2024,
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/2024/bin/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_period_waste_bin_api_year(self):
        """
        Test the endpoint for retrieving waste data for a specific bin in a specific year when the bin ID is invalid.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Bin ID"}
        response = self.client.get('/api/waste/2024/bin/3/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    def test_valid_specific_period_waste_location_api_year(self):
        """
        Test the endpoint for retrieving waste data for a specific location in a specific year.

        Ensures that the response status code is 200 (OK) and the response data matches the expected response.
        """
        expected_response = {
            "location": "Thanyaburi",
            "year": 2024,
            "records": [
                {
                    "datetime": datetime.datetime(2024, 4, 23, 10, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("70.50"),
                    "temp": Decimal("30.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("60.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 9, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("60.00"),
                    "temp": Decimal("29.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("65.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 8, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("50.25"),
                    "temp": Decimal("29.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("70.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 7, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("40.75"),
                    "temp": Decimal("28.50"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("75.00")
                },
                {
                    "datetime": datetime.datetime(2024, 4, 23, 6, 0,
                                                  tzinfo=datetime.timezone.utc),
                    "bin": 1,
                    "level": Decimal("30.25"),
                    "temp": Decimal("28.00"),
                    "precip": Decimal("0.00"),
                    "humid": Decimal("80.00")
                }
            ]
        }
        response = self.client.get('/api/waste/2024/location/Thanyaburi/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_invalid_specific_period_waste_location_api_year(self):
        """
        Test the endpoint for retrieving waste data for a specific location in a specific year when the location is invalid.

        Ensures that the response status code is 404 (Not Found) and the response data matches the expected response.
        """
        expected_response = {"Error": "Invalid Location"}
        response = self.client.get('/api/waste/2024/location/Undefined/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)
