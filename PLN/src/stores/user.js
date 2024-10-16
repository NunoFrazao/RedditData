import { ref, inject, onMounted } from "vue"
import { defineStore } from "pinia"
import { useToast } from "vue-toastification"
import { useOthersStore } from '@/stores/others'

export const useUserStore = defineStore("user", () => {
    const socket = inject("socket")
    const toast = useToast()
    const users = ref([])
    const countRequests = ref(0)
    const timeLastRequest = ref(0)
    const othersStore = useOthersStore()

    // Count requests and update time of last request
    const countUp = (requests) => {
        if (timeLastRequest.value === 0 || ((Date.now() - timeLastRequest.value) / 1000 > 60)) {
            timeLastRequest.value = Date.now()
            countRequests.value = requests
        } else {
            countRequests.value += requests
        }
    }

    // Verify if requests can be made
    const verifyRequests = () => {
        const canMakeRequest = (Date.now() - timeLastRequest.value) / 1000 > 60 || countRequests.value <= 95
        return canMakeRequest
    }

    onMounted(() => {
        socket.on('newUser', (user) => {
            console.log('Client received newUser:', user)
            users.value.push(user)
            toast.success(`Utilizador ${othersStore.getFirstAndLastName(user.name)} foi criado`)
        })

        socket.on('userChange', (user) => {
            console.log('Client received userChange:', user)
            users.value.push(user)
            toast.success(`Utilizador ${othersStore.getFirstAndLastName(user.name)} foi editado`)
        })
    })

    return {
        users,
        countUp,
        verifyRequests,
        countRequests,
        timeLastRequest
    }
})
