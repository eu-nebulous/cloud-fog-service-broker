<template>
  <div class="row" style="padding-bottom: 2rem">
  </div>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col col-12 col-lg-8">
        <div class="card">
          <div class="card-header">
            <h2>Selection of Criteria</h2>
          </div>
          <div class="card-body">
            <HierarchicalCategoryList
                :items="hierarchicalCategoryList"
                @selected-items="updateSelectedItems"
            ></HierarchicalCategoryList>
          </div>
        </div>
        <!-- <div>Selected Items Length: {{ selectedItems.length }}</div>
        <button v-if="selectedItems.length > 0" @click="navigateToDataGrid">Go to DataGrid</button> -->
      </div>
    </div>
  </div>
</template>

<script>
import HierarchicalCategoryList from "@/components/HierarchicalCategoryList.vue";

export default {
  components: {
    HierarchicalCategoryList
  },
  data() {
    return {
      hierarchicalCategoryList: [],
      selectedItems: [],
    };
  },
  mounted() {
    console.log('CriteriaSelection.vue mounted');
    this.fetchHierarchicalCategoryList();
  },
  methods: {
    async fetchHierarchicalCategoryList() {
      try {
        const response = await fetch('http://127.0.0.1:5000/get_hierarchical_category_list');
        const data = await response.json();
        this.hierarchicalCategoryList = data;
      } catch (error) {
        console.error('Error fetching hierarchical category list:', error);
      }
    },
    navigateToDataGrid() {
      console.log('Navigating to DataGrid');
      this.$router.push({ name: 'DataGrid' });
    },
    updateSelectedItems(newSelectedItems) {
      //console.log('Updating selected items in CriteriaSelection.vue:', newSelectedItems);
      this.selectedItems = newSelectedItems;
    },
  },
};
</script>


