# pisugar-power-manager

<p align="center">
  <img width="320" src="https://raw.githubusercontent.com/JdaieLin/PiSugar/master/logo.jpg">
</p>

### Management program for PiSugar 2

Install
```
apt-get update
apt-get install python3-pyqt5 pyqt5-dev-tools
pip3 install smbus websockets

```

Start the core without UI:
```
$ python3 core/PiSugarCore.py

# core program will host an http server at port 8000
# please visit http://<ip of your pi>:8000

# core program will also create a unix domain socket file: /tmp/pisugar.sock
# use following commands to get / set data from the battery

# get model  (pisugar model)
# get battery  (battery level percent)
# get battery_v  (lithium battery votage)
# get battery_i  (lithium battery current)
# get battery_charging  (charging status)
# get rtc_time  (rtc time string)
# get rtc_time_list  (rtc time in python list)
# get rtc_alarm_flag  (rtc alarm flag)
# get safe_shutdown_level
# get alarm type (1: daily alarm, 0: off)
# get alarm time (alarm timestamp)
# get alarm type (alarm week repeat)
# get button enable <type> (type: single/double/long)
# get button shell <type> (type: single/double/long)

# rtc_clean_flag  (clean alarm flag)
# rtc_pi2rtc  (sync time from Pi to rtc)
# rtc_alarm_set  (set auto wake up alarm)
# rtc_alarm_disable  (disable wake up alarm)
# rtc_test_wake (test wake in 1min30sec)
# set_button_enable (argv1: single/double/long  argv2: 1/0)
# set_button_shell (argv1: single/double/long  argv2: shell script to execute)
# set_safe_shutdown_level (e.g. -1 / 3 / 5)

# e.g. get battery level precentage
$ echo get battery | nc -U /tmp/pisugar.sock
63.15938281249997

# e.g. set auto wake up alarm on 15:39:00 repeat on Sun, Mon, Tue, Wed, Sat
$ echo rtc_alarm_set 0,39,15,0,0,0,0 0b1001111 | nc -U /tmp/pisugar.sock
Done.


```

Start with UI:
```
$ export DISPLAY=:0
$ python3 app.py

```

<p align="center">
  <img width="688px" src="https://raw.githubusercontent.com/PiSugar/pisugar-power-manager/master/diagram.jpg">
</p>
