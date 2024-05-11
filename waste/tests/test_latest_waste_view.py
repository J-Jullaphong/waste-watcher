from django.db import connection
from django.test import TestCase
from django.urls import reverse

from ..models import Waste


class LatestWasteViewTest(TestCase):
    """
    Test case for the Latest Waste view.
    """

    def setUp(self):
        """
        Set up test data for the Latest Waste view tests.
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

    def test_latest_waste_view_uses_correct_template(self):
        """
        Test if the Latest Waste view uses the correct template.
        """
        response = self.client.get(reverse('waste:latest'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'latest_waste.html',
                                "Template used for the latest waste view is incorrect.")

    def test_latest_waste_view_no_waste_data(self):
        """
        Test the Latest Waste view with no waste data available.
        """
        Waste.objects.all().delete()
        response = self.client.get(reverse('waste:latest'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No waste data available.")

    def test_latest_waste_view_waste_data_with_bin_filter(self):
        """
        Test the Latest Waste view with waste data filtered by bin ID.
        """
        response = self.client.get(
            f"{reverse('waste:latest')}?filter_type=bin_id&filter_value=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['waste'].level, 70.50)
        self.assertEqual(response.context['latest_weather'].temp, 30.0)
        self.assertEqual(response.context['waste'].bin_id, 1)

    def test_latest_waste_view_waste_data_with_location_filter(self):
        """
        Test the Latest Waste view with waste data filtered by location.
        """
        response = self.client.get(
            f"{reverse('waste:latest')}?filter_type=location&filter_value=Thanyaburi")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['waste'].level, 70.50)
        self.assertEqual(response.context['latest_weather'].temp, 30.0)
        self.assertEqual(response.context['waste'].bin.location, 'Thanyaburi')
