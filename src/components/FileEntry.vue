<template>
  <div class="ui list">
    <div v-for="item in items" :key="item.name" class="item">
      <span class="clickable" title="Download" @click="item.download(item.name)">
        <span :class="item.icon" />&nbsp;
        <span class="pi pi-download" />&nbsp;
      </span>

      <span class="clickable" :title="item.action_title" @click="item.action(item.name)">
        <span :style="style" v-text="item.name" />
      </span>

    </div>
  </div>
</template>

<script setup>
defineProps({
  items: Array,
  style: String(),
});
</script>

<style scoped>
.icon {
  margin-right: .5ex;
}

.clickable {
  cursor: pointer;
  border-radius: 3px;
  padding: .7ex .5ex;

  &:hover {
    text-decoration: underline;
    animation-duration: 300ms;
  }
}
</style>
