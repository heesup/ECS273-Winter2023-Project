<script lang="ts">
import ScatterPlotView from './components/ScatterPlotView.vue';
import BarPlotView from './components/BarPlotView.vue';
import ParallelPlotView from './components/ParallelPlotView.vue';
import SimulationView from './components/SimulationView.vue';


export default {
  components: {
    ScatterPlotView,
    BarPlotView,
    ParallelPlotView,
    SimulationView,
  }
}
</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
  <v-row no-gutters>
    <v-col cols="">
      <!-- <v-row no-gutters> -->
      <v-row style="height: 40vh" no-gutters>
        <v-col cols="" offset="">
          <ScatterPlotView/>
        </v-col>
        
        <v-col cols="" offset="">
          <BarPlotView/>
          <!-- <img src="./components/BarPlotView.png" height="300"> -->
        </v-col>
      </v-row>

      <v-row>
        <v-col offset="3" style="height: 50vh">
          <!-- <Notes msg="This message is showcasing how to pass down the props"/> -->
          <ParallelPlotView/>
          <!-- <img src="./components/ParallelPlotView.png" width="600"> -->
        </v-col>
      </v-row>
    
    </v-col>
    
    <v-col cols="" offset="3">
      <v-row no-gutters>
        <v-col style="height: 90vh">
          <SimulationView/>
          <!-- <img src="./components/SimulationView.png" height="600"> -->
        </v-col>
      </v-row>
    </v-col>

  </v-row>
  



  </v-container>
</template>

<style scoped>
#main-container{
  height: 100%;
}
</style>
