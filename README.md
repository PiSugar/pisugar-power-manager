# pisugar-power-manager

Management program for PiSugar 2

Install
```
apt-get update
apt-get install python3-pyqt5 pyqt5-dev-tools
pip3 install gevent

```

Start the core without UI:
```
$ python3 core/PiSugarCore.py

# core program will create a unix domain socket file: /tmp/pisugar.sock
# use following commands to get / set data from the battery

# get model
# get battery
# get battery_v
# get battery_i
# get battery_charging
# get rtc_time
# get rtc_time_list
# get rtc_clock_flag
# rtc_clean_flag
# rtc_pi2rtc
# rtc_clock_set

# e.g. get battery level precentage

$ echo get battery | nc -U /tmp/pisugar.sock
63.15938281249997

# e.g. set auto wake up alarm on 15:39:00 repeat on Sun, Mon, Tue, Wed, Sat
$ echo rtc_clock_set 0,39,15,0,0,0,0 0b1001111 | nc -U /tmp/pisugar.sock
Done.

```

Start with UI:
```
$ export DISPLAY=:0
$ python3 app.py

```
