<template>
  <div>
    <form v-if="!isChild" @submit.prevent="submitSelection">
      <ul class="list-group">
        <li v-for="item in items" :key="item.name" class="list-group-item criteria-card">
          <span v-if="item.children.length > 0" @click="toggleCategory(item)" class="float-end" v-bind:title="'Expand ' + item.title">
            <i class="bi bi-arrow-bar-down" v-bind:aria-label="'Expand ' + item.title"></i>
          </span>
          <label>
            <!-- <input v-model="item.checked" type="checkbox" @change="handleCheckboxChange(item)" /> -->
            <input type="checkbox" :checked="item.checked" @change="() => handleCheckboxChange(item)" />
            <span @click="toggleCategory(item)" v-bind:title="item.description"> {{ item.title }} ({{ getTypeName(item.type) }}) </span>
          </label>
          <ul v-show="item.showChildren" class="list-group">
            <!-- Recursive call without Submit button -->
            <!-- <HierarchicalCategoryList :isChild="true" :items="item.children" @selected-items="updateSelectedItems" /> -->
              <HierarchicalCategoryList :isChild="true" :items="item.children" />
          </ul>
        </li>
      </ul>
      <button @click="goBackToHome" class="bg-color-primary">Back</button>
      <!-- Submit button outside the recursive structure -->
      <button type="submit" class="bg-color-primary">Next</button>
    </form>
    <div v-else>
      <li v-for="item in items" :key="item.name" class="list-group-item criteria-card">
        <span v-if="item.children.length > 0" @click="toggleCategory(item)" class="float-end" v-bind:title="'Expand ' + item.title"><i class="bi bi-arrow-bar-down" v-bind:aria-label="'Expand ' + item.title"></i></span>
        <label>
          <!--   <input v-model="item.checked" type="checkbox" @change="handleCheckboxChange(item)" />-->
          <input type="checkbox" :checked="item.checked" @change="() => handleCheckboxChange(item)" />
          <span @click="toggleCategory(item)" v-bind:title="item.description"> {{ item.title }} ({{ getTypeName(item.type) }}) </span>
         </label>
         <ul v-show="item.showChildren">
           <!-- Recursive call without Submit button
          <HierarchicalCategoryList :isChild="true" :items="item.children" @selected-items="updateSelectedItems" /> -->
           <HierarchicalCategoryList :isChild="true" :items="item.children" />
        </ul>
      </li>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    items: Array,
    isChild: {
      type: Boolean,
      default: false,
    },
    updateItemType: Function,

  },
  data() {
    return {
      localSelectedItems: [],
    };
  },
  computed: {
    computedSelectedItems() {
      return this.localSelectedItems.slice();
    },
  },
  methods: {
    toggleCategory(item) {
      item.showChildren = !item.showChildren;
    },
    handleCheckboxChange(changedItem) {
      // Toggle the checked state of the current item
      changedItem.checked = !changedItem.checked;

      // If the current item is a child and is being checked, uncheck its parent
      if (changedItem.parentId && changedItem.checked) {
        this.uncheckParent(changedItem.parentId);
      }

      // Update the selected items list
      this.updateSelectedItems();
    },
    uncheckParent(parentId) {
      const parentItem = this.findItemById(parentId, this.items);
      if (parentItem) {
        parentItem.checked = false;
      }
    },
    findItemById(id, items) {
      // Recursive function to find an item by id
      for (const item of items) {
        if (item.id === id) {
          return item;
        }
        if (item.children) {
          const foundItem = this.findItemById(id, item.children);
          if (foundItem) {
            return foundItem;
          }
        }
      }
      return null;
    },
    setChildrenVisibility(items, visible) {
      items.forEach(item => {
        item.showChildren = visible;
        if (item.children && item.children.length > 0) {
          this.setChildrenVisibility(item.children, visible);
        }
      });
    },
    updateSelectedItems() {
      // Update the selected items list with additional type information
      const selectedItemsWithType = this.items
          .filter(item => item.checked)
          .map(item => ({ name: item.name, type: item.type }));
    },
    getTypeName(type) {
      switch (type) {
        case 2: return 'Numeric';
        case 1: return 'Ordinal';
        case 5: return 'Boolean';
        case 7: return 'Ordinal';
        default: return 'Numeric';
      }
    },
    collectSelectedItems(items) {
      let selectedItems = [];
      for (const item of items) {
        if (item.checked) {
          console.log(`Selected item: ${item.name}, Type: ${item.type}, Title: ${item.title}`);
          selectedItems.push({ name: item.name, type: item.type, title: item.title });
          //console.log('Selected items in collectSelectedItems:', selectedItems); // Log selected items
        }
        if (item.children && item.children.length > 0) {
          const childSelectedItems = this.collectSelectedItems(item.children);
          selectedItems = selectedItems.concat(childSelectedItems);
        }
      }
      return selectedItems;
    },
    async submitSelection() {
      const selectedItems = this.collectSelectedItems(this.items);
      //console.log('Selected items in Submit:', selectedItems); // Log selected items

      let nonBooleanCriteriaCount = 0;
      let selectedItemsWithType = selectedItems.map(item => ({
        name: item.name,
        type: item.type,
        title: item.title
      }));

      for (const item of selectedItemsWithType) {
        console.log(`Item: ${item.name}, Type: ${item.type}`); // Add this line for debugging
        if (item.type !== 5) { // Or item.type !== 'Boolean' depending on the actual format
          nonBooleanCriteriaCount++;
        }
      }

      //console.log('Non-boolean criteria count:', nonBooleanCriteriaCount); // Log non-boolean criteria count
      console.log('selectedItemsWithType:', selectedItemsWithType);

      if (selectedItemsWithType.length < 2) {
        //console.log('Blocking submission due to insufficient criteria selection.');
        alert('Please select at least two criteria to proceed.');
        return;
      }

      if (nonBooleanCriteriaCount < 2) {
        //console.log('Blocking submission due to insufficient non-boolean criteria selection.');
        alert('Please select at least two non-boolean criteria.');
        return;
      }

      // Save the selected items with types to Local Storage
      localStorage.setItem('selectedCriteria', JSON.stringify(selectedItemsWithType));

      // Emitting the selected items with types to the DataGrid.vue
      // this.$emit('selected-items', selectedItemsWithType);

      // Navigate to DataGrid.vue, passing only the item names as route parameters
      const itemNames = selectedItemsWithType.map(item => item.name);
      this.$router.push({ name: 'DataGrid', params: { selectedItems: itemNames } });
    },
    goBackToHome() {
      this.$router.push({ name: 'HomePage' });
    }
  }
};
</script>

