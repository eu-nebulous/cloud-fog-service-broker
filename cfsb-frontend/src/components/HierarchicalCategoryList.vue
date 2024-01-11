<template>
  <div>
    <form v-if="!isChild" @submit.prevent="submitSelection">
      <ul class="list-group">
        <li v-for="item in items" :key="item.name" class="list-group-item criteria-card">
          <span v-if="item.children.length > 0" @click="toggleCategory(item)" class="float-end" v-bind:title="'Expand ' + item.title"><i class="bi bi-arrow-bar-down" v-bind:aria-label="'Expand ' + item.title"></i></span>
          <label>
            <!--
            <input v-model="item.checked" type="checkbox" @change="handleCheckboxChange(item)" />
            <span @click="toggleCategory(item)" v-bind:title="item.description">{{ item.title }}</span>  -->
            <input type="checkbox" :checked="item.checked" @change="() => handleCheckboxChange(item)" />
            <span @click="toggleCategory(item)">{{ item.title }}</span>
          </label>
          <ul v-show="item.showChildren" class="list-group">
            <!-- Recursive call without Submit button -->
            <HierarchicalCategoryList :isChild="true" :items="item.children" @selected-items="updateSelectedItems" />
          </ul>
        </li>
      </ul>
      <!-- Submit button outside the recursive structure -->
      <button type="submit" class="bg-color-primary">Submit</button>
    </form>
    <div v-else>
      <li v-for="item in items" :key="item.name" class="list-group-item criteria-card">
        <span v-if="item.children.length > 0" @click="toggleCategory(item)" class="float-end" v-bind:title="'Expand ' + item.title"><i class="bi bi-arrow-bar-down" v-bind:aria-label="'Expand ' + item.title"></i></span>
        <label>
          <!--   <input v-model="item.checked" type="checkbox" @change="handleCheckboxChange(item)" />
           <span @click="toggleCategory(item)" v-bind:title="item.description">{{ item.title }}</span>  -->
          <input type="checkbox" :checked="item.checked" @change="() => handleCheckboxChange(item)" />
          <span @click="toggleCategory(item)">{{ item.title }}</span>
        </label>
        <ul v-show="item.showChildren">
          <!-- Recursive call without Submit button -->
          <HierarchicalCategoryList :isChild="true" :items="item.children" @selected-items="updateSelectedItems" />
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
  },
  data() {
    return {
      localSelectedItems: [],
      selectedItemsFromBack: [],
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
    updateSelectedItems() {
      // Update the selected items list
      this.localSelectedItems = this.collectSelectedItems(this.items);
      // Emit the updated list
      this.$emit('selected-items', this.localSelectedItems);
    },
    collectSelectedItems(items) {
      let selectedItems = [];
      for (const item of items) {
        if (item.checked) {
          selectedItems.push(item.name);
        }
        if (item.children) {
          selectedItems = selectedItems.concat(this.collectSelectedItems(item.children));
        }
      }
      return selectedItems;
    },
    submitSelection() {
      const selectedItems = this.collectSelectedItems(this.items);

      if (selectedItems.length < 2) {
        alert('Please select at least two items before submitting.');
        return;
      }

      // Emitting the selected items - useful if there's a parent component listening to this event
      this.$emit('selected-items', selectedItems);

      // Programmatic navigation to the DataGrid page, passing the selected items as route parameters
      this.$router.push({ name: 'DataGrid', params: { selectedItems: selectedItems } });
    },
    async postSelectedItems(selectedItems) {
      const requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({selectedItems}),
      };
      const response = await fetch('http://127.0.0.1:5000/process_selected_items', requestOptions);
      const data = await response.json();
      //console.log('Send Selected items to back', data);
      this.selectedItemsFromBack = data;
    },
  },
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
</style>
