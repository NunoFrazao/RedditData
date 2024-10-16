<template>
    <nav class="navbar p-0 fixed-top d-flex flex-row" :class="{ 'navbar-no-account': !isLoggedIn }">
        <div class="navbar-menu-wrapper flex-grow d-flex align-items-stretch justify-content-between">
            <!-- Left side -->
            <button id="button-open-sidebar" class="navbar-toggler navbar-toggler align-self-center" type="button"
                data-toggle="minimize" v-if="isLoggedIn">
                <span class="mdi mdi-menu"></span>
            </button>

            <!-- Main title -->
            <div class="d-lg-flex align-items-center d-none">
                <span id="nav-main-title"
                    :class="showNavigation == true ? 'nav-main-title-extra' : 'nav-main-title'">Análise de
                    Sentimentos</span>
            </div>

            <!-- Right side -->
            <ul class="navbar-nav navbar-nav-right">
                <li class="nav-item dropdown position-relative" v-if="isLoggedIn">
                    <a id="button-profile" class="nav-link" href="#">
                        <div class="navbar-profile">
                            <span class="profile-images">{{ firstLetterfinalName }}</span>
                            <p class="mb-0 d-sm-block navbar-profile-name text-capitalize">{{ finalName }}</p>
                            <i class="mdi mdi-menu-down d-none d-sm-block"></i>
                        </div>
                    </a>

                    <div id="dropdown-profile">
                        <RouterLink to="/profile" class="routerlink-anc dropdown-links">
                            <a class="dropdown-item preview-item d-flex align-items-center py-3">
                                <div class="preview-thumbnail">
                                    <div class="preview-icon rounded-circle">
                                        <i class="mdi mdi-settings text-success"></i>
                                    </div>
                                </div>
                                <div class="preview-item-content pl-3">
                                    <p class="preview-subject m-0">Perfil</p>
                                </div>
                            </a>
                        </RouterLink>
                        <div class="dropdown-divider"></div>

                        <RouterLink to="/login" class="routerlink-anc dropdown-links" @click="handleLogout()">
                            <a class="dropdown-item preview-item d-flex align-items-center py-3">
                                <div class="preview-thumbnail">
                                    <div class="preview-icon rounded-circle">
                                        <i class="mdi mdi-logout text-danger"></i>
                                    </div>
                                </div>
                                <div class="preview-item-content pl-3">
                                    <p class="preview-subject m-0">Logout</p>
                                </div>
                            </a>
                        </RouterLink>
                    </div>
                </li>
                <li class="nav-item" v-if="!isLoggedIn && showLoginButton">
                    <RouterLink to="/login" class="routerlink-anc">
                        <a class="nav-link text-light btn btn-outline-warning px-4">Log in</a>
                    </RouterLink>
                </li>
            </ul>

            <!-- Mobile menu -->
            <button v-if="isLoggedIn == true" class="navbar-toggler navbar-toggler-right d-lg-none align-self-center" type="button"
                data-toggle="offcanvas">
                <span class="mdi mdi-format-line-spacing"></span>
            </button>
        </div>
    </nav>
</template>

<script setup>

//#region Imports
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '@/stores/login'
import { useOthersStore } from '@/stores/others'

import '@/assets/js/sidebar.js'
import '@/assets/js/perfil-dropdown.js'
import '@/assets/css/navbar.css'
//#endregion

//#region Variables
const route = useRoute()
const othersStore = useOthersStore()

const finalName = computed(() => othersStore.getFirstAndLastName(store.name))
const firstLetterfinalName = computed(() => othersStore.getFirstAndLastName(store.name)[0].toUpperCase())
const isLoggedIn = computed(() => store.isLoggedIn)
const showLoginButton = computed(() => !isLoggedIn.value && route.name !== 'login')
//#endregion

//#region Methods
const showNavigation = computed(() => route.meta.requiresAuth !== false || isLoggedIn.value == false)

const handleLogout = async () => { store.logout() }
//#endregion

</script>
