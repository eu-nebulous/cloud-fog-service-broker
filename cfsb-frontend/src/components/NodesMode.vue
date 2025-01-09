<script>

export default {
  data() {
  return {
    nodesModeChoice: 0,
    policyChoice : this.$route.params.policy,
  };
  },
  methods: {
    handleSubmit() {
      console.log("submitted nodesMode:", this.nodesModeChoice);
      this.$router.push({name: 'CriteriaSelection', params: {nodesMode: this.nodesModeChoice, policy: this.policyChoice}})
    },
    onChoiceChange() {
      console.log("Selected nodesMode Choice:", this.nodesModeChoice);
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
            <h2>Select All or Application Specific Resources</h2>
          </div>
          <div class="card-body">
            <p class="description">
              Choose to evaluate all nodes or filter yours only
            </p>
            <form @submit.prevent="handleSubmit">
              <div class="form-check">
              <input v-model="nodesModeChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="nodes_mode_choice" id="nodes_choice_all" value="0" checked>
              <label class="form-check-label" for="nodes_choice_all">All Available Nodes</label>
              </div>
              <div class="form-check">
                <input v-model="nodesModeChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="nodes_mode_choice" id="nodes_choice_own" value="1">
                <label class="form-check-label" for="nodes_choice_own">Application Specific Nodes</label>
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