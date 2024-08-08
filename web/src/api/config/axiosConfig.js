import axios from "axios"


export const api = axios.create({
    baseURL: "http://localhost:8000/v1",
})

const errorHandler = (error) => {
    const statusCode = error.response?.status

    if (statusCode && statusCode !== 401) {
        console.error(error)
    }

    return Promise.reject(error)
}

api.interceptors.response.use(undefined, (error) => {
    return errorHandler(error)
})