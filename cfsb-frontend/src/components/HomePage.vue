<script>
export default {
  name: "HomePage",
  data() {
    return {
      policyChoice: 0,
      nodesModeChoice: 0,
    }
  },
  methods: {
    async saveIds(appId, userId) {
      fetch(' http://127.0.0.1:5000/save_ids', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          app_id: appId,
          user_id: userId,
        }),
      })
      .then(response => response.json())
      .then(data => {
            console.log('Success:', data);
            // Save to local storage
            localStorage.setItem('app_id', appId);
            localStorage.setItem('user_id', userId);
      })
      .catch((error) => {
           console.error('Error:', error);
      });
    },
    onChoiceChange() {
      console.log("Selected policy Choice:", this.policyChoice);
      console.log("Selected nodesMode Choice:", this.nodesModeChoice);
    },
    get_project_choices() {
      localStorage.setItem('policyChoice', this.policyChoice);
      localStorage.setItem('nodesModeChoice', this.nodesModeChoice);
      this.$router.push({
        name: "CriteriaSelection",
        params: {
          policyChoice: this.policyChoice,
          nodesModeChoice: this.nodesModeChoice,
        },
      });
    }
  },
  mounted() {
    // Example usage
    // this.saveIds('d535cf554ea66fbebfc415ac837a5828', 'e3ff4006-be5f-4e00-bbe1-e49a88b2541a');
  },
}
</script>

<template>
  <div class="container">
    <div class="row p-4 text-center">
      <div class="col col-12">
        <h1 class="display-2">Welcome to <span style="color: var(--main-color);">Cloud Fog Service Broker</span></h1>
      </div>
    </div>
    <div class="spacer-sm"></div>

    <div class="row text-center p-4 bg-row border-radius-sm">
      <div class="col col-12 col-lg-4">
        <div class="card">
          <div class="card-header">
            <h2>Select Policy</h2>
          </div>
          <div class="card-body text-start">
            <p class="description">
              Policy used for the criteria in the evaluation
              <!-- Put this in bubble: Rank at highest positions the nodes with lower RAM and # of Cores (Minimal policy).The opposite holds for Maximal policy.
              -->
            </p>
            <form>
              <div class="form-check">
              <input v-model="policyChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="policy_choice" id="policy_choice_minimal" value="0" checked>
              <label class="form-check-label" for="policy_choice_minimal">Minimal</label>
              </div>
              <div class="form-check">
                <input v-model="policyChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="policy_choice" id="policy_choice_maximal" value="1">
                <label class="form-check-label" for="policy_choice_maximal">Maximal</label>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div class="col col-12 col-lg-4">
        <div class="card">
          <div class="card-header">
            <h2>Use All or Specific Nodes</h2>
          </div>
          <div class="card-body text-start">
            <p class="description">
              Employ all available or application-specific nodes
            </p>
            <form>
              <div class="form-check">
              <input v-model="nodesModeChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="nodes_mode_choice" id="nodes_choice_all" value="0" checked>
              <label class="form-check-label" for="nodes_choice_all">All Available Nodes</label>
              </div>
              <div class="form-check">
                <input v-model="nodesModeChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="nodes_mode_choice" id="nodes_choice_own" value="1">
                <label class="form-check-label" for="nodes_choice_own">Application Specific Nodes</label>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div class="col col-12 col-lg-4">
        <h3 class="display-6">Try now</h3>
        <router-link to="/criteria-selection" class="btn button-primary btn-lg" @click.native="get_project_choices">Criteria Selection</router-link>
      </div>
    </div>
    <div class="spacer-sm"></div>

    <div class="row p-4 text-center bg-row border-radius-sm">
      <div class="col col-12">
        <h2 class="display-4">Architecture</h2>
      </div>
      <div class="col col-12">
        <img src="/images/Broker.png" class="img-fluid border-radius-md" alt="...">
      </div>
    </div>
  </div>

</template>

<style scoped>
button-primary:hover{
  border: 2px #172135;
}
.bg-row {
  background-color: #e9ebed;
  box-shadow: 0 3px 10px #031633;
}
.row{text-align: justify;
}
.img-fluid {
  max-width: 75%;
  height: auto;
}

.card {
  box-shadow: 0 3px 10px #031633;
}

.user-id-display {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 16px;
  color: #FFFFFF;
  font-weight: bold;
}


</style>