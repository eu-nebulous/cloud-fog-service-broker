<script>

export default {
  data() {
  return {
    policyChoice: 0,
  };
  },
  methods: {
    handleSubmit() {
      console.log("submitted Policy:", this.policyChoice);
      this.$router.push({name: 'NodesMode', params: {policy: this.policyChoice}})
    },
    onChoiceChange() {
      console.log("Selected Policy Choice:", this.policyChoice);
    }
  }
}
</script>

<template>

  <div class="spacer-sm"></div>

  <div class="container">
    <div class="row justify-content-center">
      <div class="col col-12 col-lg-8">
        <div class="card">
          <!-- Use a flex container for the header -->
          <div class="card-header d-flex justify-content-between align-items-center">
            <h2>Select Policy</h2>
          </div>
          <div class="card-body">
            <p class="description">
              Selecting a policy defines how the nodes will be evaluated
            </p>
            <form @submit.prevent="handleSubmit">
              <div class="form-check">
              <input v-model="policyChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="policy_choice" id="policy_choice_minimal" value="0" checked>
              <label class="form-check-label" for="policy_choice_minimal">Minimal</label>
              </div>
              <div class="form-check">
                <input v-model="policyChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="policy_choice" id="policy_choice_maximal" value="1">
                <label class="form-check-label" for="policy_choice_maximal">Maximal</label>
              </div>
              <button type="submit" class="bg-color-primary">Next</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<style scoped>

</style>