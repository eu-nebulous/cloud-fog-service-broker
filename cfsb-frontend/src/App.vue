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
    <footer class="footer text-center p-2">
      <span class="text-white">&copy NebulOus</span>
    </footer>
  </div>
</template>

<style>
:root {
  --main-color: #7030A0;
  --secondary-color: #e0cffc;
  --color-indigo-700: #3d0a91;
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
}
</style>

<script>
export default {
  name: 'App',
  methods: {
    goToCriteriaSelection() {
      this.$router.push('/criteria-selection');
    }
  },
  computed: {
    showCriteriaSelectionButton() {
      return this.$route.path === '/';  /* other conditions */
    }
  },
};
</script>

