import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UsersView from '@/views/UsersView.vue'

// Determine if the user is an admin
const isAdmin = parseInt(localStorage.getItem('tipo'), 10) === 1

const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView,
        meta: { isAdmin: isAdmin }
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('../views/Auth/LoginView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/register',
        name: 'registar conta',
        component: () => import('../views/Auth/RegisterView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/users',
        name: 'users',
        component: UsersView,
        meta: { requiresAuth: true }
    },
    {
        path: '/users/:id/:type',
        name: 'Detalhe do Utilizador',
        component: () => import('@/views/UserDetail.vue'),
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/history',
        name: 'histórico',
        component: () => import('../views/HistoryView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/profile',
        name: 'perfil',
        component: () => import('../views/ProfileView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/graphs',
        name: 'gráficos',
        component: () => import('../views/GraphsView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: () => import('../views/NotFoundView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/server-error',
        name: 'server error',
        component: () => import('../views/ServerErrorView.vue'),
        meta: { requiresAuth: false }
    }
]

// Create a new router instance
const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
        return savedPosition || { top: 0 }
    },
})

// Capitalize the first letter of each word in a string
function capitalizeFirstLetter(string) {
    return string.replace(/(?:^|\s|-)\S/g, match => match.toUpperCase())
}

router.beforeEach((to, from, next) => {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'

    to.meta.requiresAuth && !isLoggedIn ? next({ name: 'login' }) : next()
})

// Set the page title based on the route name
router.afterEach((to) => {
    document.title = to.name ? `PLN - ${capitalizeFirstLetter(to.name)}` : "Dashboard"

    // Reinitialize profile dropdowns after each route change
    if (typeof window.initProfileDropdown === 'function') window.initProfileDropdown()

    // Reinitialize sidebar after each route change
    if (typeof window.initSidebarToggle === 'function') window.initSidebarToggle()
})

export default router
