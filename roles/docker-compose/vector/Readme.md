# Vector

❯ bash -c "$(curl -L https://setup.vector.dev)"
% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
Dload  Upload   Total   Spent    Left  Speed
0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100  8439  100  8439    0     0  13928      0 --:--:-- --:--:-- --:--:-- 13928

* Vector repository setup script


* Installing apt-transport-https, curl and gnupg

[sudo] password for triantium:
Get:1 https://download.docker.com/linux/ubuntu noble InRelease [48,5 kB]
Hit:2 https://repository.spotify.com stable InRelease
Get:3 http://apt.insync.io/ubuntu xenial InRelease [5.548 B]
Hit:4 https://apt.releases.hashicorp.com noble InRelease
Get:5 https://pkgs.tailscale.com/stable/ubuntu noble InRelease
Hit:6 https://deb.tuxedocomputers.com/ubuntu noble InRelease
Hit:7 https://txos-extra.tuxedocomputers.com/ubuntu noble InRelease
Hit:8 https://txos.tuxedocomputers.com/ubuntu-plasma noble InRelease
Get:9 https://mirrors.tuxedocomputers.com/ubuntu/mirror/archive.ubuntu.com/ubuntu noble InRelease [256 kB]
Hit:10 https://txos.tuxedocomputers.com/ubuntu-plasma noble-updates InRelease
Hit:12 https://txos.tuxedocomputers.com/ubuntu noble InRelease
Hit:13 https://ppa.launchpadcontent.net/musicbrainz-developers/stable/ubuntu noble InRelease
Hit:14 https://mirrors.tuxedocomputers.com/ubuntu/mirror/archive.ubuntu.com/ubuntu noble-updates InRelease
Hit:15 https://mirrors.tuxedocomputers.com/ubuntu/mirror/security.ubuntu.com/ubuntu noble-security InRelease
Hit:16 https://ppa.launchpadcontent.net/openrazer/stable/ubuntu noble InRelease
Hit:17 https://ppa.launchpadcontent.net/polychromatic/stable/ubuntu noble InRelease
Hit:18 https://downloads.typora.io/linux ./ InRelease
Get:19 https://packages.microsoft.com/repos/code stable InRelease [3.590 B]
Hit:11 https://prod-cdn.packages.k8s.io/repositories/isv:/kubernetes:/core:/stable:/v1.33/deb  InRelease
Get:20 https://packages.microsoft.com/repos/code stable/main amd64 Packages [25,4 kB]
Fetched 345 kB in 2s (210 kB/s)
Reading package lists... Done
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
curl is already the newest version (8.5.0-2ubuntu10.9).
gnupg is already the newest version (2.4.4-2ubuntu17.4).
gnupg set to manually installed.
The following NEW packages will be installed:
apt-transport-https
0 upgraded, 1 newly installed, 0 to remove and 74 not upgraded.
Need to get 3.970 B of archives.
After this operation, 36,9 kB of additional disk space will be used.
Get:1 https://mirrors.tuxedocomputers.com/ubuntu/mirror/archive.ubuntu.com/ubuntu noble-updates/universe amd64 apt-transport-https all 2.8.3 [3.970 B]
Fetched 3.970 B in 0s (30,5 kB/s)
Selecting previously unselected package apt-transport-https.
(Reading database ... 468140 files and directories currently installed.)
Preparing to unpack .../apt-transport-https_2.8.3_all.deb ...
Unpacking apt-transport-https (2.8.3) ...
Setting up apt-transport-https (2.8.3) ...

* Installing APT package sources for Vector

deb [signed-by=/usr/share/keyrings/datadog-archive-keyring.gpg] https://apt.vector.dev/ stable vector-0
gpg: directory '/root/.gnupg' created
gpg: /root/.gnupg/trustdb.gpg: trustdb created
gpg: key E6266D4AC0962C7D: public key "Datadog, Inc. APT key (2023-04-20) (APT key) <package+aptkey@datadoghq.com>" imported
gpg: Total number processed: 1
gpg:               imported: 1
gpg: key E6266D4AC0962C7D: "Datadog, Inc. APT key (2023-04-20) (APT key) <package+aptkey@datadoghq.com>" not changed
gpg: Total number processed: 1
gpg:              unchanged: 1
gpg: key 32637D44F14F620E: public key "Datadog, Inc. Master key (2020-09-08) <package+masterkey@datadoghq.com>" imported
gpg: Total number processed: 1
gpg:               imported: 1
Ign:1 https://apt.vector.dev stable InRelease
Get:2 https://apt.vector.dev stable Release [33,7 kB]
Get:3 https://apt.vector.dev stable Release.gpg [926 B]
Get:4 https://apt.vector.dev stable/vector-0 amd64 Packages [10,2 kB]
Fetched 44,8 kB in 0s (138 kB/s)
Reading package lists... Done

* Vector repository has been setup


