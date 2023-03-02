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
  <v-row>
    <v-col cols="7">
      <v-row no-gutters>
        <v-col cols="7">
          <ScatterPlotView/>
          <!-- <img src="./components/ScatterPlotView.png" height="300"> -->
        </v-col>
        
        <v-col cols="3">
          <!-- <BarPlotView/> -->
          <img src="./components/BarPlotView.png" height="300">
        </v-col>
      </v-row>
      
      <v-row no-gutters>
        <v-col>
          <!-- <Notes msg="This message is showcasing how to pass down the props"/> -->
          <!-- <ParallelPlotView/> -->
          <img src="./components/ParallelPlotView.png" width="730">
        </v-col>
      </v-row>
    </v-col>
    
    <v-col cols="3">
      <v-row no-gutters>
        <v-col>
          <!-- <SimulationView/> -->
          <img src="./components/SimulationView.png" height="600">
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
