<template>
  <div class="row" style="padding-bottom: 2rem">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col col-12 col-md-8">
          <div v-if="!this.policy || !this.nodesMode" class="alert alert-warning">
            <p>Policy or Nodes Mode have not been set.</p>
            <p>Default policy is set to <span class="fw-bold">Minimal</span> and default Nodes Mode is set to <span class="fw-bold">Bring All Nodes</span></p>
            <button @click="goBackToHome" class="bg-color-primary">Change Settings</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col col-12 col-lg-8">
        <div class="card">
          <!-- Use a flex container for the header -->
          <div class="card-header d-flex justify-content-between align-items-center">
            <h2>Selection of Criteria</h2>
            <!-- Clickable icon and text for expanding/collapsing -->
            <span class="expand-collapse-link" @click="toggleExpandAll">
              <i v-bind:class="expandIconClass"></i>{{ expandButtonText }}</span>
          </div>
          <div class="card-body">
            <p class="description">
              Please select at least two criteria to proceed.
            </p>
            <!-- HierarchicalCategoryList is included here with the necessary bindings -->
            <HierarchicalCategoryList ref="hierarchicalList" :items="hierarchicalCategoryList" @selected-items="updateSelectedItems"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>

export const backendURL = import.meta.env.VITE_BACKEND_URL;
const apiURL = backendURL;
import HierarchicalCategoryList from "@/components/HierarchicalCategoryList.vue";

export default {
  components: {
    HierarchicalCategoryList
  },
  data() {
    return {
      hierarchicalCategoryList: [],
      selectedItems: [],
      allCategoriesExpanded: false,
      policy: null,
      nodesMode: null
    };
  },
  mounted() {
    console.log('CriteriaSelection.vue mounted');
    this.fetchHierarchicalCategoryList();
    this.policy = this.$route.params.policyChoice || localStorage.getItem("policyChoice");
    this.nodesMode = this.$route.params.nodesModeChoice || localStorage.getItem("nodesModeChoice");
    if (!this.policy || !this.nodesMode) {
      this.policy = 0;
      this.nodesMode = 0;
      console.log('set default policy to ', this.policy, 'and default nodes to', this.nodesMode);
      localStorage.setItem('policyChoice', this.policy);
      localStorage.setItem('nodesModeChoice', this.nodesMode);
    } else {
      console.log('policy chosen', this.policy, 'and nodes chosen', this.nodesMode);
    }
  },
  computed: {
    expandButtonText() {
      return this.allCategoriesExpanded ? 'Collapse All' : 'Expand All';
    },
    expandIconClass() {
      return this.allCategoriesExpanded ? 'bi-arrow-bar-up' : 'bi-arrow-bar-down';
    }
  },
  methods: {
    async fetchHierarchicalCategoryList() {
      try {
        const response = await fetch(apiURL+'/get_hierarchical_category_list');
        const data = await response.json();
        this.hierarchicalCategoryList = data;
      } catch (error) {
        console.error('Error fetching hierarchical category list:', error);
      }
    },
    toggleExpandAll() {
      this.allCategoriesExpanded = !this.allCategoriesExpanded;
      if (this.$refs.hierarchicalList) {
        this.$refs.hierarchicalList.setChildrenVisibility(this.hierarchicalCategoryList, this.allCategoriesExpanded);
      }
    },
    updateSelectedItems(newSelectedItems) {
      //console.log('Updating selected items in CriteriaSelection.vue:', newSelectedItems);
      this.selectedItems = newSelectedItems;
    },
    goBackToHome() {
      this.$router.push({ name: 'HomePage' });
    }

  },

};
</script>

<style>
button {
  //color: var(--main-color);
  border: 2px solid;
  border-color:  #1B253BFF;
}

button:hover {
  background-color: #e9ebed;
  color: var(--main-color);
  border: 2px solid;
  border-color: var(--main-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expand-collapse-link {
  cursor: pointer;
  color: var(--color-indigo-700);  user-select: none;
  display: flex;
  align-items: center; /* Aligns the icon and text vertically */
}

.expand-collapse-link i {
  margin-right: 0.5rem; /* Add some space between the icon and text */
}

</style>