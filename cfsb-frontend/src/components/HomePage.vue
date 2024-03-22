<script>
export default {
  name: "HomePage",
  // methods: {
  //   async saveIds(appId, userId) {
  //     fetch(' http://127.0.0.1:5000/save_ids', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({
  //         app_id: appId,
  //         user_id: userId,
  //       }),
  //     })
  //     .then(response => response.json())
  //     .then(data => {
  //           console.log('Success:', data);
  //           // Save to local storage
  //           localStorage.setItem('app_id', appId);
  //           localStorage.setItem('user_id', userId);
  //     })
  //     .catch((error) => {
  //          console.error('Error:', error);
  //     });
  //   }
  // },
  // mounted() {
  //   // Example usage
  //   // this.saveIds('d535cf554ea66fbebfc415ac837a5828', 'e3ff4006-be5f-4e00-bbe1-e49a88b2541a');
  // },
}
</script>

<template>
  <div class="container">
    <div class="row p-4 text-center">
      <div class="col col-12">
        <h1 class="display-2">Welcome to <span style="color: var(--main-color);">Cloud Fog Service Broker</span></h1>
      </div>
    </div>
    <!--
    <div class="row align-items-center">
      <div class="col col-12 col-md-6 col-lg-6">
        <p class="lead">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.</p>
      </div>
      <div class="col col-12 col-md-6 col-lg-6">
        <img src="https://img.freepik.com/free-vector/cloud-network-system-background-vector-social-media-banner_53876-111851.jpg?w=1380&t=st=1704656229~exp=1704656829~hmac=74f300e7d16d8e290cf82299d18aeaf12ec4705f2da8aa41504a519aa6afdb00" class="img-fluid border-radius-md" alt="Nebulous">
      </div>
    </div>

    <div class="row align-items-center">
      <div class="col col-12 col-md-6 col-lg-6">
        <img src="https://img.freepik.com/free-vector/cloud-services-isometric-composition-with-big-cloud-computing-infrastructure-elements-connected-with-dashed-lines-vector-illustration_1284-30495.jpg?w=900&t=st=1704654924~exp=1704655524~hmac=46d02fbd782b895b4f119eb0cf21e0b02d1b4bf736fc8d66b357b7ca10a7908f" class="img-fluid border-radius-md" alt="Nebulous">
      </div>
      <div class="col col-12 col-md-6 col-lg-6">
        <p class="lead">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.</p>
      </div>
    </div>
    -->
    <div class="spacer-sm"></div>

    <div class="row text-center p-4 bg-row border-radius-sm">
      <div class="col col-12 col-md-10 offset-1">
        <h3 class="display-6">Try now</h3>
        <router-link to="/criteria-selection" class="btn button-primary btn-lg">Criteria Selection</router-link>
      </div>
    </div>
    <div class="spacer-sm"></div>

    <div class="row p-4 text-center">
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
}
.row{text-align: justify;
}
.img-fluid {
  max-width: 75%;
  height: auto;
}
</style>