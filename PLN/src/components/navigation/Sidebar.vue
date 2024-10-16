<template>
    <nav class="sidebar sidebar-offcanvas" id="sidebar">
        <!-- Logo -->
        <RouterLink to="/">
            <div class="sidebar-brand-wrapper d-none d-md-flex align-items-center justify-content-center fixed-top">
                <a class="sidebar-brand brand-logo">PLN</a>
                <a class="sidebar-brand brand-logo-mini" href="index.html">PLN</a>
            </div>
        </RouterLink>

        <!-- Sidebar content -->
        <ul class="nav">
            <!-- Profile -->
            <li class="nav-item profile border-bottom pb-3">
                <div class="profile-desc">
                    <div class="profile-pic">
                        <div class="profile-name ml-0">
                            <h5 class="mb-0 font-weight-normal text-capitalize">{{ finalName }}</h5>
                        </div>
                    </div>
                </div>
            </li>

            <!-- Divider -->
            <li class="nav-item nav-category">
                <span class="nav-link">Navegação</span>
            </li>

            <!-- Siderbar items -->
            <div class="mt-3">
                <SidebarItem />
            </div>
        </ul>
    </nav>
</template>

<script setup>

//#region Imports
import { computed } from 'vue'
import { store } from '@/stores/login'
import { useOthersStore } from '@/stores/others'

import SidebarItem from '@/components/navigation/SidebarItem.vue'

import '@/assets/css/sidebar.css'
//#endregion

//#region Variables
const othersStore = useOthersStore()

const finalName = computed(() => othersStore.getFirstAndLastName(store.name))
//#endregion

</script>