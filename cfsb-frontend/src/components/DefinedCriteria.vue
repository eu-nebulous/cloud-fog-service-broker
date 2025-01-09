<script>
export default {
  props: {
    criteria: {
      type: Array,
      required: true
    },
    providers: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      options: ["Low", "Medium", "High"],
      selections: {},
      criteria_selections: {},
    };
  },
  methods: {
    updateSelection(provider, criterion, value) {
      const providerKey = String(provider);
      const criterionKey = String(criterion.title);
      console.log(criterionKey);
      if (!this.selections[providerKey]) {
        this.selections[providerKey] = {};
        this.criteria_selections[providerKey] = {};
      }
      this.selections[providerKey][criterionKey] = value;
      console.log(this.selections[providerKey][criterionKey]);
      this.$emit("criteriaUpdated", this.selections); // Emit selections
      // try to save the selections per provider with original criterion name (attr-accountability)
      const criterionName = String(criterion.name);
      this.criteria_selections[providerKey][criterionName] = value;
      let provider_selections = JSON.stringify(this.criteria_selections);
      localStorage.setItem('provider_selections', provider_selections); // store the selections per provider
    }
  }
};
</script>

<template>
<h3>Please provide your input for the following criteria:</h3>


  <table>
    <thead>
      <tr>
        <th>Provider</th>
        <th v-for="criterion in criteria" :key="criterion.title">{{ criterion.title }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="provider in providers" :key="provider">
        <td>{{ provider }}</td>
        <td v-for="criterion in criteria" :key="criterion">
          <select @input="updateSelection(provider, criterion, $event.target.value)">
            <option v-for="option in options" :key="option" :value="option">{{ option }}</option>
          </select>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>

</style>