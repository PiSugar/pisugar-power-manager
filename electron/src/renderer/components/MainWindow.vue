<template>
  <div id="wrapper">
    <div class="battery-info">
      <div :class="{'show': batteryCharging}" class="charge-tag">
        <img class="flash" src="~@/assets/flash.svg" alt="">
        <p>Charging</p>
      </div>
      <div class="battery-shape">
        <div class="battery-content" :class="batteryColor" :style="'width:'+batteryPercent+'%'"></div>
      </div>
      <div class="battery-level">{{batteryPercent}}%</div>
      <div class="battery-model">{{model}}</div>
      <img class="logo" src="~@/assets/logo.svg" alt="">
    </div>
    <div class="setting-panel">
      <div class="title">Schedule Wake Up</div>
      <el-row>
        <el-select v-model="alarmOptionValue" placeholder="请选择" :disabled="!socketConnect">
          <el-option
                  v-for="item in alarmOption"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
          </el-option>
        </el-select>
        <el-time-picker
                class="time-picker"
                v-model="timeEditValue"
                :disabled="alarmOptionValue === 0 || !socketConnect"
                :picker-options="{
                  selectableRange: '00:00:00 - 23:59:59'
                }"
                @change="timeEditChange"
                placeholder="任意时间点">
        </el-time-picker>
        <el-button v-if="alarmOptionValue === 1" :disabled="!socketConnect">Repeat</el-button>
      </el-row>
      <el-row>
        <p class="desc">Schedule wake up off</p>
      </el-row>
      <div class="title">Custom Button Function</div>
      <el-row>
        <el-form ref="buttonFuncForm" :model="buttonFuncForm" label-width="80px">
          <el-form-item label="Single Tap">
            <el-select v-model="buttonFuncForm.single" placeholder="请选择活动区域">
              <el-option
                      v-for="item in buttonFuncForm.singleOpts"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
              </el-option>
            </el-select>
            <el-button v-if="buttonFuncForm.single === 1">Edit</el-button>
            <span class="tag-span"><el-tag :type="singleTrigger?'success':''">Triggered</el-tag></span>
          </el-form-item>
        </el-form>
      </el-row>
      <el-row>
        <el-form ref="buttonFuncForm" :model="buttonFuncForm" label-width="80px">
          <el-form-item label="Double Tap">
            <el-select v-model="buttonFuncForm.double" placeholder="请选择活动区域">
              <el-option
                      v-for="item in buttonFuncForm.doubleOpts"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
              </el-option>
            </el-select>
            <el-button v-if="buttonFuncForm.double === 2">Edit</el-button>
            <span class="tag-span"><el-tag :type="doubleTrigger?'success':''">Triggered</el-tag></span>
          </el-form-item>
        </el-form>
      </el-row>
      <el-row>
        <el-form ref="buttonFuncForm" :model="buttonFuncForm" label-width="80px">
          <el-form-item label="Long Tap">
            <el-select v-model="buttonFuncForm.long" placeholder="请选择活动区域">
              <el-option
                      v-for="item in buttonFuncForm.longOpts"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
              </el-option>
            </el-select>
            <el-button v-if="buttonFuncForm.long === 2">Edit</el-button>
            <span class="tag-span"><el-tag :type="longTrigger?'success':''">Triggered</el-tag></span>
          </el-form-item>
        </el-form>
      </el-row>
      <div class="title">Safe Shutdown</div>
      <el-row>
        <el-select v-model="safeShutdown" placeholder="请选择">
          <el-option
                  v-for="item in safeShutdownOpts"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
          </el-option>
        </el-select>
      </el-row>
      <div class="sys-info">RTC Time : {{rtcTime}}</div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'index-page',
    debug: true,
    components: { },
    data () {
      return {
        rtcTime: null,
        rtcUpdateTime: new Date().getTime(),
        batteryPercent: '...',
        batteryCharging: false,
        socketConnect: false,
        model: '...',
        alarmOption: [
          { label: 'Disabled', value: 0 },
          { label: 'TimeSet', value: 1 }
          // { label: 'CircleSet', value: 2 }
        ],
        alarmOptionValue: 0,
        timeEditValue: new Date(2019, 8, 1, 18, 40, 30),
        timeRepeat: parseInt(1111111, 2),
        singleTrigger: true,
        doubleTrigger: true,
        longTrigger: true,
        buttonFuncForm: {
          single: 0,
          singleOpts: [
            { label: 'None', value: 0 },
            { label: 'Custom Shell', value: 1 }
          ],
          double: 0,
          doubleOpts: [
            { label: 'None', value: 0 },
            { label: 'Shutdown', value: 1 },
            { label: 'Custom Shell', value: 2 }
          ],
          long: 0,
          longOpts: [
            { label: 'None', value: 0 },
            { label: 'Shutdown', value: 1 },
            { label: 'Custom Shell', value: 2 }
          ]
        },
        safeShutdown: 0,
        safeShutdownOpts: [
          { label: 'Disabled', value: 0 },
          { label: '< 1%', value: 1 },
          { label: '< 3%', value: 2 },
          { label: '< 5%', value: 3 }
        ]
      }
    },
    mounted () {
      const that = this
      this.createWebSocketClient()
      setTimeout(() => {
        that.timeUpdater()
      }, 1000)
    },
    computed: {
      batteryColor () {
        if (this.batteryPercent < 10) return 'red'
        if (this.batteryPercent < 30) return 'yellow'
        return 'green'
      }
    },
    methods: {
      createWebSocketClient () {
        const that = this
        console.log(this.$socket)
        this.$socket.onopen = function () {
          console.log(`[Websocket CLIENT] open()`)
          that.getBatteryInfo(true)
        }
      },
      bindSocket () {
        const that = this
        this.$socket.onmessage = async function (e) {
          let message = await that.blob2String(e.data)
          if (message.indexOf('model:') > -1) {
            that.model = message.replace('model: ', '')
          }
          if (message.indexOf('battery:') > -1) {
            that.batteryPercent = parseInt(message.replace('battery: ', ''))
          }
          if (message.indexOf('battery_charging: ') > -1) {
            that.batteryCharging = message.indexOf('True') > 0
          }
          if (message.indexOf('rtc_time: ') > -1) {
            console.log(message)
            message = message.replace('rtc_time: ', '')
            that.rtcTime = new Date(message)
            that.rtcUpdateTime = new Date().getTime()
          }
          if (message.indexOf('button_event: ') > -1) {
            console.log(message)
            if (message.indexOf('single') > -1) {
              that.singleTrigger = false
            }
            if (message.indexOf('double') > -1) {
              that.doubleTrigger = false
            }
            if (message.indexOf('long') > -1) {
              that.longTrigger = false
            }
            setTimeout(()=> {
              that.singleTrigger = true
              that.doubleTrigger = true
              that.longTrigger = true
            }, 10)
          }
        }
      },
      getBatteryInfo (loop) {
        const that = this
        if (this.$socket.readyState === 1) {
          if (!this.socketConnect) {
            console.log('bind socket')
            this.bindSocket()
            this.$socket.send('get model')
            this.$socket.send('get rtc_time')
          }
          this.socketConnect = true
          this.$socket.send('get battery')
          this.$socket.send('get battery_i')
          this.$socket.send('get battery_v')
          this.$socket.send('get battery_charging')
        } else {
          this.socketConnect = false
          this.batteryPercent = 0
          this.batteryCharging = false
          this.model = 'Not Available'
        }
        if (loop) {
          setTimeout(() => {
            that.getBatteryInfo(true)
          }, 1000)
        }
      },
      blob2String (blob) {
        return new Promise((resolve, reject) => {
          let reader = new FileReader()
          reader.onload = function(event){
            let content = reader.result
            resolve(content)
          }
          reader.readAsText(blob)
        })
      },
      timeUpdater () {
        const that = this
        if (this.rtcTime) {
          let timeStamp = this.rtcTime.getTime()
          let current = new Date().getTime()
          let offset = current - this.rtcUpdateTime
          this.rtcUpdateTime = current
          this.rtcTime = new Date(timeStamp + offset)
        }
        setTimeout(() => {
          that.timeUpdater()
        }, 1000)
      },
      timeEditChange (time) {
        let sec = time.getSeconds()
        let min = time.getMinutes()
        let hour = time.getHours()
        this.$socket.send(`rtc_clock_set ${sec},${min},${hour},0,0,0,0 0b${this.timeRepeat.toString(2)}`)
      }
    }
  }
