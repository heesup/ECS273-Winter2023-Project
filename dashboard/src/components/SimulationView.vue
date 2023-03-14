<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin } from '../types';
// A "extends" B means A inherits the properties and methods from B.
interface ScatterPoint extends Point{ 
    cluster: string;
}

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram

export default {
    data() {
        // Here we define the local states of this component. If you think the component as a class, then these are like its private variables.
        return {
            points: [] as ScatterPoint[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
            clusters: [] as string[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 20, right: 20, top: 20, bottom: 40} as Margin,
            MFGs: ['Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS'] as string[],
            selectedMFG: "Seagate" as string,
            selectedCapacity: 0 as number,
            useMonth:0,
        }
    },
    computed: {
        // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
        rerender() {
            return (!isEmpty(this.points)) && this.size
        }
    },
    created() {
        // fetch the data via API request when we init this component. This will only get called once.
        // In axios anything we send back in the response are always bound to the "data" property.
        axios.get(`${server}/fetchExample`)
            .then(resp => { // check out the app.py in ./server/ to see the format
                this.points = resp.data.data; 
                this.clusters = resp.data.clusters;
                return true;
            })
            .catch(error => console.log(error));
    },
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let chartContainer = d3.select('#simulation-svg')

        },
    },
    watch: {
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                d3.select('#simulation-svg').selectAll('*').remove() // Clean all the elements in the chart
                this.initChart()
            }
        }
    },
    // The following are general setup for resize events.
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100)) 
        this.onResize()
    },
    beforeDestroy() {
       window.removeEventListener('resize', this.onResize)
    }
}
</script>

<!-- "ref" registers a reference to the HTML element so that we can access it via the reference in Vue.  -->
<!-- We use flex to arrange the layout-->
<template>
    <div>
        <p style="text-align:center;font-size:20px">HDD Failure Simulator</p>
    </div>

    <div class="radioMFG" style="">

        <input type="radio" name="" id="Seagate" value="Seagate" v-model="selectedMFG">
        <label for="Seagate">Seagate</label>

        <input type="radio" name="" id="TOSHIBA" value="TOSHIBA" v-model="selectedMFG">
        <label for="TOSHIBA">TOSHIBA</label>
      
        <input type="radio" name="" id="HGST" value="HGST" v-model="selectedMFG">
        <label for="HGST">HGST</label>

        <input type="radio" name="" id="WDC" value="WDC" v-model="selectedMFG">
        <label for="WDC">WDC</label>

        <input type="radio" name="" id="Micron" value="Micron" v-model="selectedMFG">
        <label for="Micron">Micron</label>

        <input type="radio" name="" id="HP" value="HP" v-model="selectedMFG">
        <label for="HP">HP</label>

        <input type="radio" name="" id="Hitachi" value="Hitachi" v-model="selectedMFG">
        <label for="Hitachi">Hitachi</label>

        <input type="radio" name="" id="DELLBOSS" value="DELLBOSS" v-model="selectedMFG">
        <label for="DELLBOSS">DELLBOSS</label>
    </div>

    <div style="text-align:center;font-size: 15px;">
        Capacity (TB)
        <select name="" v-model="selectedCapacity">
            <!-- Todo: Add MFG and Capacity Combination -->
            <option value=2>2TB</option>
            <option value=4>4TB</option>
            <option value=6>6TB</option>
            <option value=8>8TB</option>
            <option value=10>10TB</option>
            <option value=12>12TB</option>
            <option value=14>14TB</option>
            <option value=16>16TB</option>
        </select>
    </div>

    <v-app>
        <div>
            <!-- <v-slider label="Capacity" v-model="slider" :value="slider" track-color="grey" always-dirty min="1" max="36" thumb-label="always"/> -->
            <v-slider label="Capacity" v-model="selectedCapacity" :value="selectedCapacity" track-color="grey" always-dirty min="1" max="36" thumb-label/>
            <v-slider label="Month" v-model="useMonth" :value="useMonth" track-color="grey" always-dirty min="1" max="36" thumb-label/>
            <!-- 임시로 -->
            
        </div>
        <div class="chart-container d-flex" ref="scatterContainer"> 
            <img src="src/components/Screenshot 2023-03-14 at 1.37.43 PM.png" width="475">
        <svg id="simulation-svg" width="100%" height="100%">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
        </svg>
        </div>
    </v-app>
    


</template>

<style scoped>
.chart-container{
    width: calc(100% - 5rem);
    height: 100%;
    /* for debug */
    border: 1px;
    border-style: dashed;
}
.radioMFG{
    font-size: 15px;
    text-align:center;
}
</style>