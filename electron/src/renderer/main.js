import Vue from 'vue'
import axios from 'axios'

import App from './App'
import router from './router'
// import store from './store'
import VueNativeSock from 'vue-native-websocket'

import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

const productionHost = window.navigator.userAgent.toLowerCase().indexOf('electron') >= 0 ? 'ws://localhost:3001' : `ws://${window.location.hostname}:3001`
const webSocketHost = process.env.NODE_ENV === 'development' ? 'ws://192.168.2.130:3001' : productionHost

if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
Vue.http = Vue.prototype.$http = axios
Vue.config.productionTip = false
Vue.use(ElementUI)
Vue.use(VueNativeSock, webSocketHost, {
  reconnection: true,
  reconnectionDelay: 3000
})

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  // store,
  template: '<App/>'
}).$mount('#app')