</script>

<style>
  @import url('https://fonts.googleapis.com/css?family=Source+Sans+Pro');
  @keyframes show-once {
    0% {
      opacity: 0;
    }
    10% {
      opacity: 1;
    }
    100% {
      opacity: 0;
    }
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: 'Source Sans Pro', sans-serif;
    width: 900px;
    height: 560px;
    position: fixed;
    background-color: orange;
  }
  .setting-panel .el-date-editor.el-input, .el-date-editor.el-input__inner{
    width: 160px;
  }
  .el-row{
    margin-top: 6px;
  }
  .setting-panel .el-form-item__label{
    text-align: left;
  }
  .setting-panel .el-form-item{
    margin-bottom: 10px;
  }
  .tag-span .el-tag{
    display: none;
    opacity: 1;
  }
  .tag-span .el-tag.el-tag--success{
    display: inline-block;
    animation: show-once 2s ease-in-out forwards;
  }
</style>

<style lang="less">

  #wrapper {
    background: linear-gradient(#ffe025, orange);
    width: 100vw;
    height: 100vw;
  }

  .battery-info{
    position: absolute;
    top: 0;
    left: 0;
    width: 350px;
    height: 560px;
  }

  .charge-tag{
    position: absolute;
    left: 50%;
    top: 140px;
    width: 120px;
    height: 30px;
    margin-left: -75px;
    color: orange;
    padding: 3px 40px;
    background-color: #fff;
    border-radius: 15px;
    box-shadow: 0 0 10px 2px rgba(157, 104, 0, 0.1);
    font-weight: bold;
    opacity: 0;
    transition: all 0.5s ease-in-out;
    transform: translateY(80px);
    .flash{
      position: absolute;
      left: 20px;
      top: 6px;
      width: 12px;
    }
    &.show{
      transform: translateY(0);
      opacity: 1;
    }
  }
  
  .battery-shape{
    position: absolute;
    top: 200px;
    left: 80px;
    width: 160px;
    height: 80px;
    padding: 6px;
    background-color: #fff;
    border-radius: 6px;
    box-shadow: 0 0 10px 2px rgba(157, 104, 0, 0.1);
    &:before{
      display: block;
      position: absolute;
      content: " ";
      width: 30px;
      height: 30px;
      background-color: #fff;
      right: -15px;
      top: 25px;
      border-radius: 6px;
    }
    .battery-content{
      position: relative;
      width: 0%;
      height: 100%;
      border-radius: 4px;
      transition: all 1s ease-in-out;
      &.green{
        background-color: #88e61b;
      }
      &.red{
        background-color: #ff521c;
      }
      &.yellow{
        background-color: #ffd100;
      }
    }
  }
  
  .battery-level{
    position: absolute;
    top: 290px;
    left: 80px;
    width: 160px;
    height: 80px;
    text-align: center;
    color: #fff;
    font-size: 42px;
    font-weight: bold;
  }

  .battery-model{
    position: absolute;
    top: 340px;
    left: 80px;
    width: 160px;
    height: 80px;
    text-align: center;
    color: #fff;
    font-size: 16px;
  }

  .logo{
    position: absolute;
    width: 140px;
    bottom: 50px;
    left: 50%;
    margin-left: -85px;
  }

  .setting-panel{
    position: absolute;
    top: 20px;
    right: 20px;
    width: 550px;
    height: 520px;
    padding: 0 30px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 0 10px 2px rgba(157, 104, 0, 0.1);
    .title{
      font-size: 18px;
      font-weight: bold;
      color: #1f3f6b;
      margin: 20px 0;
    }
    .desc{
      color: #a2a6b8;
    }
  }
  .sys-info{
    margin-top: 20px;
    font-size: 12px;
    color: #999;
  }

</style>
