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
            let target = this.$refs.barContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            var svgHeight = 200
            var barElements;
            var dataSet = [120, 70, 175, 80, 220];


            // var offset 만들기
            var offsetX = 40;
            var offsetY = 10;


            // range limit 정의
            var y_range_limit = 300;

            var interval = 5;

            //그래프에 눈금 표시
            var y = d3.scaleLinear() // 눈금의 종류를 지정
                .range([y_range_limit, 0]) // 세로형 막대그래프는 range() 반대
                .domain([0, 300])

            var yScale = d3.axisLeft(y)
                .tickValues(d3.range(0, 301, 50))
                .tickFormat(function (d) { return " $" + d })

            d3.select("#bar-svg").append("g") // 눈금은 g 요소를 사용하여 그룹
                .attr("class", "axis")  // axis 라는 class 이름 지정
                // 중요 !! transform 변경
                //.attr("transform", "translate(40, 0)")  // 눈금 표시위치 transform 으로 조정
                .attr("transform", "translate(" + offsetX + ", " + ((svgHeight - y_range_limit) - offsetY) + ")")  // 눈금 표시위치 transform 으로 조정
                // == ("transform"), "translate(40,-70)"
                .call(yScale)

            //그래프 그리기
            barElements = d3.select("#bar-svg")
                .selectAll("rect")
                .data(dataSet)

            barElements.enter()
                .append("rect")
                .attr("class", "bar")
                .attr("height", function (d) {
                    return d;
                })
                .attr("width", 20)
                .attr("x", function (d, i) {
                    return i * 30 + interval + offsetX; //updated offsetX
                })
                .attr("y", function (d) {
                    return svgHeight - d - offsetY; //updated offsetY
                })
            //        .exit()

            let textElements = d3.select("#bar-svg")
                .selectAll("#barNum")
                .data(dataSet)

            textElements.enter()
                .append("text")
                .attr("class", "barNum")
                .attr("x", function (d, i) {
                    return i * 30 + 10 + interval + offsetX;    // 막대그래프 표시간격 맞춤 // updated offsetX
                })
                .attr("y", svgHeight - 5 - offsetY) //updated offsetY
                .text(function (d, i) {
                    return d;
                })
            //        .exit()

            //가로방향 선을 표시
            d3.select("#bar-svg").append("rect")
                .attr("class", "axis_x")
                .attr("width", 320)
                .attr("height", 1)
                .attr("transform", "translate(" + offsetX + ", " + ((svgHeight) - offsetY) + ")")

            var xElements = d3.select("#bar-svg")
                .selectAll("#barName")
                .data(dataSet)
                
            xElements.enter()
                .append("text")
                .attr("class", "barName")
                .attr("x", function (d, i) {
                    return i * 30 + 10 + interval + offsetX
                })
                .attr("y", svgHeight + 15 - offsetY)
                .text(function (d, i) {
                    return ["A", "B", "C", "D", "E"][i];
                })
        },
    },
    watch: {
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                d3.select('#bar-svg').selectAll('*').remove() // Clean all the elements in the chart
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
    <div class="chart-container d-flex" ref="barContainer">
        <svg id="bar-svg" width="100%" height="100%">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
        </svg>
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>