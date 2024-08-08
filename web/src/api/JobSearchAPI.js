import { api } from "./config/axiosConfig"
import { defineCancelApiObject } from "./config/axiosUtil"


export const JobSearchAPI = {
    search: async function (query, cancel = false) {
        const response = await api.request({
            url: `/job/${query}`,
            method: "GET",
            signal: cancel ? cancelApiObject[this.get.name].handleRequestCancellation().signal : undefined,
        })

        return response.data
    },
}

const cancelApiObject = defineCancelApiObject(JobSearchAPI)