<style scoped>
/* Add your styling here if needed */
.custom-container {
  background-color: #f0f0f0; /* Light grey background */
  padding: 20px;
  border-radius: 8px;
}

/* Style for checkbox label */
label {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

/* Style for checkbox */
input[type="checkbox"] {
  margin-right: 5px;
}

/* Style for category name */
span {
  cursor: pointer;
  //color: #3498db; /* Blue color */
  color: var(--main-color);
  transition: color 0.3s ease;
}

span:hover {
  //color: #217dbb; /* Darker shade of blue on hover */
  color: var(--color-indigo-700);
}

/* Style for the category item */
.category-item {
  transition: background-color 0.3s ease;
}

.category-item:hover {
  background-color: #e0e0e0; /* Light grey background on hover */
}

/* Style for the submit button */
button {
  background-color: var(--main-color); /* Blue color */
  color: #fff; /* White text color */
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-bottom: 10px;
  margin-top: 10px;
}

button:hover {
  background-color: var(--secondary-color); /* Lighter shade of purple on hover */
  color: var(--main-color);
  border: 2px;
  border-color: var(--main-color);
}

ul {
  list-style-type: none;
}

.criteria-card {
  padding: 0.5rem;
  border-radius: 0.5rem;
  margin: 0.5rem;
  box-shadow: 0 3px 10px rgb(0 0 0 / 0.2);
}

.criteria-card:hover {
  background-color: var(--light-gray-color);
  color: var(--main-color);
}

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

</style>
