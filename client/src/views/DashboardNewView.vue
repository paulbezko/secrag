<template>
  <div>
    <SidebarComp :type="type"></SidebarComp>
    <NewChatComp :type="type" v-if="newChat"></NewChatComp>
  </div>
</template>

<script>
import SidebarComp from '../components/Dashboard/SidebarComp.vue';
import NewChatComp from '../components/Dashboard/NewChatComp.vue';

export default {
  name: 'DashboardNewView',
  mode: 'history',
  components: {SidebarComp, NewChatComp},
  data() {
    return {
      type: 'preview',

      newChat: true,
    };
  },
}


</script>