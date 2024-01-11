<template>
  <div>
    <h2>Vue Hierarchical Category List Example</h2>
    <HierarchicalCategoryList
        :items="hierarchicalCategoryList"
        @selected-items="updateSelectedItems"
    ></HierarchicalCategoryList>

    <h2>Selected Items</h2>
    <ul>
      <li v-for="item in selectedItems" :key="item">{{ item }}</li>
    </ul>

    <DataGrid :items="selectedItemsFromBackend"></DataGrid>
  </div>
</template>

<script>
import HierarchicalCategoryList from "@/components/HierarchicalCategoryList";
import DataGrid from "@/components/DataGrid.vue";

export default {
  components: {
    HierarchicalCategoryList,
    DataGrid,
  },
  data() {
    return {
      hierarchicalCategoryList: [], // Initialize with your data
      selectedItems: [],
      selectedItemsFromBackend: [],
    };
  },
  methods: {
    updateSelectedItems(newSelectedItems) {
      console.log('Updating selected items in ParentComponent:', newSelectedItems);
      this.selectedItems = newSelectedItems;
    },

    updateSelectedItemsFromBackend(newSelectedItems) {
      console.log('Updating selected items from backend in ParentComponent:', newSelectedItems);
      this.selectedItemsFromBackend = newSelectedItems;
    },
  },
};
</script>


