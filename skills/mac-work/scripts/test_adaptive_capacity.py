"""Admission capacity decisions from bounded kernel samples."""

import subprocess
import time
import unittest
from unittest.mock import patch

import runner


class AdaptiveCapacity(unittest.TestCase):
    def test_fixed_config_does_not_probe(self):
        with patch('runner.subprocess.check_output') as probe:
            self.assertIsNone(runner._admission_sample_expiry({}))
        probe.assert_not_called()

    def test_only_normal_pressure_and_available_memory_allow_two(self):
        cases = ((b'1\n40\n', 10.1), (b'1\n100\n', 10.1), (b'1\n39\n', None),
                 (b'1\n101\n', None), (b'2\n80\n', None), (b'4\n80\n', None),
                 (b'1\n', None), (b'1\nunknown\n', None), (b'1\n80\n0\n', None))
        for output, expiry in cases:
            with self.subTest(output=output):
                with patch('runner.subprocess.check_output', return_value=output) as probe, \
                     patch('runner.time.clock_gettime', return_value=10):
                    self.assertEqual(runner._admission_sample_expiry({'adaptive_capacity': True}), expiry)
                self.assertEqual(probe.call_args.args[0], [
                    '/usr/sbin/sysctl', '-n', 'kern.memorystatus_vm_pressure_level', 'kern.memorystatus_level'])

    def test_failed_probe_allows_one_slot(self):
        for error in (OSError(), subprocess.CalledProcessError(1, 'sysctl'),
                      subprocess.TimeoutExpired('sysctl', .1)):
            with self.subTest(error=error), patch('runner.subprocess.check_output', side_effect=error):
                self.assertIsNone(runner._admission_sample_expiry({'adaptive_capacity': True}))

    def test_freshness_budget_starts_before_the_probe_with_a_sleep_inclusive_clock(self):
        readings = iter((10, 10.25))

        def slow_probe(*args, **kwargs):
            self.assertEqual(kwargs['timeout'], .1)
            self.assertEqual(next(readings), 10.25)
            return b'1\n80\n'

        with patch('runner.subprocess.check_output', side_effect=slow_probe), \
             patch('runner.time.clock_gettime', side_effect=lambda _: next(readings)) as clock:
            self.assertEqual(runner._admission_sample_expiry({'adaptive_capacity': True}), 10.1)
        clock.assert_called_once_with(time.CLOCK_MONOTONIC_RAW)
