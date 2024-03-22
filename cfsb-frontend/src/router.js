import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import HierarchicalCategoryList from '@/components/HierarchicalCategoryList.vue';
import DataGrid from '@/components/DataGrid.vue';

const routes = [
    {
        path: '/',
        component: HierarchicalCategoryList,
    },
    {
        path: '/datagrid',
        name: 'DataGrid',
        component: DataGrid,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
