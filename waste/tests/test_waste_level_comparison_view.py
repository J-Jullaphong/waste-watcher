from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.urls import reverse

from ..models import Waste


class WasteLevelComparisonViewTest(TestCase):
    def setUp(self):
        """
        Set up test data for the Waste Level Comparison view tests.
        """
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

    def test_comparison_view_uses_correct_template(self):
        """
        Verify if the Waste Level Comparison view uses the correct template.
        """
        response = self.client.get(reverse('waste:comparison'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'waste_level_comparison.html',
                                "Template used for the comparison view is incorrect.")

    def test_comparison_view_with_no_data(self):
        """
        Test the Waste Level Comparison view with no data available.
        """
        Waste.objects.all().delete()
        response = self.client.get(reverse('waste:comparison'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chart_data'],
                         [None, None, None, None, None, None])
        self.assertEqual(response.context['temperature_data'],
                         [None, None, None, None, None, None])
        self.assertEqual(response.context['precipitation_data'],
                         [None, None, None, None, None, None])

    def test_comparison_view_with_filter_bin_id_and_year(self):
        """
        Test the Waste Level Comparison view with data filtered by bin ID and year.
        """
        response = self.client.get(
            f"{reverse('waste:comparison')}?filter_type=bin_id&filter_value=1&year=2024")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chart_data'],
                         [None, None, None, 251.75, None, None, None, None,
                          None, None, None, None])
        self.assertEqual(response.context['temperature_data'],
                         [None, None, None, Decimal('29'), None, None, None,
                          None, None, None, None, None])
        self.assertEqual(response.context['precipitation_data'],
                         [None, None, None, Decimal('0'), None, None, None,
                          None, None, None, None, None])

    def test_comparison_view_with_filter_bin_id_and_month(self):
        """
        Test the Waste Level Comparison view with data filtered by bin ID and month.
        """
        response = self.client.get(
            f"{reverse('waste:comparison')}?filter_type=bin_id&filter_value=1&year=2024&month=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chart_data'],
                         [None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, 251.75, None,
                          None, None, None, None, None, None])
        self.assertEqual(response.context['temperature_data'],
                         [None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, Decimal('29'), None,
                          None, None, None, None, None, None])
        self.assertEqual(response.context['precipitation_data'],
                         [None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, Decimal('0'), None,
                          None, None, None, None, None, None])

    def test_comparison_view_with_filter_bin_id_and_day(self):
        """
        Test the Waste Level Comparison view with data filtered by bin ID and day.
        """
        response = self.client.get(
            f"{reverse('waste:comparison')}?filter_type=bin_id&filter_value=1&year=2024&month=4&day=23")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chart_data'],
                         [None, 71.0, 180.75, None, None, None])
        self.assertEqual(response.context['temperature_data'],
                         [None, Decimal('28.25'), Decimal('29.5'), None, None,
                          None])
        self.assertEqual(response.context['precipitation_data'],
                         [None, Decimal('0'), Decimal('0'), None, None, None])

    def test_comparison_view_with_filter_location_and_year(self):
        """
        Test the Waste Level Comparison view with data filtered by location and year.
        """
        response = self.client.get(
            f"{reverse('waste:comparison')}?filter_type=location&filter_value=Thanyaburi&year=2024")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chart_data'],
                         [None, None, None, 251.75, None, None, None, None,
                          None, None, None, None])
        self.assertEqual(response.context['temperature_data'],
                         [None, None, None, Decimal('29'), None, None, None,
                          None, None, None, None, None])
        self.assertEqual(response.context['precipitation_data'],
                         [None, None, None, Decimal('0'), None, None, None,
                          None, None, None, None, None])

    def test_comparison_view_with_filter_location_and_month(self):
        """
        Test the Waste Level Comparison view with data filtered by location and month.
        """
        response = self.client.get(
            f"{reverse('waste:comparison')}?filter_type=location&filter_value=Thanyaburi&year=2024&month=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chart_data'],
                         [None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, 251.75, None,
                          None, None, None, None, None, None])
        self.assertEqual(response.context['temperature_data'],
                         [None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, Decimal('29'), None,
                          None, None, None, None, None, None])
        self.assertEqual(response.context['precipitation_data'],
                         [None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, None, None,
                          None, None, None, None, Decimal('0'), None,
                          None, None, None, None, None, None])

    def test_comparison_view_with_filter_location_and_day(self):
        """
        Test the Waste Level Comparison view with data filtered by location and day.
        """
        response = self.client.get(
            f"{reverse('waste:comparison')}?filter_type=location&filter_value=Thanyaburi&year=2024&month=4&day=23")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chart_data'],
                         [None, 71.0, 180.75, None, None, None])
        self.assertEqual(response.context['temperature_data'],
                         [None, Decimal('28.25'), Decimal('29.5'), None, None,
                          None])
        self.assertEqual(response.context['precipitation_data'],
                         [None, Decimal('0'), Decimal('0'), None, None, None])
