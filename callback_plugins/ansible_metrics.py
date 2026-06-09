import os
import time
import socket
try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import Request, urlopen
    from urllib2 import URLError

from ansible.plugins.callback import CallbackBase


DOCUMENTATION = '''
  name: ansible_metrics
  type: aggregate
  short_description: pushes playbook summary metrics to Prometheus Pushgateway
  description:
      - This callback pushes metrics about playbook runs to a Prometheus Pushgateway.
  options:
    pushgateway_url:
      description: URL of the Prometheus Pushgateway
      env:
        - name: ANSIBLE_PUSHGATEWAY_URL
      default: http://gloin.taila24d4b.ts.net:9091
      type: string
'''


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'ansible_metrics'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.start_time = time.time()
        self.playbook_name = None
        self.pushgateway_url = os.environ.get(
            'ANSIBLE_PUSHGATEWAY_URL',
            'http://gloin.taila24d4b.ts.net:9091'
        ).rstrip('/')
        self.hostname = socket.gethostname()
        self._display.vvv('ansible_metrics callback initialized, pushgateway: %s', self.pushgateway_url)

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = playbook._file_name

    def v2_playbook_on_stats(self, stats):
        duration = time.time() - self.start_time

        hosts_ok = 0
        hosts_changed = 0
        hosts_failed = 0
        hosts_unreachable = 0

        for host in stats.processed:
            summary = stats.summarize(host)
            hosts_ok += summary['ok']
            hosts_changed += summary['changed']
            hosts_failed += summary['failures']
            hosts_unreachable += summary['unreachable']

        success = 0 if hosts_failed == 0 else 1

        labels = 'playbook="{}",controller="{}"'.format(
            (self.playbook_name or 'unknown').replace('"', '\\"'),
            self.hostname
        )

        lines = [
            '# HELP ansible_playbook_duration_seconds Duration of playbook run in seconds',
            '# TYPE ansible_playbook_duration_seconds gauge',
            'ansible_playbook_duration_seconds{{{}}} {}'.format(labels, duration),
            '',
            '# HELP ansible_playbook_status Playbook exit status (0=success, 1=1+ failures)',
            '# TYPE ansible_playbook_status gauge',
            'ansible_playbook_status{{{}}} {}'.format(labels, success),
            '',
            '# HELP ansible_hosts_ok Total hosts with ok=results',
            '# TYPE ansible_hosts_ok gauge',
            'ansible_hosts_ok{{{}}} {}'.format(labels, hosts_ok),
            '',
            '# HELP ansible_hosts_changed Total hosts with changed results',
            '# TYPE ansible_hosts_changed gauge',
            'ansible_hosts_changed{{{}}} {}'.format(labels, hosts_changed),
            '',
            '# HELP ansible_hosts_failed Total hosts with failed results',
            '# TYPE ansible_hosts_failed gauge',
            'ansible_hosts_failed{{{}}} {}'.format(labels, hosts_failed),
            '',
            '# HELP ansible_hosts_unreachable Total hosts with unreachable results',
            '# TYPE ansible_hosts_unreachable gauge',
            'ansible_hosts_unreachable{{{}}} {}'.format(labels, hosts_unreachable),
        ]

        body = '\n'.join(lines) + '\n'

        instance = (self.playbook_name or 'unknown').replace('/', '_')
        url = '{}/metrics/job/ansible/instance/{}'.format(
            self.pushgateway_url, instance
        )

        try:
            req = Request(url, data=body.encode('utf-8'))
            req.add_header('Content-Type', 'text/plain; version=0.0.4')
            req.add_header('X-Requested-By', 'ansible')
            resp = urlopen(req, timeout=10)
            resp.read()
            self._display.vvv('Pushed ansible metrics to pushgateway: %s', url)
        except URLError as e:
            self._display.warning('Failed to push ansible metrics: %s', e)
