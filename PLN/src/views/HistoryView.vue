<template>
    <div class="row">
        <div class="col-12 grid-margin">
            <div class="card">
                <div class="card-body">
                    <!-- Title -->
                    <div class="row justify-content-between px-3">
                        <TitleSection title="Histórico de Pesquisas" />
                    </div>

                    <!-- Table -->
                    <div class="row mt-5 px-3">
                        <div class="ag-theme-quartz" style="width: 100%; height: 100%;">
                            <ag-grid-vue :rowData="historyData" :columnDefs="columnDefs" :pagination="true"
                                :paginationPageSize="20" class="ag-theme-quartz" style="height: 500px">
                            </ag-grid-vue>
                        </div>
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

import axios from 'axios'

import "ag-grid-community/styles/ag-grid.css"
import "ag-grid-community/styles/ag-theme-quartz.css"

import TitleSection from '@/components/TitleSection.vue'
//#endregion

//#region Variables
const historyData = ref([])

const userId = localStorage.getItem('user_id')
//#endregion

//#region Methods
const columnDefs = ref([
    {
        headerName: 'ID',
        field: 'id',
        sortable: true,
        filter: false,
        width: 80,
        resizable: false
    },
    {
        headerName: 'Consulta',
        field: 'query',
        sortable: true,
        filter: true,
        flex: 1,
    },
    {
        headerName: 'Tipo de Pesquisa',
        field: 'tipo_pesquisa',
        sortable: true,
        filter: true,
        cellClass: (params) => {
            switch (params.value) {
                case 'normal':
                    return 'text-primary text-capitalize font-weight-bold'
                case 'gpt':
                    return 'text-danger text-capitalize font-weight-bold'
                case 'topic':
                    return 'text-warning text-capitalize font-weight-bold'
                case 'elastic':
                    return 'text-info text-capitalize font-weight-bold'
                default:
                    return {}
            }
        }
    },
    {
        headerName: 'Data',
        field: 'created_at',
        sortable: true,
        filter: true,
        resizable: false,
        valueFormatter: (params) => {
            const date = new Date(params.value)
            const day = String(date.getDate()).padStart(2, '0')
            const month = String(date.getMonth() + 1).padStart(2, '0') // Months are zero-indexed
            const year = date.getFullYear()
            const hours = String(date.getHours()).padStart(2, '0')
            const minutes = String(date.getMinutes()).padStart(2, '0')

            return `${day}-${month}-${year} ${hours}:${minutes}`
        }
    },
])

const fetchHistory = async () => {
    try {
        const response = await axios.get(`/users/history/${userId}`)
        historyData.value = response.data
    } catch (error) {
        // console.error('Failed to fetch history:', error)
        toast.error('Ocorreu um erro ao obter o histórico de pesquisas.')
    }
}
//#endregion

//#region Lifecycle Hooks
onMounted(() => {
    fetchHistory()
})
//#endregion

</script>
