import unittest
import time
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tracker.utils import clamp, TimestampClock, Toast


class TestTrackerUtils(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-5, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)

    def test_timestamp_clock_monotonic(self):
        clock = TimestampClock()
        t1 = clock.next_ms()
        time.sleep(0.01)
        t2 = clock.next_ms()
        self.assertTrue(t2 > t1)

    def test_toast_lifecycle(self):
        toast = Toast()
        self.assertFalse(toast.active())
        toast.show("Halo", duration=0.1)
        self.assertTrue(toast.active())
        time.sleep(0.12)
        self.assertFalse(toast.active())


if __name__ == '__main__':
    unittest.main()
