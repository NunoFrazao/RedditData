<template>
    <!-- Static item for home -->
    <li class="nav-item menu-items">
        <RouterLink to="/" class="routerlink-anc">
            <a class="nav-link">
                <span class="menu-icon">
                    <i class="mdi mdi-speedometer"></i>
                </span>
                <span class="menu-title">Dashboard</span>
            </a>
        </RouterLink>
    </li>

    <!-- Admin items -->
    <li v-if="isAdmin" v-for="item in adminItems" :key="item.path" class="nav-item menu-items">
        <RouterLink :to="item.path" class="routerlink-anc">
            <a class="nav-link">
                <span class="menu-icon">
                    <i :class="item.icon"></i>
                </span>
                <span class="menu-title">{{ item.title }}</span>
            </a>
        </RouterLink>
    </li>

    <!-- Static item for settings -->
    <li class="nav-item menu-items">
        <RouterLink to="/profile" class="routerlink-anc">
            <a class="nav-link">
                <span class="menu-icon">
                    <i class="mdi mdi-settings"></i>
                </span>
                <span class="menu-title">Definições</span>
            </a>
        </RouterLink>
    </li>
</template>

<script setup>

//#region Imports
import { ref } from 'vue'
//#endregion

//#region Variables
const isAdmin = ref(localStorage.getItem('tipo') == 1)

const adminItems = [
    {
        path: "/users",
        icon: "mdi mdi-account",
        title: "Utilizadores"
    },
    {
        path: "/history",
        icon: "mdi mdi-table-large",
        title: "Histórico"
    },
    {
        path: "/graphs",
        icon: "mdi mdi-chart-bar",
        title: "Gráficos"
    }
]
//#endregion
</script>
