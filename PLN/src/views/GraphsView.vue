<template>
    <!-- Title -->
    <div class="row">
        <div class="col-12 grid-margin">
            <div class="card">
                <div class="card-body">
                    <!-- Title -->
                    <div class="row justify-content-start px-3">
                        <TitleSection title="Gráficos" />
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Graphs and user comparison -->
    <div class="row">
        <!-- Searches -->
        <div class="col-lg-6 grid-margin stretch-card">
            <div class="card">
                <div class="card-body">
                    <h4 class="card-title">Nº de Pesquisas Por Mês</h4>
                    <canvas id="lineChart" style="height:250px"></canvas>
                </div>
            </div>
        </div>

        <!-- Users -->
        <div class="col-lg-6 grid-margin">
            <div class="card">
                <div class="card-body">
                    <h4 class="card-title">Utilizadores no Mês Atual</h4>
                    <div class="d-flex">
                        <h2 class="pr-4 m-0">{{ currentMonthCount }}</h2>
                        <span class="d-flex align-items-center"
                            :class="{ 'text-success': currentMonthCount > previousMonthCount, 'text-danger': currentMonthCount < previousMonthCount }">
                            <i
                                :class="{ 'mdi mdi-arrow-up-bold': currentMonthCount > previousMonthCount, 'mdi mdi-arrow-down-bold': currentMonthCount < previousMonthCount }"></i>
                            <span>{{ differenceMessage }}</span>
                        </span>
                    </div>
                </div>
            </div>

            <div class="card mt-2">
                <div class="card-body">
                    <h4 class="card-title">Histórico de Likes/Dislikes</h4>
                    <div class="ag-theme-quartz" style="width: 100%; height: 100%;">
                        <ag-grid-vue :rowData="postsLikesDislikesHistory" :columnDefs="postsLikesDislikesColumnDefs"
                            :pagination="true" :paginationPageSize="20" class="ag-theme-quartz" style="height: 500px">
                        </ag-grid-vue>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>

//#region Imports
import { ref, onMounted } from 'vue'
import { AgGridVue } from "ag-grid-vue3"
import { useToast } from "vue-toastification"

import axios from 'axios'
import TitleSection from '@/components/TitleSection.vue'

import "ag-grid-community/styles/ag-grid.css"
import "ag-grid-community/styles/ag-theme-quartz.css"

import '@/assets/js/chart.js'
//#endregion

//#region Variables
const toast = useToast()

const currentMonthCount = ref(0)
const previousMonthCount = ref(0)

const differenceMessage = ref('')

const postsLikesDislikesHistory = ref([])
//#endregion

//#region Methods
function fetchSearchesPerDay() {
    axios.get('/searches-per-month').then(response => {
        const ctx = document.getElementById('lineChart').getContext('2d')
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: response.data.labels,
                datasets: [{
                    label: 'Pesquisas por dia',
                    data: response.data.data,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        display: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        })
    })
}

function fetchUsersCountForComparison() {
    axios.get('/users-count-for-comparison').then(response => {
        currentMonthCount.value = response.data.currentMonthCount
        previousMonthCount.value = response.data.previousMonthCount
        differenceMessage.value = currentMonthCount.value > previousMonthCount.value
            ? 'Mais que no mês passado' : 'Menos que no mês passado'
    }).catch(error => {
        // console.error('There was an error fetching the user count data:', error)
        toast.error('Ocorreu um erro ao obter os dados de utilizadores.')
    })
}

// Renderer for the permalink button
const buttonRenderer = (params) => {
    return `<a href="https://www.reddit.com${params.value}" target="_blank"><i class="mdi mdi-open-in-new"></i></a>`;
}

// Column definitions for the posts likes/dislikes history
const postsLikesDislikesColumnDefs = ref([
    {
        headerName: 'ID',
        field: 'id',
        sortable: true,
        filter: false,
        width: 80,
        resizable: false
    },
    {
        headerName: 'Post ID',
        field: 'post_id',
        sortable: true,
        filter: true,
        flex: 1,
        resizable: false
    },
    {
        headerName: 'Likes',
        field: 'count_likes',
        sortable: true,
        filter: true,
        width: 100,
        flex: 1,
        resizable: false,
        // pinned: 'right',
        cellClass: 'text-success font-weight-bold',
    },
    {
        headerName: 'Dislikes',
        field: 'count_dislikes',
        sortable: true,
        filter: true,
        width: 100,
        flex: 1,
        resizable: false,
        // pinned: 'right',
        cellClass: 'text-danger font-weight-bold',
    },
    {
        headerName: '',
        field: 'permalink',
        sortable: false,
        width: 50,
        resizable: false,
        pinned: 'right',
        cellRenderer: buttonRenderer,
    },
])

// Fetch posts likes/dislikes history data
const fetchPostsLikesDislikesHistory = async () => {
    try {
        const response = await axios.get('/posts-likes-dislikes-history')
        postsLikesDislikesHistory.value = response.data
    } catch (error) {
        toast.error('Ocorreu um erro ao obter o histórico de likes/dislikes.')
    }
}
//#endregion

//#region Lifecycle Hooks
onMounted(() => {
    fetchSearchesPerDay()
    fetchUsersCountForComparison()
    fetchPostsLikesDislikesHistory()
})
//#endregion

</script>
