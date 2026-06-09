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


def escape_label(v):
    return str(v).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')


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
        self.current_task = None
        self.current_role = None
        self.task_timers = {}
        self.task_stats = {}
        self.role_timers = {}
        self.role_stats = {}
        self._display.vvv('ansible_metrics callback initialized, pushgateway: %s' % self.pushgateway_url)

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = playbook._file_name

    def v2_playbook_on_task_start(self, task, is_conditional):
        now = time.time()
        if self.current_task and self.current_task in self.task_timers:
            duration = now - self.task_timers[self.current_task]
            self.task_stats[self.current_task]['duration'] = duration
            role = self.task_stats[self.current_task].get('role')
            if role and role in self.role_stats:
                self.role_stats[role]['duration'] += duration
                self.role_stats[role]['task_count'] += 1

        task_name = task.get_name().strip()
        self.current_task = task_name
        self.task_timers[task_name] = now

        role_name = task._role.get_name() if task._role else None
        self.current_role = role_name

        if task_name not in self.task_stats:
            self.task_stats[task_name] = {
                'ok': 0, 'failed': 0, 'skipped': 0, 'unreachable': 0,
                'duration': 0.0, 'role': role_name
            }

        if role_name:
            if role_name not in self.role_stats:
                self.role_stats[role_name] = {'duration': 0.0, 'task_count': 0}

    def v2_runner_on_ok(self, result):
        if self.current_task and self.current_task in self.task_stats:
            self.task_stats[self.current_task]['ok'] += 1

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if self.current_task and self.current_task in self.task_stats:
            self.task_stats[self.current_task]['failed'] += 1

    def v2_runner_on_skipped(self, result):
        if self.current_task and self.current_task in self.task_stats:
            self.task_stats[self.current_task]['skipped'] += 1

    def v2_runner_on_unreachable(self, result):
        if self.current_task and self.current_task in self.task_stats:
            self.task_stats[self.current_task]['unreachable'] += 1

    def v2_playbook_on_stats(self, stats):
        now = time.time()

        if self.current_task and self.current_task in self.task_timers:
            duration = now - self.task_timers[self.current_task]
            self.task_stats[self.current_task]['duration'] = duration
            role = self.task_stats[self.current_task].get('role')
            if role and role in self.role_stats:
                self.role_stats[role]['duration'] += duration
                self.role_stats[role]['task_count'] += 1

        duration = now - self.start_time

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

        playbook_label = escape_label(self.playbook_name or 'unknown')
        base_labels = 'playbook="{playbook}",controller="{controller}"'.format(
            playbook=playbook_label, controller=escape_label(self.hostname)
        )

        data = {}
        declared = set()

        def add(name, help_text, line):
            if name not in declared:
                data.setdefault(name, []).append(
                    '# HELP {name} {help}'.format(name=name, help=help_text))
                data[name].append('# TYPE {name} gauge'.format(name=name))
                declared.add(name)
            data[name].append(line)

        add('ansible_playbook_duration_seconds',
            'Duration of playbook run in seconds',
            'ansible_playbook_duration_seconds{{{base}}} {val}'.format(
                base=base_labels, val=duration))

        add('ansible_playbook_status',
            'Playbook exit status (0=success, 1=1+ failures)',
            'ansible_playbook_status{{{base}}} {val}'.format(
                base=base_labels, val=success))

        add('ansible_hosts_ok', 'Total hosts with ok results',
            'ansible_hosts_ok{{{base}}} {val}'.format(base=base_labels, val=hosts_ok))
        add('ansible_hosts_changed', 'Total hosts with changed results',
            'ansible_hosts_changed{{{base}}} {val}'.format(base=base_labels, val=hosts_changed))
        add('ansible_hosts_failed', 'Total hosts with failed results',
            'ansible_hosts_failed{{{base}}} {val}'.format(base=base_labels, val=hosts_failed))
        add('ansible_hosts_unreachable', 'Total hosts with unreachable results',
            'ansible_hosts_unreachable{{{base}}} {val}'.format(base=base_labels, val=hosts_unreachable))

        for task_name, ts in sorted(self.task_stats.items()):
            if ts['duration'] == 0 and ts['ok'] == 0 and ts['failed'] == 0 and ts['skipped'] == 0:
                continue
            task_labels = '{base},task="{name}"'.format(
                base=base_labels, name=escape_label(task_name))
            if ts.get('role'):
                task_labels += ',role="{role}"'.format(role=escape_label(ts['role']))

            add('ansible_task_duration_seconds',
                'Task execution duration in seconds',
                'ansible_task_duration_seconds{{{labels}}} {val}'.format(
                    labels=task_labels, val=ts['duration']))

            for status in ('ok', 'failed', 'skipped', 'unreachable'):
                val = ts[status]
                if val:
                    add('ansible_task_results_total',
                        'Task result count per status',
                        'ansible_task_results_total{{{labels},status="{status}"}} {val}'.format(
                            labels=task_labels, status=status, val=val))

        for role_name, rs in sorted(self.role_stats.items()):
            if rs['task_count'] == 0:
                continue
            role_labels = '{base},role="{name}"'.format(
                base=base_labels, name=escape_label(role_name))

            add('ansible_role_duration_seconds',
                'Role execution duration in seconds',
                'ansible_role_duration_seconds{{{labels}}} {val}'.format(
                    labels=role_labels, val=rs['duration']))

            add('ansible_role_task_count',
                'Total tasks executed in role',
                'ansible_role_task_count{{{labels}}} {val}'.format(
                    labels=role_labels, val=rs['task_count']))

        body = '\n\n'.join(
            '\n'.join(data[name])
            for name in sorted(data)
        ) + '\n'

        instance = playbook_label.replace('/', '_')
        url = '{pgw}/metrics/job/ansible/instance/{inst}'.format(
            pgw=self.pushgateway_url, inst=instance)

        try:
            req = Request(url, data=body.encode('utf-8'))
            req.add_header('Content-Type', 'text/plain; version=0.0.4')
            req.add_header('X-Requested-By', 'ansible')
            resp = urlopen(req, timeout=10)
            resp.read()
            self._display.vvv('Pushed ansible metrics to pushgateway: {url}'.format(url=url))
        except URLError as e:
            self._display.warning(
                'Failed to push ansible metrics to {url}: {err}'.format(url=url, err=e))