~ took 18s
❯ sudo apt install vector
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Recommended packages:
datadog-signing-keys
The following NEW packages will be installed:
vector
0 upgraded, 1 newly installed, 0 to remove and 74 not upgraded.
Need to get 36,6 MB of archives.
After this operation, 151 MB of additional disk space will be used.
Get:1 https://apt.vector.dev stable/vector-0 amd64 vector amd64 0.56.0-1 [36,6 MB]
Fetched 36,6 MB in 6s (5.898 kB/s)
Selecting previously unselected package vector.
(Reading database ... 468144 files and directories currently installed.)
Preparing to unpack .../vector_0.56.0-1_amd64.deb ...
Unpacking vector (0.56.0-1) ...
Setting up vector (0.56.0-1) ...
systemd-journal:x:999:triantium

~ took 10s
❯ sudo systemctl start vector
Job for vector.service failed because the control process exited with error code.
See "systemctl status vector.service" and "journalctl -xeu vector.service" for details.

~
❯ sudo systemctl status vector
× vector.service - Vector
Loaded: loaded (/usr/lib/systemd/system/vector.service; disabled; preset: enabled)
Active: failed (Result: exit-code) since Wed 2026-06-10 10:02:07 CEST; 8s ago
Docs: https://vector.dev
Process: 21432 ExecStartPre=/usr/bin/vector validate (code=exited, status=78)
CPU: 12ms

Jun 10 10:02:07 berserker systemd[1]: vector.service: Scheduled restart job, restart counter is at 5.
Jun 10 10:02:07 berserker systemd[1]: vector.service: Start request repeated too quickly.
Jun 10 10:02:07 berserker systemd[1]: vector.service: Failed with result 'exit-code'.
Jun 10 10:02:07 berserker systemd[1]: Failed to start vector.service - Vector.

~
❯ sudo systemctl status vectorjournalctl -xeu vector.servic

~
❯ journalctl -xeu vector.service
░░ The job identifier is 9664.
Jun 10 10:02:06 berserker vector[21414]: 2026-06-10T08:02:06.762163Z ERROR vector::config::loading: Config file not found in path. path="/etc/vector/vector.yaml" internal_log_rate_limit=false
Jun 10 10:02:06 berserker systemd[1]: vector.service: Control process exited, code=exited, status=78/CONFIG
░░ Subject: Unit process exited
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ An ExecStartPre= process belonging to unit vector.service has exited.
░░
░░ The process' exit code is 'exited' and its exit status is 78.
Jun 10 10:02:06 berserker systemd[1]: vector.service: Failed with result 'exit-code'.
░░ Subject: Unit failed
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ The unit vector.service has entered the 'failed' state with result 'exit-code'.
Jun 10 10:02:06 berserker systemd[1]: Failed to start vector.service - Vector.
░░ Subject: A start job for unit vector.service has failed
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ A start job for unit vector.service has finished with a failure.
░░
░░ The job identifier is 9664 and the job result is failed.
Jun 10 10:02:06 berserker systemd[1]: vector.service: Scheduled restart job, restart counter is at 4.
░░ Subject: Automatic restarting of a unit has been scheduled
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ Automatic restarting of the unit vector.service has been scheduled, as the result for
░░ the configured Restart= setting for the unit.
Jun 10 10:02:07 berserker systemd[1]: Starting vector.service - Vector...
░░ Subject: A start job for unit vector.service has begun execution
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ A start job for unit vector.service has begun execution.
░░
░░ The job identifier is 9797.
Jun 10 10:02:07 berserker vector[21432]: 2026-06-10T08:02:07.017749Z ERROR vector::config::loading: Config file not found in path. path="/etc/vector/vector.yaml" internal_log_rate_limit=false
Jun 10 10:02:07 berserker systemd[1]: vector.service: Control process exited, code=exited, status=78/CONFIG
░░ Subject: Unit process exited
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ An ExecStartPre= process belonging to unit vector.service has exited.
░░
░░ The process' exit code is 'exited' and its exit status is 78.
Jun 10 10:02:07 berserker systemd[1]: vector.service: Failed with result 'exit-code'.
░░ Subject: Unit failed
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ The unit vector.service has entered the 'failed' state with result 'exit-code'.
Jun 10 10:02:07 berserker systemd[1]: Failed to start vector.service - Vector.
░░ Subject: A start job for unit vector.service has failed
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ A start job for unit vector.service has finished with a failure.
░░
░░ The job identifier is 9797 and the job result is failed.
Jun 10 10:02:07 berserker systemd[1]: vector.service: Scheduled restart job, restart counter is at 5.
░░ Subject: Automatic restarting of a unit has been scheduled
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ Automatic restarting of the unit vector.service has been scheduled, as the result for
░░ the configured Restart= setting for the unit.
Jun 10 10:02:07 berserker systemd[1]: vector.service: Start request repeated too quickly.
Jun 10 10:02:07 berserker systemd[1]: vector.service: Failed with result 'exit-code'.
░░ Subject: Unit failed
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ The unit vector.service has entered the 'failed' state with result 'exit-code'.
Jun 10 10:02:07 berserker systemd[1]: Failed to start vector.service - Vector.
░░ Subject: A start job for unit vector.service has failed
░░ Defined-By: systemd
░░ Support: http://www.ubuntu.com/support
░░
░░ A start job for unit vector.service has finished with a failure.
░░
░░ The job identifier is 9930 and the job result is failed.
