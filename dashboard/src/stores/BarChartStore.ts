import { defineStore } from 'pinia'
import axios from "axios"
import { isEmpty } from 'lodash';
import { server } from '../helper';

import { Point, BarPoint, ComponentSize, Margin } from '../types';
interface ScatterPoint extends Point{
    cluster: string;
}

export const useBarChartStore = defineStore('useBarChartStore', {
    state: () => ({
        points: [] as BarPoint[],
        clusters: [] as string[],
        size: { width: 0, height: 0 } as ComponentSize,
        margin: { left: 40, right: 20, top: 20, bottom: 40 } as Margin,
        methods: ['count', 'failure',"power_on_years"] as string[],
        selectedMethod: 'count', // default value
    }),
    getters: {
        resize: (state) => {
            return (!isEmpty(state.points) && state.size)
        }
    },
    actions: {
        async fetchExample(method: string) { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
            axios.post(`${server}/fetchBarPlotData`, {method: method})
                .then(resp => {
                    //console.log(resp.data)
                    this.points = resp.data.data; // value, cluster
                    //console.log(this.points)
                    this.clusters = resp.data.clusters; //for legend
                    //console.log(resp.data.clusters)
                    return true;
                })
                .catch(error => console.log(error));
        },
    }
})