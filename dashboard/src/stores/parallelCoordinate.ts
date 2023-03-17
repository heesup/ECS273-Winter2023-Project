import { defineStore } from 'pinia'
import axios from "axios"
import { isEmpty } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin } from '../types';
interface ScatterPoint extends Point{
    cluster: string;
}

export const useParallelStore = defineStore('Parallel', {
    state: () => ({
        clusters: [] as string[],
        HDDFailure_data: [] as HDDFailure[],
        columns: [] as string[],
        size: { width: 0, height: 0 } as ComponentSize,
        margin: {left: 20, right: 20, top: 60, bottom: 60} as Margin,
        manufacturers: ['All', 'Seagate', 'TOSHIBA', 'HGST', 'WDC', 'Micron', 'HP', 'Hitachi', 'DELLBOSS'] as string[],
        //selectedMFG: 'Seagate', // default value
        selectedMFG: 'All', // default value
    }),
    getters: {
        resize: (state) => {
            return (!isEmpty(state.HDDFailure_data)) && state.size
        }
    },
    actions: {
        async fetchParallel(manufacturer: string) { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
            axios.post(`${server}/fetchParallelData`, {manufacturer: manufacturer})
                .then(resp => {
                    this.HDDFailure_data = resp.data.data; 
                    this.clusters = resp.data.clusters;
                    this.columns = resp.data.columns;

                    return true;
                })
                .catch(error => console.log(error));
            //console.log(manufacturer)
        },
    }
})