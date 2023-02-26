<script lang="ts">
import * as d3 from "d3";
import { debounce, isEmpty } from 'lodash';
import { Point } from '../types';
interface ScatterPoint extends Point{
    cluster: string;
}

/* The new major things from ExampleWithLegend.vue
1) Add a dropdown menu to switch between different DR techniques, the changes are mostly in the template
2) Using a store from './dashboard/stores/exampleStore'
3) Composition API rather than Option API (just used a little bit)
*/

// For importing a store. See how it's set up in ./dashboard/stores/ and ./dashboard/main.ts
import { mapState, storeToRefs } from 'pinia'; 
import { useExampleStore } from '../stores/exampleStore';

export default {
    setup() { // Composition API syntax
        const store = useExampleStore()
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
        }
    },
    computed: {
        ...mapState(useExampleStore, ['selectedMethod']) // Traditional way to map the store state to the local state
    },
    created() {
        this.store.fetchExample(this.selectedMethod);
    },
    methods: {
        onResize() {
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined || target === null) return;
            this.store.size = { width: target.clientWidth, height: target.clientHeight }; // How you update the store
        },
        initChart() {
            let chartContainer = d3.select('#scatter-svg')

            let xExtents = d3.extent(this.store.points.map((d: ScatterPoint) => d.posX as number)) as [number, number]
            let yExtents = d3.extent(this.store.points.map((d: ScatterPoint) => d.posY as number)) as [number, number]

            let xScale = d3.scaleLinear()
                .range([this.store.margin.left, this.store.size.width - this.store.margin.right])
                .domain(xExtents)

            let yScale = d3.scaleLinear()
                .range([this.store.size.height - this.store.margin.bottom, this.store.margin.top])
                .domain(yExtents)

            let clusters: string[] = this.store.clusters.map((cluster: string, idx: number) => String(idx))
            let colorScale = d3.scaleOrdinal().domain(clusters).range(d3.schemeTableau10) // d3.schemeTableau10: string[]

            const points = chartContainer.append('g')
                .selectAll('circle')
                .data<ScatterPoint>(this.store.points)
                .join('circle')
                .attr('cx', (d: ScatterPoint) => xScale(d.posX))
                .attr('cy', (d: ScatterPoint) => yScale(d.posY))
                .attr('r', 5)
                .style('fill', (d: ScatterPoint) => colorScale(String(d.cluster)) as string)
                .style('opacity', .7)

            const title = chartContainer.append('g')
                .append('text')
                .attr('transform', `translate(${this.store.size.width / 2}, ${this.store.size.height - this.store.margin.top})`)
                .attr('dy', '0.5rem')
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .text(`Wine Dataset ${this.selectedMethod} Projection`)
        },
        initLegend() {
            let legendContainer = d3.select('#scatter-legend-svg')

            let clusterLabels: string[] = this.store.clusters.map((cluster: string, idx: number) => `Cultivar ${idx+1}`)
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
                .text('Cultivars')
                .attr('x', 5)
                .attr('dy', '0.7rem')
        },
        rerender() {
            d3.select('#scatter-svg').selectAll('*').remove() // Clean all the elements in the chart
            d3.select('#scatter-legend-svg').selectAll('*').remove()
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
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100))
        this.onResize()
    },
    beforeDestroy() {
       window.removeEventListener('resize', this.onResize)
    }
}
</script>

<!-- We only use vanilla widgets here, you can use the equivalent components from the UI library -->
<!-- Helpful References: https://vuejs.org/guide/essentials/class-and-style.html#binding-html-classes -->
<template>
    <div class="viz-container d-flex justify-end">
        <div class="chart-container d-flex" ref="scatterContainer">
            <svg id="scatter-svg" width="100%" height="100%">
            </svg>
        </div>
        <div id="scatter-control-container" class="d-flex">
            <div class="d-flex mb-4">
                <label :style="{ fontSize: '0.7rem'}"> Select DR method:
                    <select class="method-select" v-model="store.selectedMethod">
                        <option v-for="method in store.methods" :value="method" 
                            :selected="(method === store.selectedMethod)? true : false">{{method}}</option>
                    </select>
                </label>
            </div>
            <svg id="scatter-legend-svg" width="100%" height="80%">
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
    height: 100%;
    width: calc(100% - 6rem);
}
#scatter-control-container{
    width: 6rem;
    flex-direction: column;
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