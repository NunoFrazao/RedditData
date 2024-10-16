import { reactive, watchEffect, inject } from 'vue'

export const store = reactive({
    isLoggedIn: localStorage.getItem('isLoggedIn') === 'true',
    name: localStorage.getItem('name'),
    tipo_user: parseInt(localStorage.getItem('tipo'), 10),

    // Login user and store user data in local storage
    login(userData, socket) {
        this.isLoggedIn = true
        this.name = userData.name
        this.tipo_user = userData.tipo_user

        localStorage.setItem('user_id', userData.id)
        localStorage.setItem('name', userData.name)
        localStorage.setItem('tipo', userData.tipo_user)
        localStorage.setItem('email', userData.email)
        localStorage.setItem('isLoggedIn', 'true')

        socket.emit('loggedIn', userData)
    },

    // Logout user and clear local storage
    logout() {
        this.isLoggedIn = false
        this.name = null
        this.tipo_user = null

        localStorage.removeItem('user_id')
        localStorage.removeItem('name')
        localStorage.removeItem('tipo')
        localStorage.removeItem('email')
        localStorage.setItem('isLoggedIn', 'false')
    }
})

// Ensure that changes to store.tipo_user are reactive
watchEffect(() => {
    store.tipo_user = parseInt(localStorage.getItem('tipo'), 10)
})
