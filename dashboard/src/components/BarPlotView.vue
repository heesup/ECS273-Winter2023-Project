<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce, fill, size } from 'lodash';
import { server } from '../helper';

import { Point, BarPoint, ComponentSize, Margin } from '../types';
// A "extends" B means A inherits the properties and methods from B.
interface ScatterPoint extends Point{ 
    cluster: string;
}


// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram
import { mapState, storeToRefs } from 'pinia'; 
import { useBarChartStore } from '../stores/BarChartStore';

export default {
    setup() { // Composition API syntax
        const store = useBarChartStore()
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
        }
    },
    computed: {
        ...mapState(useBarChartStore, ['selectedMethod']) // Traditional way to map the store state to the local state
    },
    created() {
        this.store.fetchExample(this.selectedMethod);
    },
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.barContainer as HTMLElement
            if (target === undefined) return;
            this.store.size = { width: target.clientWidth, height: target.clientHeight }; // How you update the store
        },
        initChart() {
            let chartContainer = d3.select('#bar-svg')


            let clusters: string[] = this.store.clusters.map((cluster: string, idx: number) => cluster[0])
            let colorScale = d3.scaleOrdinal().domain(clusters).range(d3.schemeTableau10) // d3.schemeTableau10: string[]
            // let colorScale = d3.scaleOrdinal().domain(['All', 'Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS'] 
            //                     ).range(d3.schemeTableau10) // d3.schemeTableau10: string[]
            
            var svgHeight = this.store.size.height;
            var dataSet = this.store.points;

            // var offset 만들기
            var offsetX = this.store.margin.left;
            var offsetY = this.store.margin.top;
            var bottom = this.store.margin.bottom;
            
            // let xExtents = d3.extent(this.store.clusters.map((d: Object,i) => i as number)) as [number, number]
            // let xScale = d3.scaleLinear()
            //     .range([this.store.margin.left, this.store.size.width - this.store.margin.right])
            //     .domain(xExtents)
            let xScale = d3.scaleBand()
            .range([this.store.margin.left, this.store.size.width - this.store.margin.right])
            .domain(this.store.clusters.map(d => d[1]+d[0]))
           

            // console.log(type
            // let xExtents = d3.extent(this.store.clusters.map((d: Object,i) => d as String)) as [String, String]
            // let xScale = d3.scaleBand()
            //     .range([this.store.margin.left, this.store.size.width - this.store.margin.right])
            //     .domain(xExtents)

            // range limit 정의
            var interval = 5;
            //console.log(this.store.size.height)
            let yExtents = d3.extent(this.store.points.map((d: BarPoint) => d.value as number)) as [number, number]
            //let yScale = d3.scaleLinear()
            
            
            function getScale(method: string) {
                if (method === 'failure') {
                    return d3.scaleLinear()
                } else {
                    return d3.scaleLog()
                }
            }

            let yScale = getScale(this.store.selectedMethod)
                .range([this.store.size.height - this.store.margin.bottom, this.store.margin.top])
                .domain(yExtents)

            if(this.store.selectedMethod =='failure'){
                const yAxis = chartContainer.append('g')
                .attr('transform', `translate(${offsetX}, ${0})`)
                .call(d3.axisLeft(yScale)
                .tickFormat(d => (d*100).toFixed(0) + "%")
                )
            }else{
                const yAxis = chartContainer.append('g')
                .attr('transform', `translate(${offsetX}, ${0})`)
                .call(d3.axisLeft(yScale)
                )
            
            }
                

            //그래프 그리기
            var barElements = chartContainer
                .selectAll("rect")
                .data(dataSet)

            const points = chartContainer.append('g')
                .selectAll(".bar")
                .data(this.store.points)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function (d){
                    //console.log(d.cluster[0])
                    return xScale(d.cluster[1]+d.cluster[0]) as number; // 용량 먼저
                })
                .attr("y", d => yScale(d.value))
                .attr("width", this.store.size.width/(size(this.store.points)+10))
                .attr("height", d => this.store.size.height - this.store.margin.bottom - yScale(d.value))
                .style("fill", (d: BarPoint, i:number) => colorScale(String(this.store.clusters[i][0])) as string)
                .style('opacity', .5)

            let textElements = d3.select("#bar-svg")
                .selectAll("#barNum")
                .data(this.store.clusters)


            const xAxis = chartContainer.append('g')
                .attr("class", "x axis")
                .attr('transform', `translate(0, ${this.store.size.height - this.store.margin.bottom})`)
                .call(d3.axisBottom(xScale)
                    .tickFormat(function(d){
                        //console.log(d);
                        return parseInt(d, 10).toString();// 용량 표시
                    })
                )
                .selectAll("text")
                .attr("y", 10)
                .attr("x", 0)
                .attr("dy", ".35em")
                .style('font-size', '.4rem')
                //.attr("transform", "rotate(-45)")
                .style("text-anchor", "center");

            var xElements = d3.select("#bar-svg")
                .selectAll("#barName")
                .data(dataSet)

            
            const xLabel = chartContainer.append('g')
                .attr('transform', `translate(${(this.store.size.width + this.store.margin.left) / 2 }, ${this.store.size.height - 15})`)
                .append('text')
                .text('Capacity')
                .style('font-size', '.5rem')
                .style('text-anchor', 'middle')

                const yLabel = chartContainer.append('g')
                .attr('transform', `translate(${this.store.margin.left-30}, ${this.store.size.height / 2 - this.store.margin.top}) rotate(-90)`)
                .append('text')
                .text(this.selectedMethod)
                .style('font-size', '.5rem')
                .style('text-anchor', 'middle')


            // xElements.enter()
            //     .append("text")
            //     .attr("class", "barName")
            //     .attr("x", function (d, i) {
            //         return i * 30 + 10 + interval + offsetX
            //     })
            //     .attr("y", svgHeight + 15 - offsetY)
            //     .text(function (d, i) {
            //         return ["A", "B", "C", "D", "E"][i];
            //     })
        },
        initLegend() {
            let legendContainer = d3.select('#bar-legend-svg')

            //let clusterLabels: string[] = this.store.clusters.map((cluster: string, idx: number) => `${cluster[0]}`)
            let clusterLabels: string[] = this.store.clusters.map((d) => `${d[0]}`)
            function removeDuplicates(arr:string[]) {
                return arr.filter((item, index) => arr.indexOf(item) === index);
            }
            clusterLabels = removeDuplicates(clusterLabels)
            let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)
            // let colorScale = d3.scaleOrdinal().domain(['All', 'Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS'] 
            //                     ).range(d3.schemeTableau10) // d3.schemeTableau10: string[]

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
        rerender() {
            d3.select('#bar-svg').selectAll('*').remove() // Clean all the elements in the chart
            d3.select('#bar-legend-svg').selectAll('*').remove()
            this.initChart()
            this.initLegend()
        }
    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'store.points'(newPoints) { // when data changes
            if (!isEmpty(newPoints)) {
                this.rerender()
            }
        },
        selectedMethod(newMethod) { // function triggered when a different method is selected via dropdown menu
            this.store.fetchExample(newMethod)
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
    <div class="viz-container d-flex justify-end">
        <div class="chart-container d-flex" ref="barContainer">
            <svg id="bar-svg" width="100%" height="100%">
                <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
            </svg>
        </div>
        <div id="bar-control-container" class="d-flex">
            <div class="d-flex mb-4">
                <label :style="{ fontSize: '0.7rem'}"> Select <br> Attributes:
                    <br>
                    <select class="method-select" v-model="store.selectedMethod">
                        <option v-for="method in store.methods" :value="method" 
                        :selected="(method === store.selectedMethod)? true : false">{{method}}</option>
                    </select>
                </label>
            </div>
            <svg id="bar-legend-svg" width="100%" height="100%">
            </svg>
        </div>
    </div>
</template>

<style scoped>
.viz-container{
    height:100%;
    flex-direction: row;
    flex-wrap: nowrap;
    /* for debug */
    /* border: 1px;
    border-style: dashed; */
    border: 1px solid;
    border-radius: 10px;
    border-color: rgb(0, 0, 0);
}

.chart-container{
    /* 자동 리사이즈  */
    width: calc(100% - 5rem); 
    height: 100%;
    /* for debug */
    /* border: 1px;
    border-style: dashed; */
}

#bar-control-container{
    width: 6rem;
    flex-direction: column;
}


.barNum {
  font-size: 9pt;
  text-anchor : middle;
}
.axis text {
  font-size: 11px;

}
.axis path,
.axis line {
  fill :none;
  stroke : black;
}

.axis_x line {
  fill : none;
  stroke: black;
}
.barName {
  font-size : 9pt;
  text-anchor : middle;
}
.method-select{
    outline: solid;
    outline-width: 1px;
    outline-color: lightgray;
    border-radius: 2px;
    width: 100%;
    padding: 2px 5px;
}
</style>