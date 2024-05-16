<template>
  <div id="app">
       <!-- Header section (if any) -->
    <header>
      <!-- Navigation, branding, etc. -->
    </header>

    <nav class="navbar navbar-expand-lg bg-color-primary" data-bs-theme="dark">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">NebulOuS</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link to="/" class="nav-link text-white">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/criteria-selection" class="nav-link text-white">Criteria Selection</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
        <router-view></router-view>

    <!-- Main content where routed components will be displayed -->
    <!--  <router-view></router-view>
      <button v-if="showCriteriaSelectionButton" @click="goToCriteriaSelection">Go to Criteria Selection</button> -->

    <div class="modal fade" id="userLoginModal" aria-hidden="false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title">User login</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">

            <form @submit.prevent="submitUserLoginForm">
              <div class="mb-3">
                <label for="app_id" class="form-label">Insert Application ID</label>
                <input type="text" class="form-control" id="app_id" v-model="app_id" placeholder="Application ID" required>
              </div>
              <div class="mb-3">
                <label for="username" class="form-label">Your username</label>
                <input type="text" class="form-control" id="username" v-model="username" placeholder="Username" required>
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Your password</label>
                <input type="password" class="form-control" id="password" v-model="password" placeholder="Password" required>
              </div>

              <button type="submit" class="btn btn-success">Login</button>
            </form>

            <div v-if="!login" class="alert alert-danger">Error</div>

          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" ref="modalCloseBtn">Close</button>
          </div>
        </div>
      </div>
    </div>

    <footer class="footer text-center p-2">
      <span class="text-white">&copy NebulOus - Cloud Fog Service Broker</span>
    </footer>
  </div>
</template>

<style>
:root {
  --main-color: #1b253b;
  --secondary-color: #e0cffc;
  --color-indigo-700: #172135;
  --light-gray-color: #f8f9fa;
  --medium-gray-color: #6c757d;
}

.color-primary {
  color: var(--main-color);
}
.bg-color-primary {
  background-color: var(--main-color);
}

.text-white {
  color: #FFFFFF;
}

.button-primary {
  background-color: var(--main-color); /* Blue color */
  color: #fff; /* White text color */
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.button-primary:hover {
  background-color: var(--secondary-color); /* Lighter shade of purple on hover */
  color: var(--main-color);
  border: 2px;
  border-color: var(--main-color);
}

.border-radius-sm {
  border-radius: 1rem;
}

.border-radius-md {
  border-radius: 2rem;
}

.spacer-sm {
  padding-top: 1rem;
}

.spacer-sm {
  padding-top: 2rem;
}

.footer {
  background-color: var(--main-color);
  margin-top: 15px;
}
</style>

<script>
export const backendURL = import.meta.env.VITE_BACKEND_URL;
const apiURL = backendURL;
export default {
  name: 'App',
  data() {
    return {
      username: "",
      password: "",
      uuid: "",
      app_id: "",
      login: true
    }
  },
  methods: {
    goToCriteriaSelection() {
      this.$router.push('/criteria-selection');
    },
    checkUserLogin() {
      let uuid = localStorage.getItem('fog_broker_user_uuid');
      if (uuid) {
        console.log("user is set");
      } else {
        console.log("user not set");
        let myModal = new bootstrap.Modal(document.getElementById('userLoginModal'));
        myModal.show();
      }
    },
    async submitUserLoginForm() {
      console.log('username = :', this.username);
      let user_data = {
        'username': this.username,
        'password': this.password,
        'app_id': this.app_id,
      }
      let result = await this.fetchUser(user_data)
      this.username = "";
      this.password = "";
    },
    async fetchUser(user_data) {
      try {
        const response = await fetch(apiURL+'/login', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(user_data)
        });
        const data = await response.json();
        console.log(data);
        if (data.length===1) {
          this.uuid = data[0][2];
          console.log(data[0][2]);
          localStorage.setItem('fog_broker_user_uuid', data[0][2]);
          localStorage.setItem('fog_broker_app_id', user_data.app_id);
          let elem = this.$refs.modalCloseBtn
          elem.click()
          this.login = true;
        } else {
          this.login = false;
        }
      } catch (error) {
        console.error('Error fetching user:', error);
      }
    },
    setDefaultUser() {
      localStorage.setItem('fog_broker_user_uuid', 'e3ff4006-be5f-4e00-bbe1-e49a88b2541a');
      localStorage.setItem('fog_broker_app_id', '2f7cc63df4b1da7532756f44345758da');
    },
    getURLparams() {
      let app_in_url = false
      let user_in_url = false
      let app_id_from_js = new URL(location.href).searchParams.get('app_id');
      let user_id_from_js = new URL(location.href).searchParams.get('user_id');

      if (app_id_from_js) {
        console.log('app_id from URL:', app_id_from_js);
        this.app_id = app_id_from_js;
        app_in_url = true;
        localStorage.setItem('fog_broker_app_id', this.app_id);
      }
      if (user_id_from_js) {
        console.log('user_id from URL:', user_id_from_js);
        this.uuid = user_id_from_js;
        user_in_url = true
        localStorage.setItem('fog_broker_user_uuid', this.uuid);
      }
      if (app_in_url && user_in_url){
        return true
      } else {
        return false
      }
    },
  },
  computed: {
    showCriteriaSelectionButton() {
      return this.$route.path === '/';  /* other conditions */
    }
  },
  mounted() {
    this.getURLparams();
    // this.checkUserLogin();
    this.setDefaultUser();
  }
};
</script>

