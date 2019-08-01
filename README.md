# pisugar-power-manager

Management program for PiSugar 2

Install
```
apt-get update
apt-get install python3-pyqt5 pyqt5-dev-tools
pip3 install smbus

```

Start the core without UI:
```
$ python3 core/PiSugarCore.py

# core program will create a unix domain socket file: /tmp/pisugar.sock
# use following commands to get / set data from the battery

# get model  (pisugar model)
# get battery  (battery level percent)
# get battery_v  (lithium battery votage)
# get battery_i  (lithium battery current)
# get battery_charging  (charging status)
# get rtc_time  (rtc time string)
# get rtc_time_list  (rtc time in python list)
# get rtc_clock_flag  (rtc alarm flag)
# rtc_clean_flag  (clean alarm flag)
# rtc_pi2rtc  (sync time from Pi to rtc)
# rtc_clock_set  (set auto wake up alarm)

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
