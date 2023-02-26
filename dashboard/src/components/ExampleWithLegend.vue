<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin } from '../types';
interface ScatterPoint extends Point{
    cluster: string;
}

/* The new major things from Example.vue
1) initLegend() in this component
2) the template and the css in this component
*/

export default {
    data() {
        return {
            points: [] as ScatterPoint[],
            clusters: [] as string[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 20, right: 20, top: 20, bottom: 40} as Margin,
        }
    },
    computed: {
        rerender() {
            return (!isEmpty(this.points))  && this.size
        }
    },
    created() {
        axios.get(`${server}/fetchExample`)
            .then(resp => {
                this.points = resp.data.data;
                this.clusters = resp.data.clusters;
                return true;
            })
            .catch(error => console.log(error));
    },
    methods: {
        onResize() {
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined || target === null) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            let chartContainer = d3.select('#scatter-svg')

            let xExtents = d3.extent(this.points.map((d: ScatterPoint) => d.posX as number)) as [number, number]
            let yExtents = d3.extent(this.points.map((d: ScatterPoint) => d.posY as number)) as [number, number]

            let xScale = d3.scaleLinear()
                .range([this.margin.left, this.size.width - this.margin.right])
                .domain(xExtents)

            let yScale = d3.scaleLinear()
                .range([this.size.height - this.margin.bottom, this.margin.top])
                .domain(yExtents)

            let clusters: string[] = this.clusters.map((cluster: string, idx: number) => String(idx))
            let colorScale = d3.scaleOrdinal().domain(clusters).range(d3.schemeTableau10) // d3.schemeTableau10: string[]

            const points = chartContainer.append('g')
                .selectAll('circle')
                .data<ScatterPoint>(this.points)
                .join('circle')
                .attr('cx', (d: ScatterPoint) => xScale(d.posX))
                .attr('cy', (d: ScatterPoint) => yScale(d.posY))
                .attr('r', 5)
                .style('fill', (d: ScatterPoint) => colorScale(String(d.cluster)) as string)
                .style('opacity', .7)

            const title = chartContainer.append('g')
                .append('text')
                .attr('transform', `translate(${this.size.width / 2}, ${this.size.height - this.margin.top})`)
                .attr('dy', '0.5rem')
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .text('Wine Dataset PCA Projection')
        },
        initLegend() {
            let legendContainer = d3.select('#scatter-legend-svg')

            let clusterLabels: string[] = this.clusters.map((cluster: string, idx: number) => `Cultivar ${idx+1}`)
            let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)

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
                        .style('fill', (d: string) => colorScale(d) as string)

                    select.append('text')
                        .text((d: string) => d)
                        .style('font-size', '.7rem')
                        .style('text-anchor', 'start')
                        .attr('x', rectSize)
                        .attr('y', (d: string, idx: number) => idx * rectSize * 1.5)
                        .attr('dx', '0.7rem')
                        .attr('dy', '0.7rem')
                    return select
                }, // you can add callbacks for updating elements and removing elements as other arguments here.
                )
            
            /* // Equivalent to above, but iterates through data twice.
            const rects = legendContainer.append('g')
                .attr('transform', `translate(0, ${titleHeight})`)
                .selectAll('rect')
                .data<string>(clusterLabels)
                .join('rect')
                .attr('width', rectSize).attr('height', rectSize)
                .attr('x', 5).attr('y', (d: string, idx: number) => idx * rectSize * 1.5)
                .style('fill', (d: string) => colorScale(d) as string)

            const labels = legendContainer.append('g')
                .attr('transform', `translate(0, ${titleHeight})`)
                .selectAll('text')
                .data<string>(clusterLabels)
                .join('text')
                .text((d: string) => d)
                .style('font-size', '.7rem')
                .style('text-anchor', 'start')
                .attr('x', rectSize)
                .attr('y', (d: string, idx: number) => idx * rectSize * 1.5)
                .attr('dx', '0.7rem')
                .attr('dy', '0.7rem')
            */

            const title = legendContainer
                .append('text')
                .style('font-size', '.7rem')
                .style('text-anchor', 'start')
                .style('font-weight', 'bold')
                .text('Cultivars')
                .attr('x', 5)
                .attr('dy', '0.7rem')
        }
    },
    watch: { // updated because a legend is added.
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                d3.select('#scatter-svg').selectAll('*').remove()
                d3.select('#scatter-legend-svg').selectAll('*').remove()
                this.initChart()
                this.initLegend()
            }
        }
    },
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100))
        this.onResize()
    },
    beforeDestroy() {
       window.removeEventListener('resize', this.onResize)
    }
}
</script>

<!-- We use flex to arrange the layout-->
<template>
    <div class="viz-container d-flex justify-end">
        <div class="chart-container d-flex" ref="scatterContainer">
            <svg id="scatter-svg" width="100%" height="100%">
            </svg>
        </div>
        <div id="scatter-legend-container" class="d-flex">
            <svg id="scatter-legend-svg" width="100%" height="100%">
            </svg>
        </div>
    </div>
</template>

<!-- How we arrange the two svgs with css-->
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
#scatter-legend-container{
    width: 5rem;
}
</style>