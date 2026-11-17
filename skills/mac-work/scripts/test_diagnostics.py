"""Telemetry decoding and bounded external-command behavior."""

import sys
import time
import unittest

from diagnostics import decode_vm, decode_swap, sample_age, read_probe, decode_events


class Telemetry(unittest.TestCase):
    def test_native_event_envelope_retains_only_correlation_fields(self):
        import json
        text = json.dumps({'event':'lease.granted','timestamp':1234000,
                           'payload':{'leaseId':'lease-a','deviceId':'device-a','environment':{'TOKEN':'SECRET'}}})
        value = decode_events(text)
        self.assertEqual(value,[{'lease_id':'lease-a','device_id':'device-a','event':'lease.granted','event_at':1234}])
        self.assertNotIn('SECRET',str(value))
    def test_swap_and_stale_missing_or_future_samples_are_explicit(self):
        value = decode_swap('vm.swapusage: total = 2048.00M used = 1084.44M free = 963.56M (encrypted)')
        self.assertEqual(value['used_bytes'],round(1084.44*1024**2))
        self.assertEqual(sample_age(10,80)['freshness'],'stale')
        self.assertEqual(sample_age(79,80)['freshness'],'fresh')
        self.assertEqual(sample_age(90,80)['freshness'],'clock-skew')
        with self.assertRaises(ValueError):decode_swap('unsupported format')

    def test_probe_bounds_time_and_output_and_does_not_echo_private_stderr(self):
        result = read_probe([sys.executable,'-c','import time;time.sleep(2)'],seconds=.05)
        self.assertEqual(result['status'],'unavailable')
        self.assertEqual(result['reason'],'timeout')
        result = read_probe([sys.executable,'-c','print("x"*10000)'],max_bytes=100)
        self.assertEqual(result['reason'],'output-limit')
        result = read_probe([sys.executable,'-c','import sys;sys.stderr.write("SECRET");sys.exit(3)'])
        self.assertEqual(result['reason'],'exit-3')
        self.assertNotIn('SECRET',str(result))
    def test_vm_pages_have_host_page_units_and_distinguish_compressor_sizes(self):
        value = decode_vm('Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 2.\nPages occupied by compressor: 3.\nPages stored in compressor: 5.\n')
        self.assertEqual(value['free_bytes'],32768)
        self.assertEqual(value['compressor_physical_bytes'],49152)
        self.assertEqual(value['compressor_logical_bytes'],81920)
        with self.assertRaises(ValueError):decode_vm('unknown native format')


if __name__ == '__main__':unittest.main()
