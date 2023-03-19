<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { server } from '../helper';

import { mapState, storeToRefs } from 'pinia'; 
import { Point, ComponentSize, Margin } from '../types';
import { useParallelStore } from '../stores/parallelCoordinate';
import { thresholdScott } from "d3";

// A "extends" B means A inherits the properties and methods from B.
interface ScatterPoint extends Point{ 
    cluster: string;
}

interface confidencePlot{
    x: number;
    y: number;
    CI_left: number;
    CI_right: number;
}

// Define your data
interface DataPoint {
    x: number;
    y: number;
    CI_left: number;
    CI_right: number;
}

interface HddLifeData{
    MFG:string;
    label?:string;
    capacity?:number;
    x:number;
    y:number;
    y_lower:number;
    y_upper:number;
}

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram

export default {
    setup() { // Composition API syntax
        const store = useParallelStore()
        // Alternative expression from computed
        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
        }
    },
    data() {
        // Here we define the local states of this component. If you think the component as a class, then these are like its private variables.
        return {
            points: [] as HddLifeData[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
            clusters: [] as string[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 50, right: 20, top: 20, bottom: 40} as Margin,
            MFGs: ['Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS'] as string[],
            selectedMFG: "All" as string,
            selectedCapacity: "" as string,
            selectedCapacityNum:0 as number,
            capacityList:[] as any[],
            capacityListLen:0 as number,
            capacityListLabels:{} as {},
            useMonth:36,
            life_exp:3 as number,
            life_exp_list:[] as number[],
            life_exp_str:"" as string,
        }
    },
    computed: {
        //...mapState(useParallelStore, ['selectedMFG']) // Traditional way to map the store state to the local state
    },
    created() {
        this.getData(this.selectedMFG)
    },
    methods: {
        getData(method: string) {
            // fetch the data via API request when we init this component. This will only get called once.
            // In axios anything we send back in the response are always bound to the "data" property.
            let api_addr:string;
            if(method ==='All'){
                api_addr = `${server}/fetchKMSurvivalCurveData`
                axios.get(api_addr)
                .then(resp => { // check out the app.py in ./server/ to see the format
                    this.points = resp.data.data; 
                    this.clusters = resp.data.clusters;
                    //console.log(resp.data.data)
                    this.capacityList = []
                    this.capacityListLabels = {}
                    this.capacityListLen = 0
                    this.selectedCapacityNum = 0
                    return true;
                })
                .catch(error => console.log(error));
            }else{
                api_addr = `${server}/fetchKMSurvivalCurveSerialData?manufacturer=${method}`
                axios.get(api_addr)
                .then(resp => { // check out the app.py in ./server/ to see the format
                    this.points = resp.data.data; 
                    this.clusters = resp.data.clusters;
                    this.capacityList = resp.data.capacity_clusters;
                    //console.log(this.capacityList)
                    const tickLabels: { [key: number]: string } = {};
                    for (let i = 0; i < this.capacityList.length; i++) {
                        tickLabels[i] = this.capacityList[i];
                    }
                    this.capacityListLabels = tickLabels
                    this.selectedCapacity = this.capacityList[this.selectedCapacityNum]
                    this.capacityListLen = this.capacityList.length
                    this.selectedCapacityNum = 0
                    this.life_exp_list = resp.data.life_exp
                    //console.log(this.life_exp_list)
                    return true;
                })
                .catch(error => console.log(error));
            }
            console.log(api_addr)

        },
        onResize() {  // record the updated size of the target element
            let target = this.$refs.simulationContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            //console.log("Init Simulation chart")
            if(this.selectedMFG === "All"){
                this.life_exp = 3
            }else{
                this.life_exp = this.life_exp_list[this.selectedCapacityNum]
                this.selectedCapacity = this.capacityList[this.selectedCapacityNum]
            }
            

            // console.log("initChart()")
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let chartContainer = d3.select('#simulation-svg')

            const data = this.points

            // Set the dimensions and margins of the graph
            
            const width = this.size.width - this.margin.left - this.margin.right;
            const height = this.size.height - this.margin.top - this.margin.bottom;


            let clusterLabels: string[] = this.clusters
            let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)
            // let colorScale = d3.scaleOrdinal().domain(['All', 'Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS'] 
            //                     ).range(d3.schemeTableau10) // d3.schemeTableau10: string[]
            
            // group the data: I want to draw one line per group
            let grouped_data;
            if(this.selectedMFG === "All"){
                grouped_data = d3.group(data, d => d.MFG);
            }else{
                grouped_data = d3.group(data, d => d.label);
            }
            
            // console.log(grouped_data)
            // console.log(grouped_data.keys())
            //////////////////////////////////////////

            // Create the scales for the X and Y axes
            const xScale = d3
            .scaleLinear()
            //.domain([0, d3.max(mfg_data, (d) => d.x) ?? 0])
            .domain([0, this.useMonth/12])
            .range([0, width]);

            let yScale = d3.scaleLinear();
            if(this.selectedMFG ==='All'){
                yScale.domain([0.6  as number,
                        d3.max(data, (d) => d.y_upper)  as number])
                        .range([height, 0]);
            }else{
                yScale.domain([d3.min(data, (d) => d.y_lower)  as number,
                            d3.max(data, (d) => d.y_upper)  as number])
            }
            yScale.range([height, 0]);

            const svg = d3
                    .select("#simulation-svg")
                    .append("svg")
                    .attr("width", width + this.margin.left + this.margin.right)
                    .attr("height", height + this.margin.top + this.margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

            // Add the X and Y axes to the SVG object
            svg
            .append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale));
            
            svg.append("g").call(d3.axisLeft(yScale)
                        .tickFormat(d=>(d*100.0).toFixed(0)+"%")
                        );

            // Define the area function
            const area = d3
                .area<HddLifeData>()
                .x(function(d) { return xScale(d.x) })
                .y0(function(d) { return yScale(d.y_lower) })
                .y1(function(d) { return yScale(d.y_upper) })
            // Define the line function
            const line = d3
                    .line<HddLifeData>()
                    .x((d) => xScale(d.x))
                    .y((d) => yScale(d.y));

            for(let i = 0;i < this.clusters.length;i++){
                // Append the SVG object to the body of the page
                const mfg_data = grouped_data.get(this.clusters[i]) as HddLifeData[]

                // Show confidence interval
                svg.append("path")
                    .datum(mfg_data)
                    .attr("fill", colorScale(clusterLabels[i]) as string)
                    //.attr("fill", "#cce5df")
                    .style('opacity', .5)
                    .attr("stroke", "none")
                    .attr("d", area)

                // Add the line to the SVG object
                svg
                .append("path")
                .datum(mfg_data)
                .attr("fill", "none")
                .attr("stroke", colorScale(clusterLabels[i]) as string)
                .attr("stroke-width", 1.5)
                .attr("d", line)      
            }

            // Draw Simulation
            // Append the SVG object to the body of the page
            if(this.capacityListLen > 0){
                //console.log(capacity_string)
                const mfg_data = grouped_data.get(`Simulation (${this.selectedCapacity})`) as HddLifeData[]
                if(this.life_exp < 20){
                    this.life_exp_str = `Life Expectancy for ${this.selectedMFG} ${this.selectedCapacity}: ${this.life_exp.toFixed(0)} Years`
                }else{
                    this.life_exp_str = `Life Expectancy for ${this.selectedMFG} ${this.selectedCapacity}: More than ${this.life_exp.toFixed(0)} Years`
                }
                // Show confidence interval
                svg.append("path")
                    .datum(mfg_data)
                    // .attr("fill", colorScale(clusterLabels[i]) as string)
                    .attr("fill", "#ff0000") // Manual Color
                    .style('opacity', .5)
                    .attr("stroke", "none")
                    .attr("d", area)

                // Add the line to the SVG object
                svg
                .append("path")
                .datum(mfg_data)
                .attr("fill", "none")
                //.attr("stroke", colorScale(clusterLabels[i]) as string)
                .attr("stroke","#ff0000" as string)
                .attr("stroke-width", 5.0)
                .attr("d", line)
            }else{
                this.life_exp_str = ""
            }


           
            
            const xLabel = chartContainer.append('g')
                .attr('transform', `translate(${(this.size.width+this.margin.left) / 2}, ${this.size.height - 15})`)
                .append('text')
                .text('Years')
                .style('font-size', '.5rem')
                .style('text-anchor', 'middle')

            const yLabel = chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left-35}, ${(this.size.height-this.margin.top) / 2}) rotate(-90)`)
                .append('text')
                .text('Survival %')
                .style('font-size', '.5rem')
                .style('text-anchor', 'middle')



        },
        initLegend() {
            let legendContainer = d3.select('#sim-legend-svg')

            //let clusterLabels: string[] = this.store.clusters.map((cluster: string, idx: number) => `${cluster[0]}`)
            let clusterLabels: string[] = this.clusters

            function removeDuplicates(arr:string[]) {
                return arr.filter((item, index) => arr.indexOf(item) === index);
            }
            clusterLabels = removeDuplicates(clusterLabels)
            if(this.capacityListLen > 0){
                clusterLabels.push(`Simulation (${this.selectedCapacity})`)
            }
            let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)
            
            //const rectSize = 12;
            let rectSize = this.size.height / (clusterLabels.length*2)
            if(rectSize > 12)
            {
                rectSize = 12
            }
            //console.log(rectSize)
            const titleHeight = 20;

            const legendGroups = legendContainer.append('g')
                .attr('transform', `translate(0, ${titleHeight})`)
                .selectAll('g')
                .data<string>(clusterLabels)
                .join((enter) => {
                    let select = enter.append('g');

                    select.append('rect')
                        .attr('width', rectSize).attr('height', rectSize)
                        .attr('x', 5).attr('y', (d: string, idx: number) => idx * rectSize * 1.5)
                        .style('fill', function (d: string,i:number) {
                            if(d.search("Simulation") > -1){
                                return "#ff0000"
                            }else{
                                return colorScale(d) as string
                            }
                        })
                        .style('opacity',function (d: string,i:number) {
                            if(d.search("Simulation") > -1){
                                return 1
                            }else{
                                return 0.5
                            }})

                    select.append('text')
                        .text((d: string) => d)
                        //.style('font-size', '.7rem')
                        .style('font-size', '.5rem')
                        .style('text-anchor', 'start')
                        .attr('x', rectSize)
                        .attr('y', (d: string, idx: number) => idx * rectSize * 1.5)
                        .attr('dx', '0.7rem')
                        .attr('dy', '0.7rem')
                    return select
                })
            
            const title = legendContainer
                .append('text')
                .style('font-size', '.7rem')
                .style('text-anchor', 'start')
                .style('font-weight', 'bold')
                //.text('MFG')
                .text(this.selectedMFG)
                .attr('x', 5)
                .attr('dy', '0.7rem')
        },
        rerender() {
            d3.select('#simulation-svg').selectAll('*').remove() // Clean all the elements in the chart
            d3.select('#sim-legend-svg').selectAll('*').remove()
            this.initChart()
            this.initLegend()
        }
    },
    watch: {
        // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                d3.select('#simulation-svg').selectAll('*').remove() // Clean all the elements in the chart
                d3.select('#sim-legend-svg').selectAll('*').remove()
                this.initChart()
                this.initLegend()
            }
        },
        'points'(newData) {
            if (!isEmpty(newData)) {
                this.rerender()
            }
        },
        'useMonth'() {
            this.rerender()
        },
        'selectedCapacityNum'() {
            this.rerender()
        },
        selectedMFG(newMFG) { // function triggered when a different method is selected via dropdown menu
            this.getData(newMFG)
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
    <div class="sim_control-container">
        <div>
            <p style="text-align:center;font-size:20px">HDD Failure Simulator</p>
        </div>

        <div class="radioMFG" style="">

            <input type="radio" name="" id="All" value="All" v-model="selectedMFG">
            <label for="All">All </label>

            <input type="radio" name="" id="Seagate" value="Seagate" v-model="selectedMFG">
            <label for="Seagate">Seagate </label>

            <input type="radio" name="" id="TOSHIBA" value="TOSHIBA" v-model="selectedMFG">
            <label for="TOSHIBA">TOSHIBA </label>
        
            <!-- <input type="radio" name="" id="HGST" value="HGST" v-model="selectedMFG">
            <label for="HGST">HGST </label> -->

            <input type="radio" name="" id="WDC" value="WDC" v-model="selectedMFG">
            <label for="WDC">WDC & HGST </label>

            <input type="radio" name="" id="Micron" value="Micron" v-model="selectedMFG">
            <label for="Micron">Micron </label>

            <!-- <input type="radio" name="" id="HP" value="HP" v-model="selectedMFG">
            <label for="HP">HP </label> -->

            <input type="radio" name="" id="Hitachi" value="Hitachi" v-model="selectedMFG">
            <label for="Hitachi">Hitachi </label>

            <!-- <input type="radio" name="" id="DELLBOSS" value="DELLBOSS" v-model="selectedMFG">
            <label for="DELLBOSS">DELLBOSS </label> -->
        </div>
        <v-app>
        <div>
            <v-slider
                label="Capacity"
                v-model="selectedCapacityNum"
                :ticks="capacityListLabels"
                :max="capacityListLen-1"
                step="1"
                show-ticks="always"
                tick-size="4"
                class="tick-labels"
                :disabled="capacityListLen===0"
                ></v-slider>

            <v-slider label="Month" v-model="useMonth" :value="useMonth" track-color="grey" 
                        always-dirty step="1" min="1" :max="life_exp*12" thumb-label hide-details
                        />
            <!-- <v-slider label="Month" v-model="useMonth" :value="useMonth" track-color="grey" 
                    always-dirty step="1" min="1" max="72" thumb-label hide-details
                        /> -->
        </div>
        <div style="text-align: center;"> {{ life_exp_str }}</div>
        </v-app>
    </div>

    <div class="sim_vis-container d-flex" > 
        <div class="sim_chart-container d-flex" ref="simulationContainer">
                <!-- <img src="src/components/Screenshot 2023-03-14 at 1.37.43 PM.png" width="475"> -->
            <svg id="simulation-svg" width="100%" height="100%">
                <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
            </svg>
        </div>

            <svg id="sim-legend-svg" width="40%" height="100%">
            </svg>
     
    </div>
    
    

</template>

<style scoped>
.sim_control-container{
    height: 40%;
    width: calc(100% - 2.5rem); 
    /* for debug */
    /* border: 1px;
    border-style: dashed; */
    flex-direction: column;
    flex-wrap: nowrap;
}
.sim_vis-container{
    height: 60%;
    width: calc(100% - 2.5rem); 
    /* for debug */
    /* border: 1px;
    border-style: dashed; */
    flex-direction: row;
    flex-wrap: nowrap;
}
.sim_chart-container{
    height: 100%;
    width: calc(100% - 2.5rem); 
    /* for debug */
    /* border: 1px;
    border-style: dashed; */
    flex-direction: row;
    flex-wrap: nowrap;
}

.radioMFG{
    font-size: 15px;
    text-align:center;
}

.tick-labels {
  font-size: 10px; /* Change this to the desired font size */
}
</style>