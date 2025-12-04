import { defineStore } from 'pinia';

export const useNodeStore = defineStore('nodeStore', {
  state: () => ({
    nodeNames: [],
    gridData: [],
  }),
  actions: {
    setNodeNames(data) {
      this.nodeNames = data;
    },
    setGridData(data) {
      this.gridData = data;
    },
  },
});