"""Admission capacity decisions from bounded kernel samples."""

import subprocess
import unittest
from unittest.mock import patch

import runner


class AdaptiveCapacity(unittest.TestCase):
    def test_fixed_config_does_not_probe(self):
        with patch('runner.subprocess.check_output') as probe:
            self.assertEqual(runner._admission_capacities({}).get('heavy'), 1)
        probe.assert_not_called()

    def test_only_normal_pressure_and_available_memory_allow_two(self):
        cases = ((b'1\n40\n', 2), (b'1\n100\n', 2), (b'1\n39\n', 1),
                 (b'1\n101\n', 1), (b'2\n80\n', 1), (b'4\n80\n', 1),
                 (b'1\n', 1), (b'1\nunknown\n', 1), (b'1\n80\n0\n', 1))
        for output, capacity in cases:
            with self.subTest(output=output):
                with patch('runner.subprocess.check_output', return_value=output) as probe:
                    self.assertEqual(runner._admission_capacities({'adaptive_capacity': True}).get('heavy'), capacity)
                self.assertEqual(probe.call_args.args[0], [
                    '/usr/sbin/sysctl', '-n', 'kern.memorystatus_vm_pressure_level', 'kern.memorystatus_level'])

    def test_failed_probe_allows_one_slot(self):
        for error in (OSError(), subprocess.CalledProcessError(1, 'sysctl'),
                      subprocess.TimeoutExpired('sysctl', .1)):
            with self.subTest(error=error), patch('runner.subprocess.check_output', side_effect=error):
                self.assertEqual(runner._admission_capacities({'adaptive_capacity': True}).get('heavy'), 1)

    def test_fresh_sample_expires_before_admission(self):
        with patch('runner.subprocess.check_output', return_value=b'1\n80\n'):
            with patch('runner.time.monotonic', side_effect=(10, 10.25)):
                capacities = runner._admission_capacities({'adaptive_capacity': True})
                self.assertEqual(capacities.get('heavy'), 1)
