<template>
  <NavBar />
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <BaseView v-if="user" :msg="`Welcome, ${user.username}, to Vehicle Parking App`"/>
  </div>
</template>

<script>
// @ is an alias to /src
import BaseView from '@/components/BaseView.vue'
import NavBar from '@/components/NavBar.vue';
import userMixin from '@/mixins/userMixin';

export default {
  name: 'HomeView',
  mixins: [userMixin],
  components: {
    BaseView,
    NavBar
  }
}
</script>
