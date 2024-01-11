<!-- RecursiveList.vue -->
<template>
  <ul>
    <li v-for="item in items" :key="item.name">
      {{ item.name }}
      <recursive-list v-if="item.children" :items="item.children" />
    </li>
  </ul>
</template>

<script>

export default {
  props: {
    items: {
      type: Array,
      required: true,
    },
  },
  components: {
    RecursiveList: () => import('./RecursiveList.vue'), // Lazy load to handle recursion
  },
};
</script>

<style scoped>
/* Add your styles here if needed */
</style>
