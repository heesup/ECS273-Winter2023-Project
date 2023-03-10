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
interface HDDFailure {
    // 'smart_5_normalized', 'smart_187_normalized', 'smart_188_normalized', 'smart_197_normalized', 'smart_198_normalized'
    // smart_1_normalized: number; // Raw Read Error Rate
    // smart_3_normalized: number; // Spin-Up Time
    smart_5_normalized: number; // Reallocated Sector Count
    // smart_7_normalized: number; // Seek Error Rate
    // smart_9_normalized: number; // Power-On Hours
    smart_187_normalized: number; // Reported Uncorrectable Errors
    smart_188_normalized: number; // Command Timeout
    // smart_194_normalized: number; // Temperature
    smart_197_normalized: number; // Uncorrectable Sector Count
    smart_198_normalized: number; // Current Pending Sector Count 
    MFG: string; // Manufaturer
    failure: number;
}

// 'Reallocated Sector Count', 'Reported Uncorrectable Errors', 'Command Timeout', 'Uncorrectable Sector Count', 'Current Pending Sector Count', 'Manufaturer'

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram

export default {
    data() {
        // Here we define the local states of this component. If you think the component as a class, then these are like its private variables.
        return {
            points: [] as ScatterPoint[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
            clusters: [] as string[],
            HDDFailure_data: [] as HDDFailure[],
            columns: [] as string[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 20, right: 20, top: 60, bottom: 60} as Margin,
        }
    },
    computed: {
        // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
        rerender() {
            return (!isEmpty(this.HDDFailure_data)) && this.size
        }
    },
    created() {
        // fetch the data via API request when we init this component. This will only get called once.
        // In axios anything we send back in the response are always bound to the "data" property.
        axios.get(`${server}/fetchParallelData`)
            .then(resp => { // check out the app.py in ./server/ to see the format
                this.HDDFailure_data = resp.data.data; 
                this.clusters = resp.data.clusters;
                this.columns = resp.data.columns;

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
            var margin = {top: 50, right: 80, bottom: 40, left: 5},
                            width = this.size.width - margin.left - margin.right,
                            height = this.size.height - margin.top - margin.bottom;

            var svg = d3.select("#parallel-svg")
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

            let domain_org = this.columns;

            const domains = d3.csvParse(domain_org.join(','));
            const domains_len = domains.length;

            const data = this.HDDFailure_data;
            let dimensions = domains['columns'].filter(function(d) { return d != "failure" })

            // console.log(dimensions)

            // For each dimension, I build a linear scale. I store all in a y object
            let y = {} 
            for (let i in domain_org) {
                let name = dimensions[i]

                if (name !== 'MFG') {
                    y[name] = d3.scaleLinear()
                        .domain( d3.extent(data, function(d) { return +d[name]; }) )
                        .range([height, 0])
                }
                else{
                    y[name] = d3.scalePoint()
                        .domain(data.map(d => d[name]))
                        .range([height, 0]);
                }

            }

            // Build the X scale -> it find the best position for each Y axis
            let x = d3.scalePoint()
                .range([0, width])
                .padding(1)
                .domain(dimensions);

            const color = d3.scaleOrdinal()
                            .domain([0, 1])
                            .range(['green', 'red'])

            function path(d) {
                return d3.line()(dimensions.map(function(p) { return [x(p), y[p](d[p])]; }));
            }

            // Draw the lines
            const paths = svg.selectAll("myPath")
                // .data(data.reverse())
                .data(data)
                .join("path")
                    .attr("d", path)
                    .attr("class", function (d) { return "line " + d.failure } )
                    .attr("stroke-width", 0.1)
                    .style("fill", "none")
                    .style("opacity", 0.9)
                    .style("stroke", function(d){ return( color(d.failure))} )
                    // .style("stroke", (d: number) => d === 1 ? 'red' : 'grey' )

            // const column_name: string[] = ['Raw Read Error Rate', 'Spin-Up Time', 'Reallocated Sector Count', 'Seek Error Rate', 'Power-On Hours', 'Temperature', 'Uncorrectable Sector Count', 'Current Pending Sector Count', 'Manufacturers']

            const column_name: string[] = ['Reallocated Sector Count', 'Reported Uncorrectable Errors', 'Command Timeout', 'Uncorrectable Sector Count', 'Current Pending Sector Count', 'Manufaturer']                    

            // Draw the axis:
            const Axis = svg.selectAll("myAxis")
                .data(dimensions).enter()
                .append("g")
                .attr("transform", function(d) { return "translate(" + x(d) + ")"; })
                .each(function(d) { d3.select(this).call(d3.axisLeft().scale(y[d])); })
                .append("text")
                    .style("font", "7px sans-serif")
                    .style("text-anchor", "start")
                    .attr("y", -9)
                    // .text(function(d) { return d; })
                    .text(function(d, i) { return column_name[i]; })
                        .style("fill", "black")
                        .attr("transform", "rotate(-15)")
            
            const title = svg.append('g')
                .append('text') // adding the text
                .attr('transform', `translate(${width / 2}, ${height+20})`)
                .attr('dy', '0.5rem') // relative distance from the indicated coordinates.
                .style("font", "15px sans-serif")
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .text('Parallel Coordinate') // text
        },
        initLegend() {
            let legendContainer = d3.select('#parallel-legend-svg');

            // let clusterLabels: string[] = this.clusters.map((cluster: string, idx: number) => `Cultivar ${idx+1}`)
            let clusterLabels: string[] = this.clusters
            // let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)
            // let colorScale = d3.scaleOrdinal()
                                // .domain(clusterLabels)
                                // .range(['grey', 'red'])

            const rectSize = 12;
            const titleHeight = 20;

            // This is further utilizing data joins in d3.js, you can find the equivalent code in the comments below.
            // Check out https://observablehq.com/@d3/selection-join
            const legendGroups = legendContainer.append('g')
                .attr('transform', `translate(0, ${titleHeight})`) // this is applied to "g" element and will affect all the child elements.
                .selectAll('g')
                .data<string>(clusterLabels)
                .join((enter) => { // This enter syntax is recommended when you want to join multiple non-nested elements per data point
                    // This callback here is for newly added elements.
                    let select = enter.append('g');

                    select.append('rect')
                        .attr('width', rectSize).attr('height', rectSize)
                        .attr('x', 5).attr('y', (d: string, idx: number) => idx * rectSize * 1.5)
                        .style('fill', (d: number) => d === 1 ? 'red' : 'green')

                    select.append('text')
                        // .text((d: string) => d)
                        .text((d: number) => d === 1 ? 'Failure':'Healthy')
                        .style('font-size', '.7rem')
                        .style('text-anchor', 'start')
                        .attr('x', rectSize)
                        .attr('y', (d: string, idx: number) => idx * rectSize * 1.5)
                        .attr('dx', '0.7rem')
                        .attr('dy', '0.7rem')
                    return select
                }, // you can add callbacks for updating elements and removing elements as other arguments here.
            );
            const title = legendContainer
                .append('text')
                .style('font-size', '.7rem')
                .style('text-anchor', 'start')
                .style('font-weight', 'bold')
                .text('HDD State')
                .attr('x', 5)
                .attr('dy', '0.7rem')
        }
    },    
    watch: {
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                d3.select('#parallel-svg').selectAll('*').remove()
                d3.select('#parallel-legend-svg').selectAll('*').remove()
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
    <div class="chart-container d-flex" ref="scatterContainer">
        <svg id="parallel-svg" width="100%" height="100%">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
        </svg>
        <div id="scatter-control-container" class="d-flex">
            <svg id="parallel-legend-svg" width=100 height="40%">
            </svg>
        </div>

    </div>
</template>

<style scoped>
.viz-container{
    height:100%;
    flex-direction: row;
    flex-wrap: nowrap;
}
.chart-container{
    width: calc(100% - 5rem);
    height: 100%;
}

#parallel-legend-container{
    width: 5rem;
}
</style>