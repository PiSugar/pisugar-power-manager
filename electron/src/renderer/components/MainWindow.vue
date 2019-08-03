<template>
  <div id="wrapper">
    <div class="battery-info">
      <div class="charge-tag">
        <img class="flash" src="~@/assets/flash.svg" alt="">
        <p>Charging</p>
      </div>
      <div class="battery-shape">
        <div class="battery-content"></div>
      </div>
      <div class="battery-level">86%</div>
      <div class="battery-model">PiSugar 2 Pro</div>
      <img class="logo" src="~@/assets/logo.svg" alt="">
    </div>
    <div class="setting-panel">
      <div class="title">Schedule Wake Up</div>
      <el-row>
        <el-select v-model="alarmOptionValue" placeholder="请选择">
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
                :disabled="alarmOptionValue === 0"
                :picker-options="{
                  selectableRange: '00:00:00 - 23:59:59'
                }"
                placeholder="任意时间点">
        </el-time-picker>
        <el-button v-if="alarmOptionValue === 1">Repeat</el-button>
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
    </div>
  </div>
</template>

<script>
  export default {
    name: 'index-page',
    components: { },
    data () {
      return {
        alarmOption: [
          { label: 'Disabled', value: 0 },
          { label: 'TimeSet', value: 1 },
          { label: 'CircleSet', value: 2 }
        ],
        alarmOptionValue: 0,
        timeEditValue: new Date(2019, 8, 1, 18, 40),
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
    methods: {
    }
  }
</script>

<style>
  @import url('https://fonts.googleapis.com/css?family=Source+Sans+Pro');

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
    margin-top: 10px;
  }
  .setting-panel .el-form-item__label{
    text-align: left;
  }
  .setting-panel .el-form-item{
    margin-bottom: 10px;
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
    .flash{
      position: absolute;
      left: 20px;
      top: 6px;
      width: 12px;
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
      width: 80%;
      height: 100%;
      background-color: #88e61b;
      border-radius: 4px;
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

</style>
