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
    x:number;
    y:number;
    y_lower:number;
    y_upper:number;
}

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram

export default {
    data() {
        // Here we define the local states of this component. If you think the component as a class, then these are like its private variables.
        return {
            points: [] as HddLifeData[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
            clusters: [] as string[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 50, right: 20, top: 20, bottom: 40} as Margin,
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
        this.getData(this.selectedMFG)
    },
    methods: {
        getData(method: string) {
            // fetch the data via API request when we init this component. This will only get called once.
            // In axios anything we send back in the response are always bound to the "data" property.
            axios.get(`${server}/fetchKMSurvivalCurveData`)
            //axios.get(`${server}/fetchKMSurvivalCurveSerialData?manufacturer=Seagate`)
                .then(resp => { // check out the app.py in ./server/ to see the format
                    this.points = resp.data.data; 
                    this.clusters = resp.data.clusters;
                    console.log(resp.data.data)
                    return true;
                })
                .catch(error => console.log(error));
        },
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let chartContainer = d3.select('#simulation-svg')
        
            // const data: DataPoint[] = [
            // { x: 0, y: 0, CI_left:.1, CI_right:.1},
            // { x: 1, y: 1, CI_left:.1, CI_right:.1},
            // { x: 2, y: 3, CI_left:.1, CI_right:.1},
            // { x: 3, y: 2, CI_left:.1, CI_right:.1},
            // { x: 4, y: 4, CI_left:.1, CI_right:.1},
            // { x: 5, y: 3, CI_left:.1, CI_right:.1},
            // ];
            const data = this.points

            // Set the dimensions and margins of the graph
            
            const width = this.size.width - this.margin.left - this.margin.right;
            const height = this.size.height - this.margin.top - this.margin.bottom;


            let clusterLabels: string[] = this.clusters
            let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)
            // let colorScale = d3.scaleOrdinal().domain(['All', 'Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS'] 
            //                     ).range(d3.schemeTableau10) // d3.schemeTableau10: string[]
            
            // group the data: I want to draw one line per group
            const grouped_data = d3.group(data, d => d.MFG);
            //console.log(grouped_data)
            //console.log(arrayFromRollup)
            //////////////////////////////////////////
            for(let i = 0;i < this.clusters.length;i++){
                // Append the SVG object to the body of the page
                let mfg_data = grouped_data.get(this.clusters[i]) as HddLifeData[]
                //console.log(mfg_data)
                const svg = d3
                    .select("#simulation-svg")
                    .append("svg")
                    .attr("width", width + this.margin.left + this.margin.right)
                    .attr("height", height + this.margin.top + this.margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

                // Create the scales for the X and Y axes
                const xScale = d3
                .scaleLinear()
                .domain([0, d3.max(data, (d) => d.x) ?? 0])
                .range([0, width]);

                const yScale = d3
                .scaleSymlog()
                .domain([0, d3.max(data, (d) => d.y) ?? 0])
                .range([height, 0]);

                // Add the X and Y axes to the SVG object
                svg
                .append("g")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(xScale));
                
                svg.append("g").call(d3.axisLeft(yScale)
                            .tickFormat(d=>d*100.0+"%")
                            );


                const area = d3
                .area<HddLifeData>()
                .x(function(d) { return xScale(d.x) })
                .y0(function(d) { return yScale(d.y_lower) })
                .y1(function(d) { return yScale(d.y_upper) })

                // Show confidence interval
                svg.append("path")
                .datum(mfg_data)
                .attr("fill", colorScale(clusterLabels[i]) as string)
                //.attr("fill", "#cce5df")
                .style('opacity', .5)
                .attr("stroke", "none")
                .attr("d", area)

                // Define the line function
                const line = d3
                .line<HddLifeData>()
                .x((d) => xScale(d.x))
                .y((d) => yScale(d.y));

                // Add the line to the SVG object
                svg
                .append("path")
                .datum(mfg_data)
                .attr("fill", "none")
                .attr("stroke", colorScale(clusterLabels[i]) as string)
                .attr("stroke-width", 1.5)
                .attr("d", line)
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
            let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)

            const rectSize = 12;
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
                        .style('fill', (d: string) => colorScale(d) as string)
                        .style('opacity', .5)

                    select.append('text')
                        .text((d: string) => d)
                        .style('font-size', '.7rem')
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
                .text('MFG')
                .attr('x', 5)
                .attr('dy', '0.7rem')
        },
    },
    watch: {
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                d3.select('#simulation-svg').selectAll('*').remove() // Clean all the elements in the chart
                this.initChart()
                this.initLegend()
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
    <div class="control-container">
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
        </v-app>
    </div>

    <div class="vis-container d-flex" > 
        <div class="chart-container d-flex" ref="scatterContainer">
                <!-- <img src="src/components/Screenshot 2023-03-14 at 1.37.43 PM.png" width="475"> -->
            <svg id="simulation-svg" width="100%" height="100%">
                <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
            </svg>
        </div>

            <svg id="sim-legend-svg" width="20%" height="100%">
            </svg>
     
    </div>
    
    

</template>

<style scoped>
.control-container{
    height: 40%;
    width: calc(100% - 5rem); 
    /* for debug */
    border: 1px;
    border-style: dashed;
    flex-direction: column;
    flex-wrap: nowrap;
}
.vis-container{
    height: 60%;
    width: calc(100% - 5rem); 
    /* for debug */
    border: 1px;
    border-style: dashed;
    flex-direction: row;
    flex-wrap: nowrap;
}
.chart-container{
    height: 100%;
    width: calc(100% - 5rem); 
    /* for debug */
    border: 1px;
    border-style: dashed;
    flex-direction: row;
    flex-wrap: nowrap;
}

.radioMFG{
    font-size: 15px;
    text-align:center;
}
</style>