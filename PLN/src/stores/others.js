import { ref, inject, onMounted } from "vue"
import { defineStore } from "pinia"

export const useOthersStore = defineStore("others", () => {

    // Get first and last name from full name
    const getFirstAndLastName = (fullName) => {
        const nameParts = fullName.trim().split(" ")
        if (nameParts.length > 2) {
            return `${nameParts[0]} ${nameParts[nameParts.length - 1]}`
        }
        return fullName
    }

    return {
        getFirstAndLastName
    }
})
