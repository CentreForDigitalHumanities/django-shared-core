<template>
  <div class="uil-fancy-list">
    <ListItem
      v-for="item in items"
      :item="item"
      :key="item.pk"
      :message="message"
      :context="context"
      @expanding="childIsExpandingHandler"
    >
      <!-- Pass all slots from FancyList to ListItem -->
      <template v-for="(_, name) in $scopedSlots" :slot="name" slot-scope="slotData"><slot :name="name" v-bind="slotData" /></template>
    </ListItem>
  </div>
</template>

<script>
import ListItem from "./ListItem.vue";

export default {
  name: "ListContainer",
  components: {
    ListItem
  },
  props: {
    items: {
      type: Array,
      required: true,
    },
    context: {
      type: Object,
      required: true,
    },
  },
  data () {
    return {
      message: undefined,
    }
  },
  methods: {
    childIsExpandingHandler(pk) {
      this.message = {
        event: "expanding_child",
        pk: pk
      }
    }
  }
}
</script>

<style>
.uil-fancy-list {
    margin-top: 10px;
    margin-bottom: 15px;
}
</style>