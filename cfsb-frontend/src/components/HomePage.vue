<script>
export default {
  name: "HomePage",
  data() {
    return {
      policyChoice: 0,
      nodesModeChoice: 1,
      validNodesModeChoice: false,
      nodesLocation: {country: null, city: null},
      application_id: "dummy-application-id-123",
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
      localStorage.setItem('nodesLocation', JSON.stringify(this.nodesLocation));
      this.application_id = localStorage.getItem('fog_broker_app_id');
      this.validNodesModeChoice = this.verifyNMC_with_AppID();
      console.log(this.validNodesModeChoice);
      if (this.validNodesModeChoice) {
        console.log("valid")
        this.$router.push({
          name: "CriteriaSelection",
          params: {
            policyChoice: this.policyChoice,
            nodesModeChoice: this.nodesModeChoice,
          },
        });
      } else {
        let myModal = new bootstrap.Modal(document.getElementById('invalidNMCModal'));
        myModal.show();
      }
    },
    verifyNMC_with_AppID(){
      if (this.nodesModeChoice === 1 && localStorage.getItem('fog_broker_app_id') === "dummy-application-id-123" || this.nodesModeChoice === 1 && !localStorage.getItem('fog_broker_app_id')) {
        return false;
      } else {
        return true;
      }
    },
    submitAppIDForm() {
      if (this.application_id){
        localStorage.setItem('fog_broker_app_id', this.application_id);
      }
      let elem = this.$refs.modalCloseBtn
      // elem.click()
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
      <div class="col col-12 col-lg-3">
        <div class="card">
          <div class="card-header">
            <h2 class="fw-normal">Policy</h2>
          </div>
          <div class="card-body text-start">
            <p class="description">
              Select the policy used for the criteria in the evaluation
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
      <div class="col col-12 col-lg-3">
        <div class="card">
          <div class="card-header">
            <h2 class="fw-normal">Node Usage</h2>
          </div>
          <div class="card-body text-start">
            <p class="description">
              Employ all the available nodes or the application-specific nodes only
            </p>
            <form>
              <div class="form-check">
              <input v-model="nodesModeChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="nodes_mode_choice" id="nodes_choice_all" value="0">
              <label class="form-check-label" for="nodes_choice_all">All Nodes</label>
              </div>
              <div class="form-check">
                <input v-model="nodesModeChoice" @change="onChoiceChange" class="form-check-input" type="radio" name="nodes_mode_choice" id="nodes_choice_own" value="1" checked>
                <label class="form-check-label" for="nodes_choice_own">Application Specific Nodes</label>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div class="col col-12 col-lg-3">
        <div class="card">
          <div class="card-header">
            <h2 class="fw-normal">Location</h2>
          </div>
          <div class="card-body text-start">
            <p class="description">
              Provide the location (country and/or city) for nodes filtering.
            </p>
            <form>
              <input v-model="nodesLocation.country" type="text" class="form-control" id="nodes_location_country_choice" name="nodes_location_country_choice" placeholder="e.g. Norway">
              <p></p>
              <input v-model="nodesLocation.city" type="text" class="form-control" id="nodes_location_city_choice" name="nodes_location_city_choice" placeholder="e.g. Bergen">
              <div class="form-text fw-bold">Leave blank to fetch nodes without location filtering</div>
            </form>
          </div>
        </div>
      </div>
      <div class="col col-12 col-lg-3">
        <h3 class="display-6">Select Criteria</h3>
        <router-link to="/criteria-selection" class="btn button-primary btn-lg" @click.native="get_project_choices">Apply and Proceed</router-link>
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

    <!-- Invalid nodes mode choice modal -->
    <div class="modal fade" id="invalidNMCModal" aria-hidden="false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title">Invalid Nodes Mode Choice</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">

            <form @submit.prevent="submitAppIDForm">
              <div class="mb-3">
                <label for="application_id" class="form-label">Change Application ID</label>
                <input type="text" class="form-control" id="application_id" v-model="application_id" placeholder="Application ID" required>
              </div>

              <button type="submit" class="btn btn-success" data-bs-dismiss="modal">Submit</button>
            </form>

            <div v-if="!validNodesModeChoice" class="alert alert-danger">Error: The combination of App Specific Nodes with no App ID or <span class="fw-bold" v-text="this.application_id"></span> given, will fetch nodes available for <span class="fw-bold">ALL Applications</span></div>
            <div class="alert alert-info">Please type a valid app-id and click Submit or leave it blank (for ALL Applications) and click Accept & Close</div>

          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Accept & Close</button>
          </div>
        </div>
      </div>
    </div>
    <!-- end modal -->

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