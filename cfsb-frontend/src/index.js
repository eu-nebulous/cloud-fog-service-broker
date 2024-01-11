import { createRouter, createWebHistory } from 'vue-router';
import DataGrid from '@/components/DataGrid.vue';
import CriteriaSelection from '@/components/CriteriaSelection.vue'; // Import the new component
//import SummedData from '@/components/SummedData.vue';
import Evaluation from '@/components/Evaluation.vue'; // Import the Evaluation component
import WR from '@/components/WR.vue';
import Results from '@/components/Results.vue'; // Import the Results component
import HomePage from "@/components/HomePage.vue";

const routes = [
    {
        path: '/',
        name: 'HomePage',
        component: HomePage
    },
    {
        path: '/criteria-selection',
        name: 'CriteriaSelection',
        component: CriteriaSelection
    },
    {
        path: '/data-grid',
        name: 'DataGrid',
        component: DataGrid
    },
    { path: '/data-grid', component: DataGrid },
   // { path: '/wr', name: 'WR', component: () => import('@/components/WR.vue') },
    { path: '/wr', name: 'WR', component: WR},
    {
        path: '/evaluation',
        name: 'Evaluation',
        component: Evaluation
    },
    {
        path: '/results',
        name: 'Results',
        component: Results // Route for the Results component
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});


export default router;

console.log('Router setup:', routes);